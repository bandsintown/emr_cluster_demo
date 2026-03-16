from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat, when, col, lit

import boto3
from datetime import datetime, time

FAN_SEO_DATA_S3_BUCKET_PATH = "s3a://bit-emr-cluster/dev/rene"
SITEMAP_DOMAIN_URL = "https://concerts.hypebot.com"
TODAY = datetime.now().strftime("%Y-%m-%d")
REGION_NAME = "us-east-1"
SITEMAP_S3_BUCKET = "concerts.hypebot.com"
S3_DEV_BUCKET = "bit-bigdata-state-cycle"


def main(is_dev):
    conf = SparkConf()
    conf.setAppName("Fan SEO Sitemap data")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    boto_session = boto3.Session(region_name=REGION_NAME)
    boto_s3_client = boto_session.resource("s3")

    sitemap = (
        spark.read.parquet(f"{FAN_SEO_DATA_S3_BUCKET_PATH}/artist_pages_data")
        .select(
            concat(
                lit(f"{SITEMAP_DOMAIN_URL}/artist/"),
                when(col("artist.nameFirstLetter") == "#", "%23").otherwise(
                    col("artist.nameFirstLetter")
                ),
                lit("/"),
                col("artist.id"),
                lit("-"),
                col("artist.nameSlug"),
            ).alias("loc"),
            lit(TODAY).alias("lastmod"),
        )
        .toPandas()
        .to_xml(
            root_name="urlset",
            row_name="url",
            index=False,
            pretty_print=False,
            namespaces={
                "": "http://www.sitemaps.org/schemas/sitemap/0.9",
            },
        )
    )

    if is_dev:
        boto_s3_client.Object(
            S3_DEV_BUCKET, f"dev_theo/fan_seo/sitemap_artists_{TODAY}.xml"
        ).put(Body=sitemap, ContentType="text/xml")
        boto_s3_client.Object(
            S3_DEV_BUCKET, f"dev_theo/fan_seo/sitemap_artists.xml"
        ).put(Body=sitemap, ContentType="text/xml")
    else:
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET, f"latest/sitemaps/sitemap_artists_{TODAY}.xml"
        ).put(Body=sitemap, ContentType="text/xml")
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET, f"latest/sitemaps/sitemap_artists.xml"
        ).put(Body=sitemap, ContentType="text/xml")

    spark.stop()
    exit()


if __name__ == "__main__":
    import sys
    is_dev = False
    if len(sys.argv) > 1:
        is_dev = sys.argv[1].lower() == 'true'
    
    main(is_dev)
