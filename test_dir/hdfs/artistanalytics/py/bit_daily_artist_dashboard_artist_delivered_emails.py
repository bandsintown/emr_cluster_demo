import boto3
import sys

from dateutil.parser import parse
from datetime import datetime, timedelta, timezone
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import *
from pyspark.sql.window import *
from pyspark.sql.functions import udf, row_number, col, explode, from_unixtime, count

EMAIL_CATEGORIES = [
    "Fan - Weekly Update",
    "Fan - Just Announced",
    "Fan - RSVP Reminder",
    "Fan - Ticket Reminder",
    "Fan - Ticket Inventory",
    "Fan - Low Inventory",
    "Fan - Last Chance Inventory",
    "Fan - Memories",
    "Fan - Just Announced Festival",
    "Fan - Festival Reminder",
    "Fan - Festival Reminder Streaming",
    "Fan - RSVP Reminder Streaming"
]

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
        DROP TABLE IF EXISTS bit_daily_artist_dashboard.artist_nb_delivered_emails_by_day
    """

def build_hive_table():
    query = """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_delivered_emails_by_day (
            artist_id INT,
            day STRING,
            delivered_emails_count INT
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
    conf.setAppName('BIT Daily Artist Dashboard Delivered Emails By Day')

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    TODAY = datetime.now(tz = timezone.utc).date()
    SIX_MONTHS_AGO = TODAY - timedelta(days = 180)
    """UDFs"""
    ts_udf = udf(lambda z: convert_timestamp_to_date(z), StringType())

    """Vars"""
    year_month_day = sys.argv[1]
    skip_checking_counts = sys.argv[2]
    check_counts = (skip_checking_counts != "TRUE")
    current_time = datetime.now()

    """Delivered Emails To Process"""
    files = []
    day_range = range(-1, 4)
    days = list(day_range)
    for day in days:
        date = current_time - timedelta(days=day)
        path = 's3://bit-data-firehose/sendgrid-callback-smtp/{0}/{1}/{2}/*'.format(
            date.strftime("%Y"), date.strftime("%m"), date.strftime("%d"))
        if file_exists(sc, path):
            files.append(path)

    schema = StructType([
        StructField("artist_ids", ArrayType(StringType())),
        StructField("category", StringType()),
        StructField("email", StringType()),
        StructField("event", StringType()),
        StructField("event_ids", ArrayType(StringType())),
        StructField("ip", StringType()),
        StructField("msg_id", StringType()),
        StructField("response", StringType()),
        StructField("sg_event_id", StringType()),
        StructField("sg_message_id", StringType()),
        StructField("show_type", StringType()),
        StructField("smtp-id", StringType()),
        StructField("ticket_type", StringType()),
        StructField("timestamp", StringType()),
        StructField("tls", IntegerType()),
        StructField("user_id", StringType())
    ])

    tpDF = spark.read.schema(schema).json(files).select(
        'artist_ids',
        'category',
        'email',
        "msg_id",
        "user_id",
        from_unixtime(col("timestamp")).alias("timestamp")
    ).filter(
        col('email').isNotNull() & 
        col('msg_id').isNotNull() & 
        (col("event") == "delivered") &
        col("category").isin(EMAIL_CATEGORIES)
    )

    tpDF = tpDF.select(
        explode(col('artist_ids')).alias("artist_id"),
        'category',
        'email',
        "msg_id",
        "user_id",
        ts_udf("timestamp").alias("day")
    )

    tpDF = tpDF.withColumn("artist_id", tpDF.artist_id.cast(IntegerType()))

    tpDF = tpDF.groupBy("artist_id", "day")\
        .agg(count("email").alias("delivered_emails_count"))
    tpDF = tpDF.withColumn("delivered_emails_count", tpDF.delivered_emails_count.cast(IntegerType()))
    
    to_process_count = tpDF.count()
    spark.sql(build_hive_table())
    bDF = spark.read.table('bit_daily_artist_dashboard.artist_nb_delivered_emails_by_day')
    start_count = bDF.count()

    """
    Combine previous fan artist delivered emails snapshot with updates
    """
    df = bDF.unionAll(tpDF)

    """Window functions to calculate the most recent update"""
    last_updated = Window.partitionBy([df.artist_id, df.day]).orderBy(col("artist_id"), col("day").desc())

    df = df.withColumn('row', row_number().over(last_updated)).select(
        df.artist_id,
        df.day,
        df.delivered_emails_count
    ).filter((col('row') == 1))

    df = df.filter(df.day >= SIX_MONTHS_AGO)
    output = f"s3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/delivered_emails_snapshot/{year_month_day}"
    df.write.mode("overwrite").parquet(output)

    end_count = spark.read.parquet(output).count()
    percent_change = percentage_change(start_count + 1, end_count)

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_delivered_emails_by_day_start_count": start_count,
            "bit_daily_artist_dashboard_delivered_emails_by_day_end_count": end_count,
            "bit_daily_artist_dashboard_delivered_emails_by_day_snapshot_to_process_count" : to_process_count,
            "bit_daily_artist_dashboard_delivered_emails_by_day_percent_change" : percent_change
        }
    )

    if check_counts and percent_change < -25:
        print(
            "Snapshot Counts Are Off - {0}/{1}".format(start_count, end_count))
        sys.exit(-1)
    else:
        query = """
            ALTER TABLE bit_daily_artist_dashboard.artist_nb_delivered_emails_by_day SET LOCATION '{}'
        """.format(output)
        spark.sql(query)

    spark.stop()
    exit()

if __name__ == "__main__":
    main()