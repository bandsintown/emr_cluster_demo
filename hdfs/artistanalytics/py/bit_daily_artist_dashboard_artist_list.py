import boto3
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

def build_artist_list_table():
    return """
        CREATE TABLE IF NOT EXISTS artist_list (
            artist_id INT,
            artist_name STRING,
            managed INT,
            tracker_count INT,
            on_tour INT,
            nb_upcoming_events INT,
            url STRING,
            media_id INT
        )
        LOCATION '/bit_daily/artist_dashboard/artist_list/'
    """

def insert_overwrite_into_artist_list_table():
    return """
        INSERT OVERWRITE TABLE bit_daily_artist_dashboard.artist_list
        SELECT
            ald.artist_id,
            ald.name,
            ald.managed,
            ald.tracker_count,
            IF (ald.nb_upcoming_events>0, 1, 0) on_tour,
            ald.nb_upcoming_events,
            ald.facebook_page_url AS url,
            ald.media_id
        FROM bit_daily_data_snapshot.public_artists ald
        WHERE ald.tracker_count >= 100;
    """


def main():
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist List')
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    
    spark.sql(build_artist_list_table())
    spark.sql(insert_overwrite_into_artist_list_table())

    df = spark.read.table("bit_daily_artist_dashboard.artist_list")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_artist_list_records": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()