import boto3

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, size as _size, sum as _sum

from datetime import datetime, timedelta

REGION_NAME = "us-east-1"
metrics_namespace = "FanSEOPages"
cloudwatch = boto3.client("cloudwatch", region_name=REGION_NAME)

FAN_SEO_DATA_S3_BUCKET_PATH = "s3a://bit-emr-cluster/dev/rene"


def send_to_cloudwatch_metrics(counters):
    for key, value in counters.items():
        metrics = [{"MetricName": key, "Value": int(value)}]
        cloudwatch.put_metric_data(Namespace=metrics_namespace, MetricData=metrics)


def main(is_dev):
    conf = SparkConf()
    conf.setAppName("FanSEO Pages Metrics")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    artist_pages_data_df = spark.read.parquet(
        f"{FAN_SEO_DATA_S3_BUCKET_PATH}/artist_pages_data"
    )

    fan_seo_artist_pages_count = artist_pages_data_df.count()
    fan_seo_artist_events_count = (
        artist_pages_data_df.filter(artist_pages_data_df.events.isNotNull())
        .withColumn("events_count", _size(col("events")))
        .agg(_sum("events_count").alias("total_events_count"))
        .first()
        .total_events_count
    )

    if is_dev:
        i = 1 # Does nothing
    else:
        send_to_cloudwatch_metrics(
            {
                "fan_seo_artist_pages_count": fan_seo_artist_pages_count,
                "fan_seo_artist_events_count": fan_seo_artist_events_count,
            }
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    import sys
    is_dev = False
    if len(sys.argv) > 1:
        is_dev = sys.argv[1].lower() == 'true'
    
    main(is_dev)
