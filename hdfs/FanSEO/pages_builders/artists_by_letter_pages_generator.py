from datetime import datetime
import boto3
from pyspark import SparkFiles
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    ArrayType,
)


REGION_NAME = "us-east-1"
S3_BUCKET = "concerts.hypebot.com"
CURRENT_YEAR = datetime.now().year


class ForeachWriter:
    def __init__(self, footer_artists, footer_cities):
        self.footer_artists = footer_artists
        self.footer_cities = footer_cities

    def open(self, partition_id, epoch_id):
        session = boto3.Session(region_name=REGION_NAME)
        self.s3_client = session.resource("s3")
        return True

    def process(self, row):
        html_template = jinja_env.get_template("search/artists/byLetter.njk")
        rendered = html_template.render(
            {
                "env": "production",
                "domain": "https://concerts.hypebot.com/",
                "letter": row.nameFirstLetter,
                "artists": sorted(row.artists, key=lambda a: a["name"]),
                "footerArtists": self.footer_artists,
                "footerCities": self.footer_cities,
                "copyrightYear": CURRENT_YEAR,
                "currentYear": CURRENT_YEAR,
            },
        )

        s3_path = "latest/search/artists"
        self.upload_to_s3(f"{s3_path}/{row.nameFirstLetter}", rendered)

    def close(self, error):
        if error:
            raise error

    def upload_to_s3(self, path, body):
        self.s3_client.Object(S3_BUCKET, path).put(Body=body, ContentType="text/html")


def main():
    global jinja_env, artists_lists_by_letter_template
    conf = SparkConf()
    conf.setAppName("Fan SEO template generation")

    conf.set("spark.dynamicAllocation.enabled", "false")
    conf.set("spark.executor.cores", "1")
    conf.set("spark.executor.instances", "1")
    conf.set("spark.executor.memory", "1g")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    sc.addPyFile("s3a://bit-emr-cluster/dev/rene/packages/jinja2.zip")
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/html_templates/artists_by_letter.py"
    )
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/pages_builders/city_pages/city_pages_context_builder.py"
    )

    import jinja2
    import artists_by_letter
    import city_pages_context_builder

    jinja_env = jinja2.Environment(
        loader=jinja2.DictLoader(artists_by_letter.TEMPLATES)
    )

    footer_artists_path = "s3a://bit-emr-cluster/dev/rene/qualified_footer_artists"
    path = "s3a://bit-emr-cluster/dev/rene/artists_by_name_first_letter"

    schema = StructType(
        [
            StructField("nameFirstLetter", StringType()),
            StructField(
                "artists",
                ArrayType(
                    StructType(
                        [
                            StructField("id", IntegerType()),
                            StructField("name", StringType()),
                            StructField("nameSlug", StringType()),
                            StructField("nameFirstLetter", StringType()),
                        ]
                    )
                ),
            ),
        ]
    )

    footer_artists_collection = spark.read.parquet(footer_artists_path).collect()
    footer_cities_collection = city_pages_context_builder.FOOTER_CITIES_COLLECTION

    query = (
        spark.readStream.schema(schema)
        .parquet(path)
        .writeStream.trigger(once=True)
        .foreach(
            ForeachWriter(
                footer_artists=footer_artists_collection,
                footer_cities=footer_cities_collection,
            )
        )
        .outputMode("update")
        .start()
    )

    query.awaitTermination()

    spark.stop()

    exit()


if __name__ == "__main__":
    main()
