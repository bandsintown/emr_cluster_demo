import boto3

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, size as _size, sum as _sum

from datetime import datetime, timedelta

REGION_NAME = "us-east-1"
metrics_namespace = "FanSEOPages"
cloudwatch = boto3.client("cloudwatch", region_name=REGION_NAME)

POPULAR_CITIES_PATH = (
    "s3a://bit-emr-cluster/dev/rene/city_pages/popular_cities_with_nearby_cities"
)


def send_to_cloudwatch_metrics(counters):
    for key, value in counters.items():
        metrics = [{"MetricName": key, "Value": int(value)}]
        cloudwatch.put_metric_data(Namespace=metrics_namespace, MetricData=metrics)


def main():
    conf = SparkConf()
    conf.setAppName("FanSEO Pages Metrics")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    popular_cities_pages_data_df = spark.read.parquet(POPULAR_CITIES_PATH)

    fan_seo_city_pages_count = popular_cities_pages_data_df.count()

    send_to_cloudwatch_metrics(
        {
            "fan_seo_city_pages_count": fan_seo_city_pages_count,
        }
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()