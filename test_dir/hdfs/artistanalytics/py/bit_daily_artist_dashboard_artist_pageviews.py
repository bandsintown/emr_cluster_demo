import boto3
import sys
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

############################### PAGE VIEWS GROUPED BY DAY ######################################
def build_artist_nb_page_views_by_day_table(year_month_day):
    return f"""
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_pageviews_by_day (
            artist_id INT,
            day STRING,
            pageviews_count INT
        )
        LOCATION 's3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/artist_pageviews_by_day'
    """

def insert_overwrite_into_artist_nb_page_views_by_day_table(first_day_of_last_six_full_months):
    return f"""
        INSERT OVERWRITE bit_daily_artist_dashboard.artist_nb_pageviews_by_day
        SELECT
            CAST(logs.custom.artist_id as INT) AS artist_id,
            logs.`date`,
            COUNT(logs.nonce) AS cnt
        FROM bit_logs.pixelactivities logs
        WHERE logs.ds >= '{first_day_of_last_six_full_months}'
            AND (logs.source = 'Artist Page' OR logs.source = 'Event Page')
        GROUP BY
            logs.`date`,
            logs.custom.artist_id;
    """


##################################################################################################

def main():
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist PageViews')
    conf.set("spark.hive.exec.dynamic.partition", "true")
    conf.set("spark.hive.exec.dynamic.partition.mode", "nonstrict")
    conf.set("spark.hive.exec.max.dynamic.partitions", "100000")
    conf.set("spark.hive.exec.max.dynamic.partitions.pernode", "100000")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    year_month_day = sys.argv[1]

    current_time = datetime.now(tz=timezone.utc)
    first_day_of_last_six_full_months = (current_time - relativedelta(months=6)).replace(day=1)
    
    """
        Creates a table that contains number of page views gained for each day
    """
    spark.sql(build_artist_nb_page_views_by_day_table(year_month_day))
    spark.sql(insert_overwrite_into_artist_nb_page_views_by_day_table(first_day_of_last_six_full_months))

    df = spark.read.table("bit_daily_artist_dashboard.artist_nb_pageviews_by_day")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_pageviews_by_day_records": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()