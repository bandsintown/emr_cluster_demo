from pyspark import SparkConf
from pyspark.sql import SparkSession

import boto3
from datetime import datetime, timedelta

SITEMAP_DOMAIN_URL = "https://concerts.hypebot.com"
NOW = datetime.now()
TODAY = datetime.now().strftime("%Y-%m-%d")
PREVIOUS_SUNDAY = (NOW - timedelta(days=NOW.isoweekday() + 1)).strftime("%Y-%m-%d")
REGION_NAME = "us-east-1"
SITEMAP_S3_BUCKET = "concerts.hypebot.com"
S3_DEV_BUCKET = "bit-bigdata-state-cycle"

SITEMAP_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
    <sitemapindex xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/siteindex.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    {% for sitemap in sitemaps %}
    <sitemap>
        <loc>https://concerts.hypebot.com/sitemaps/{{sitemap.path}}</loc>
        <lastmod>{{sitemap.lastmod}}</lastmod>
    </sitemap>
    {% endfor %}
</sitemapindex>
"""

# Pages generation is run daily for artists and every sunday for cities
SITEMAPS = [
    {"path": "sitemap_artists.xml", "lastmod": TODAY},
    {"path": "cities/index.xml", "lastmod": PREVIOUS_SUNDAY},
]


def main(is_dev):
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

    sitemap_index = jinja_template.render(sitemaps=SITEMAPS)
    if is_dev:
        boto_s3_client.Object(
            S3_DEV_BUCKET, f"dev_theo/fan_seo/sitemaps/index_{TODAY}.xml"
        ).put(Body=sitemap_index, ContentType="text/xml")
        boto_s3_client.Object(
            S3_DEV_BUCKET, f"dev_theo/fan_seo/sitemaps/index.xml"
        ).put(Body=sitemap_index, ContentType="text/xml")
    else:
        boto_s3_client.Object(
            SITEMAP_S3_BUCKET,
            f"latest/sitemaps/index_{TODAY}.xml",
        ).put(Body=sitemap_index, ContentType="text/xml")
        boto_s3_client.Object(SITEMAP_S3_BUCKET, f"latest/sitemaps/index.xml").put(
            Body=sitemap_index, ContentType="text/xml"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    import sys
    is_dev = False
    if len(sys.argv) > 1:
        is_dev = sys.argv[1].lower() == 'true'
    
    main(is_dev)
