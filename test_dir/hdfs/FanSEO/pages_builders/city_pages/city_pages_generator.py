import boto3
import json
from datetime import datetime
from operator import itemgetter
import concurrent.futures
import time 

from pyspark import SparkFiles
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
import pysolr


REGION_NAME = "us-east-1"
S3_BUCKET = "concerts.hypebot.com"
S3_OBJECT_PATH = "latest/cities"
POPULAR_CITIES_PATH = (
    "s3a://bit-emr-cluster/dev/rene/city_pages/popular_cities_with_nearby_cities"
)
FOOTER_ARTISTS_PATH = "s3a://bit-emr-cluster/dev/rene/qualified_footer_artists"

SOLR_COLLECTION_NAME = "fan_seo_upcoming_events_alias"
SOLR_ZOOKEEPER_URL = "solr-zookeeper01.prod.bandsintown.com:2181,solr-zookeeper02.prod.bandsintown.com:2181,solr-zookeeper03.prod.bandsintown.com:2181,solr-zookeeper04.prod.bandsintown.com:2181,solr-zookeeper05.prod.bandsintown.com:2181/solr-users"

GENRES = {
    "popular": {"query": "*", "aliases": []},
    "alternative": {"query": "alternative", "aliases": []},
    "blues": {"query": "blues", "aliases": []},
    "christian": {"query": "christian", "aliases": ["christian-gospel"]},
    "gospel": {"query": "gospel", "aliases": ["christian-gospel"]},
    "classical": {"query": "classical", "aliases": []},
    "country": {"query": "country", "aliases": []},
    "electronic": {"query": "electronic", "aliases": []},
    "folk": {"query": "folk", "aliases": []},
    "hip hop": {"query": '"hip hop"', "aliases": ["hip-hop"]},
    "jazz": {"query": "jazz", "aliases": []},
    "metal": {"query": "metal", "aliases": []},
    "pop": {"query": "pop", "aliases": []},
    "punk": {"query": "punk", "aliases": []},
    "r&b": {"query": "r\\&b", "aliases": ["rnb-soul"]},
    "soul": {"query": "soul", "aliases": ["rnb-soul"]},
    "reggae": {"query": "reggae", "aliases": []},
    "rock": {"query": "rock", "aliases": []},
}

GROUP_QUERIES = list(
    map(lambda kv: f"artistGenres:{kv[1].get('query')}", GENRES.items())
)

SOLR_QUERY_GENRES = {
    "d": "50",
    "fq": "{!geofilt}",
    "sort": "geodist() asc",
    "sfield": "latlong",
    "group": "true",
    "group.limit": "100",
    "group.query": GROUP_QUERIES,
    "group.sort": "geodist() asc, rsvpCount desc, artistTrackerCount desc",
    "start": 0,
    "rows": 100,
}


