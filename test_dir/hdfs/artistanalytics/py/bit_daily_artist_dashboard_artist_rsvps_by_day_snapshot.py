import boto3
import sys

from dateutil.parser import parse
from datetime import datetime, timedelta, timezone
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import *
from pyspark.sql.window import *
from pyspark.sql.functions import udf, coalesce, col, count

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

def percentage_change(start_count, end_count):
    return ((end_count - start_count) / start_count) * 100


def drop_hive_table():
    return """
        DROP TABLE IF EXISTS bit_daily_artist_dashboard.artist_nb_rsvps_by_day
    """

def build_hive_table():
    query = """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_rsvps_by_day (
            artist_id INT,
            day STRING,
            rsvps_count INT
        )
        STORED AS PARQUET
    """
    return query


"""udf"""
def convert_timestamp_to_date(ts):
    try:
        return parse(ts).date().strftime('%Y-%m-%d')
    except:
        return ts


def file_exists(sc, path):
    try:
        rdd = sc.textFile(path)
        rdd.take(1)
        return True
    except:
        return False


def main():
    if len(sys.argv) < 3:
        sys.exit()

    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard RSVPs By Day Snapshot')
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    TODAY = datetime.now(tz = timezone.utc).date()
    SIX_MONTHS_AGO = TODAY - timedelta(days = 180)

    """UDFs"""
    ts_udf = udf(lambda z: convert_timestamp_to_date(z), StringType())

    """Vars"""
    year_month_day = sys.argv[1]
    skip_checking_counts = sys.argv[2]
    check_counts = (skip_checking_counts != "TRUE")
    TODAY = datetime.now(tz = timezone.utc).date()
    FOUR_DAYS_AGO = TODAY - timedelta(days = 4)

    spark.sql(build_hive_table())
    df_events = spark.read.table("bit_daily_data_snapshot.events_batch").select(
        "artist_id",
        col("artist_event_int_id").alias("event_id")
    )

    df_rsvps = spark.read.table("bit_daily_data_snapshot.rsvp").select(
        "user_id",
        col("event_id").cast(IntegerType()).alias("event_id"),
        ts_udf("timestamp").alias("day")
    ).filter(
        (col("status") != "cancelled") &
        (col("timestamp") >= FOUR_DAYS_AGO)
    )

    tpDF = df_rsvps.join(df_events, df_rsvps.event_id == df_events.event_id).select(
        df_events.artist_id,
        df_rsvps.user_id,
        df_rsvps.event_id,
        df_rsvps.day
    ).distinct()

    tpDF = tpDF.groupBy("artist_id", "day").agg(count("user_id").alias("rsvps_count"))
    tpDF = tpDF.withColumn("rsvps_count", tpDF.rsvps_count.cast(IntegerType()))
    to_process_count = tpDF.cache().count()

    bDF = spark.read.table("bit_daily_artist_dashboard.artist_nb_rsvps_by_day")
    start_count = bDF.count()

    """
    Combine previous fan artist delivered emails snapshot with updates
    """
    df = bDF.join(tpDF, (bDF.artist_id == tpDF.artist_id) & (bDF.day == tpDF.day), "outer").select(
        coalesce(tpDF.artist_id, bDF.artist_id).alias("artist_id"),
        coalesce(tpDF.day, bDF.day).alias("day"),
        coalesce(tpDF.rsvps_count, bDF.rsvps_count).alias("rsvps_count")
    )
    df = df.filter(df.day >= SIX_MONTHS_AGO)
    output = f"s3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/rsvps_by_day_snapshot/{year_month_day}"
    df.cache().write.mode("overwrite").parquet(output)

    end_count = df.count()
    print(f"new counts: {end_count}, old_count: {start_count}, to process count: {to_process_count}")
    percent_change = percentage_change(start_count, end_count)

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_rsvps_by_day_start_count": start_count,
            "bit_daily_artist_dashboard_rsvps_by_day_end_count": end_count,
            "bit_daily_artist_dashboard_rsvps_by_day_snapshot_to_process_count" : to_process_count,
            "bit_daily_artist_dashboard_rsvps_by_day_percent_change" : percent_change
        }
    )

    if check_counts and percent_change < -25:
        print(
            "Snapshot Counts Are Off - {0}/{1}".format(start_count, end_count))
        sys.exit(-1)
    else:
        query = """
            ALTER TABLE bit_daily_artist_dashboard.artist_nb_rsvps_by_day SET LOCATION '{}'
        """.format(output)
        spark.sql(query)

    spark.stop()
    exit()

if __name__ == "__main__":
    main()