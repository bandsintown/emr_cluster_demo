from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, when, col, lit

import boto3
from datetime import datetime

FAN_SEO_DATA_S3_BUCKET_PATH = "s3a://bit-emr-cluster/dev/rene"
POPULAR_CITIES_PATH = (
    "s3a://bit-emr-cluster/dev/rene/city_pages/popular_cities_with_nearby_cities"
)
SITEMAP_DOMAIN_URL = "https://concerts.hypebot.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
REGION_NAME = "us-east-1"
SITEMAP_S3_BUCKET = "concerts.hypebot.com"

SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/siteindex.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for genre in genres %}
    <sitemap>
        <loc>https://concerts.hypebot.com/sitemaps/cities/{{genre}}_p1.xml</loc>
        <lastmod>{{lastmod}}</lastmod>
    </sitemap>
    <sitemap>
        <loc>https://concerts.hypebot.com/sitemaps/cities/{{genre}}_p2.xml</loc>
        <lastmod>{{lastmod}}</lastmod>
    </sitemap>
    {% endfor %}
</sitemapindex>
"""

GENRES = [
    "alternative",
    "blues",
    "christian-gospel",
    "classical",
    "country",
    "electronic",
    "folk",
    "hip-hop",
    "jazz",
    "metal",
    "pop",
    "punk",
    "rnb-soul",
    "reggae",
    "rock",
    "popular",
]


def main():
    conf = SparkConf()
    conf.setAppName("Fan SEO Sitemap data")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    sc.addPyFile("s3a://bit-emr-cluster/dev/rene/packages/jinja2.zip")
    boto_session = boto3.Session(region_name=REGION_NAME)
    boto_s3_client = boto_session.resource("s3")

    import jinja2

    jinja_template = jinja2.Environment(loader=jinja2.BaseLoader).from_string(
        SITEMAP_TEMPLATE
    )

    for genre in GENRES:
        sitemap_genre_p1 = (
            spark.read.parquet(POPULAR_CITIES_PATH)
            .select(
                concat(
                    lit(f"{SITEMAP_DOMAIN_URL}/cities/{genre}"),
                    lit("/"),
                    col("nameSlug"),
                ).alias("loc"),
                lit(TODAY).alias("lastmod"),
            )
            .limit(50_000)
        )

        sitemap_genre_p2 = (
            spark.read.parquet(POPULAR_CITIES_PATH)
            .select(
                concat(
                    lit(f"{SITEMAP_DOMAIN_URL}/cities/{genre}"),
                    lit("/"),
                    col("nameSlug"),
                ).alias("loc"),
                lit(TODAY).alias("lastmod"),
            )
            .exceptAll(sitemap_genre_p1)
        )

        sitemap_genre_p1_xml = sitemap_genre_p1.toPandas().to_xml(
            root_name="urlset",
            row_name="url",
            index=False,
            pretty_print=False,
            namespaces={
                "": "http://www.sitemaps.org/schemas/sitemap/0.9",
            },
        )

        sitemap_genre_p2_xml = sitemap_genre_p2.toPandas().to_xml(
            root_name="urlset",
            row_name="url",
            index=False,
            pretty_print=False,
            namespaces={
                "": "http://www.sitemaps.org/schemas/sitemap/0.9",
            },
        )

        # Page 1
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET,
            f"latest/sitemaps/cities/{genre}_p1_{TODAY}.xml",
        ).put(Body=sitemap_genre_p1_xml, ContentType="text/xml")
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET, f"latest/sitemaps/cities/{genre}_p1.xml"
        ).put(Body=sitemap_genre_p1_xml, ContentType="text/xml")

        # Page 2
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET,
            f"latest/sitemaps/cities/{genre}_p2_{TODAY}.xml",
        ).put(Body=sitemap_genre_p2_xml, ContentType="text/xml")
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET, f"latest/sitemaps/cities/{genre}_p2.xml"
        ).put(Body=sitemap_genre_p2_xml, ContentType="text/xml")

    sitemap_index = jinja_template.render(genres=GENRES, lastmod=TODAY)
    boto_s3_client.Object(
        SITEMAP_S3_BUCKET,
        f"latest/sitemaps/cities/index_{TODAY}.xml",
    ).put(Body=sitemap_index, ContentType="text/xml")
    boto_s3_client.Object(SITEMAP_S3_BUCKET, f"latest/sitemaps/cities/index.xml").put(
        Body=sitemap_index, ContentType="text/xml"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()