def process_partition(iterator, jinja_env, context_builder, footer_artists):
    """Process all rows in a partition with shared connections"""
    
    partition_start = time.time()
    
    # Initialize connections ONCE per partition
    session = boto3.Session(region_name=REGION_NAME)
    s3_client = session.resource("s3")
    s3_init_time = time.time()

    zookeeper = pysolr.ZooKeeper(SOLR_ZOOKEEPER_URL)
    zk_connect_time = time.time()
    
    collections = {}

    for c in zookeeper.zk.get_children("collections"):
        collections.update(
            json.loads(
                zookeeper.zk.get("collections/{}/state.json".format(c))[0].decode(
                    "ascii"
                )
            )
        )

    zk_collections_time = time.time()
    
    zookeeper.collections = collections
    solr_cloud_conn = pysolr.SolrCloud(
        zookeeper, SOLR_COLLECTION_NAME, timeout=10
    )
    solr_init_time = time.time()

    # Cache templates
    popular_template = jinja_env.get_template("city/popular_events.html")
    genre_template = jinja_env.get_template("city/genre_events.html")
    template_time = time.time()

    print(f"[PARTITION INIT] s3={s3_init_time-partition_start:.2f}s, zk_connect={zk_connect_time-s3_init_time:.2f}s, zk_collections={zk_collections_time-zk_connect_time:.2f}s, solr={solr_init_time-zk_collections_time:.2f}s, templates={template_time-solr_init_time:.2f}s, total={template_time-partition_start:.2f}s")

    def upload_to_s3(path, body):
        s3_client.Object(S3_BUCKET, path).put(Body=body, ContentType="text/html")

    def get_all_events_from_solr(latlong: str):
        query = SOLR_QUERY_GENRES.copy()  # Important: copy to avoid mutation
        query["pt"] = f"{latlong}"
        response = solr_cloud_conn.search("*:*", **query)
        return response.grouped

    def group_events_by_genre(events):
        events_by_genre = {}

        for group_query_name, results in events.items():
            query = group_query_name.split(":")[1]
            if query == "*":
                genre_name = "popular"
            else:
                genre_name = query.replace("\\", "").replace('"', "")

            genre = GENRES.get(genre_name)
            group_results = []
            
            if (results.get("matches") > 0 and 
                results.get("doclist", {}).get("numFound") > 0):
                group_results = results.get("doclist", {}).get("docs") or []

            if genre and genre.get("aliases"):
                for alias in genre.get("aliases"):
                    events_by_genre[alias] = group_results
            else:
                events_by_genre[genre_name] = group_results

        return events_by_genre

    # Process each row in the partition
    row_count = 0
    partition_errors = []
    
    for row in iterator:
        row_count += 1
        start_total = time.time()

        all_events = get_all_events_from_solr(row.latlong)
        solr_time = time.time()

        grouped_events = group_events_by_genre(all_events)
        group_time = time.time()

        genre_pop = {"label": "Popular", "labelSlug": "popular"}

        context = context_builder.build_context(
            row,
            grouped_events.get("popular", []),
            genre_pop,
            footer_artists=footer_artists,
        )

        popular_rendered = popular_template.render(context)
        popular_path = f"{S3_OBJECT_PATH}/popular/{row.nameSlug}"
        render_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = {}
            futures[executor.submit(upload_to_s3, popular_path, popular_rendered)] = popular_path

            for genre in context_builder.GENRES[0:-1]:
                ctx = context_builder.build_context(
                    row,
                    grouped_events.get(genre.get("labelSlug"), []),
                    genre,
                    footer_artists=footer_artists,
                )

                rendered = genre_template.render(ctx)
                path = f"{S3_OBJECT_PATH}/{genre.get('labelSlug')}/{row.nameSlug}"
                futures[executor.submit(upload_to_s3, path, rendered)] = path

            for future in concurrent.futures.as_completed(futures):
                path = futures[future]
                try:
                    future.result()
                except Exception as e:
                    error_msg = f"S3 upload failed for {path}: {e}"
                    print(f"[ERROR] {error_msg}")
                    partition_errors.append(error_msg)

        end_time = time.time()
        print(f"[{row.nameSlug}] solr={solr_time-start_total:.2f}s, group={group_time-solr_time:.2f}s, render={render_time-group_time:.2f}s, s3_upload={end_time-render_time:.2f}s, total={end_time-start_total:.2f}s")

    print(f"[PARTITION COMPLETE] rows_processed={row_count}, errors={len(partition_errors)}")
    
    if partition_errors:
        raise Exception(f"Partition failed with {len(partition_errors)} S3 upload errors:\n" + "\n".join(partition_errors[:10]))


def main():
    conf = SparkConf()
    conf.setAppName("Fan SEO City Pages generation")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    sc.addPyFile("s3a://bit-emr-cluster/dev/rene/packages/jinja2.zip")
    sc.addPyFile("s3a://bit-emr-cluster/hdfs/FanSEO/html_templates/city_page.py")
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/pages_builders/city_pages/city_pages_context_builder.py"
    )
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/pages_builders/city_pages/pyspark_schemas.py"
    )

    import jinja2
    import city_page
    import city_pages_context_builder
    from pyspark_schemas import POPULAR_CITIES_SCHEMA

    jinja_env = jinja2.Environment(loader=jinja2.DictLoader(city_page.TEMPLATES))
    footer_artists_collection = spark.read.parquet(FOOTER_ARTISTS_PATH).collect()

    # Repartition for better parallelism
    cities_df = spark.read.parquet(POPULAR_CITIES_PATH).repartition(100)

    cities_df.rdd.foreachPartition(
        lambda iterator: process_partition(
            iterator, 
            jinja_env, 
            city_pages_context_builder, 
            footer_artists_collection
        )
    )

    spark.stop()


if __name__ == "__main__":
    main()