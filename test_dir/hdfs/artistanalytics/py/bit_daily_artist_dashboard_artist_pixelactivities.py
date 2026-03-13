import boto3
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from datetime import datetime, timedelta, timezone
from dateutil.relativedelta import relativedelta

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

def build_hive_table():
    return """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artists_ip_ticketclicks_s3 (
            artist_id INT,
            ip STRING,
            nb INT
        )
        PARTITIONED BY (`date` STRING)
        LOCATION 's3a://bit-precomputed-data/artists_ip_ticketclicks/';
    """

def insert_overwrite_into_pixelactivities_table(last_three_days):
    return f"""
        INSERT OVERWRITE TABLE bit_daily_artist_dashboard.artists_ip_ticketclicks_s3
        PARTITION(`date`)
        SELECT
            CAST(logs.custom['artist_id'] AS INT) AS artist_id,
            logs.ip_address AS ip,
            COUNT(*) AS nb,
            to_date(logs.ds) AS `date`
        FROM bit_logs.pixelactivities logs
        JOIN bit_daily_data_snapshot.events_batch AS evl
            ON (logs.custom['artist_event_id'] = evl.artist_event_int_id)
        WHERE nvl(evl.streaming_event,FALSE) = FALSE
            AND logs.type = 'ticket'
            AND logs.action = 'click'
            AND logs.ds >= '{last_three_days}'
            AND logs.custom['artist_id'] IS NOT NULL
        GROUP BY
            logs.custom['artist_id'],
            logs.ip_address,
            to_date(logs.ds);
    """

def create_temp_artists_ip_ticket_clicks_table():
    return """
        CREATE TABLE IF NOT EXISTS temp_artists_ip_ticketclicks (
            artist_id INT,
            ip STRING,
            nb INT
        )
        LOCATION '/bit_daily/artist_dashboard/temp_artists_ip_ticketclicks/'
        TBLPROPERTIES ("auto.purge"="true");
    """

def insert_overwrite_into_temp_artists_ip_ticket_click(first_day_of_last_six_full_months):
    return f"""
        INSERT OVERWRITE bit_daily_artist_dashboard.temp_artists_ip_ticketclicks
        SELECT
            artist_id,
            ip,
            sum(nb)
        FROM bit_daily_artist_dashboard.artists_ip_ticketclicks_s3
        WHERE `date` >= '{first_day_of_last_six_full_months}'
        GROUP BY
            artist_id,
            ip;
    """

def main():
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist Pixelactivities')
    conf.set("spark.hive.exec.dynamic.partition", "true")
    conf.set("spark.hive.exec.dynamic.partition.mode", "nonstrict")
    conf.set("spark.hive.exec.max.dynamic.partitions", "100000")
    conf.set("spark.hive.exec.max.dynamic.partitions.pernode", "100000")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    current_time = datetime.now(tz=timezone.utc)
    last_three_days = (current_time - timedelta(days=3)).strftime("%Y-%m-%d")
    first_day_of_last_six_full_months = (current_time - relativedelta(months=6)).replace(day=1)
    
    spark.sql(build_hive_table())
    spark.sql(insert_overwrite_into_pixelactivities_table(last_three_days))

    spark.sql(create_temp_artists_ip_ticket_clicks_table())
    spark.sql(insert_overwrite_into_temp_artists_ip_ticket_click(first_day_of_last_six_full_months))

    df = spark.read.table("bit_daily_artist_dashboard.artists_ip_ticketclicks_s3")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_ip_ticketclicks_by_day_records": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()