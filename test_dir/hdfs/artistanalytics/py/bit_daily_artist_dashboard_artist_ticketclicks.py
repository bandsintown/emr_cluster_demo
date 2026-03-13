import boto3
import sys
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

################################# TEMP TICKETCLICKS TABLE #####################################
def drop_temp_ticketclicks_table():
    return """
       DROP TABLE IF EXISTS bit_daily_artist_dashboard.temp_ticketclick_logs;
    """

def build_temp_ticketclicks_table():
    return """
       CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.temp_ticketclick_logs (
            `date` STRING,
            artist_id INT,
            artist_event_id INT,
            upcoming INT,
            nb INT
        )
        STORED AS PARQUET
        LOCATION '/bit_daily/artist_dashboard/temp_ticketclick_logs';
    """

def insert_into_temp_ticketlicks_table(last_six_month_datetime):
    return f"""
        INSERT OVERWRITE bit_daily_artist_dashboard.temp_ticketclick_logs
        SELECT
            CONCAT(CAST(to_date(logs.click_datetime) AS STRING), ' 00:00:00') AS `date`,
            CAST(evl.artist.id AS INT),
            logs.artist_event_id,
            IF(to_date(evl.date_info.event_date) >= from_unixtime(unix_timestamp(), 'yyyy-MM-dd'), 1,0),
            COUNT(logs.click_datetime) AS nb
        FROM bit_logs.ticketclicks AS logs
        JOIN bit_daily_data_snapshot.events_raw AS evl
            ON logs.artist_event_id = evl.artist_event_int_id
        WHERE logs.`date` >= to_timestamp('{last_six_month_datetime}')
            AND evl.actor = 'artist'
            AND evl.artist.id IS NOT NULL
            AND NVL(evl.streaming_info.flag, FALSE) = FALSE
            AND evl.status in ('PUBLISHED','AUTOPUBLISHED')
        GROUP BY
            CONCAT(CAST(to_date(logs.click_datetime) AS STRING), ' 00:00:00'),
            CAST(evl.artist.id AS INT),
            IF(to_date(evl.date_info.event_date) >= from_unixtime(unix_timestamp(), 'yyyy-MM-dd'), 1,0),
            logs.artist_event_id;
    """
################################################################################################


################################# TICKETCLICKS BY DAY #################################
def build_daily_ticketclicks_by_day(year_month_day):
    return f"""
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_ticketclicks_by_day (
            artist_id INT,
            `day` STRING,
            ticketclicks_count INT
        )
        LOCATION 's3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/artist_ticketclicks_by_day';
    """

def insert_into_daily_ticketclicks_by_day():
    return """
        INSERT OVERWRITE bit_daily_artist_dashboard.artist_nb_ticketclicks_by_day 
        SELECT
            logs.artist_id,
            logs.`date` AS day,
            sum(logs.nb) AS ticketclicks_count
        FROM bit_daily_artist_dashboard.temp_ticketclick_logs logs
        GROUP BY
            logs.artist_id,
            logs.`date`;
    """
################################################################################################


################################# UPCOMING EVENTS TICKETCLICKS BY DAY #####################################
def drop_upcoming_events_ticketclicks_table():
    return f"""
       DROP TABLE IF EXISTS bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day;
    """


def build_upcoming_events_ticketclicks_table(path):
    return f"""
       CREATE EXTERNAL TABLE IF NOT EXISTS bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day (
            `date` STRING,
            artist_id INT,
            artist_event_id INT,
            nb INT
        )
        STORED AS PARQUET
        LOCATION '{path}';
    """

def seed_upcoming_events_ticketclicks_table():
    return f"""
        INSERT OVERWRITE bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day
        SELECT
            `date`,
            artist_id,
            artist_event_id,
            nb
        FROM bit_daily_artist_dashboard.temp_ticketclick_logs
        WHERE upcoming = 1;
    """

def select_upcoming_events_ticketclicks_table_from(last_six_month_datetime):
    return f"""
        SELECT
            ue.`date`,
            ue.artist_id,
            ue.artist_event_id,
            ue.nb
        FROM (
            SELECT
                `date`,
                artist_id,
                artist_event_id,
                nb
            FROM bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day
            WHERE `date` < '{last_six_month_datetime}'
            UNION ALL
            SELECT
                `date`,
                artist_id,
                artist_event_id,
                nb
            FROM bit_daily_artist_dashboard.temp_ticketclick_logs
            WHERE upcoming = 1
            AND `date` >= '{last_six_month_datetime}'
        ) AS ue
        JOIN bit_daily_data_snapshot.events_raw AS evl
            ON ue.artist_event_id = evl.artist_event_int_id
        WHERE to_date(evl.date_info.event_date) >= from_unixtime(unix_timestamp(), 'yyyy-MM-dd')
            AND evl.actor = 'artist'
            AND evl.artist.id IS NOT NULL
            AND NVL(evl.streaming_info.flag, FALSE) = FALSE
            AND evl.status in ('PUBLISHED','AUTOPUBLISHED')
    """

def update_location_upcoming_events_ticketclicks_table(path):
    return f"""
        ALTER TABLE bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day SET LOCATION '{path}';
    """

################################################################################################


################################# UPCOMING TICKETCLICKS BY EVENT ID #####################################
def drop_upcoming_ticketclicks_by_event_id():
    return """
       DROP TABLE IF EXISTS bit_daily_artist_dashboard.upcoming_ticketclicks_by_event_id;
    """

def build_upcoming_ticketclicks_by_event_id():
    return """
       CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.upcoming_ticketclicks_by_event_id (
            artist_event_id INT,
            ticketclicks_count INT
        )
        STORED AS PARQUET
        LOCATION '/bit_daily/artist_dashboard/upcoming_ticketclicks_by_event_id';
    """

def insert_into_upcoming_ticketclicks_by_event_id():
    return f"""
        INSERT OVERWRITE bit_daily_artist_dashboard.upcoming_ticketclicks_by_event_id
        SELECT
            logs.artist_event_id,
            SUM(logs.nb) AS ticketclicks_count
        FROM bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day logs
        GROUP BY
            logs.artist_event_id;
    """
################################################################################################

def main():
    """
        Spark Config
    """
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist Ticketclicks')
    conf.set("spark.hive.exec.dynamic.partition", "true")
    conf.set("spark.hive.exec.dynamic.partition.mode", "nonstrict")
    conf.set("spark.hive.exec.max.dynamic.partitions", "100000")
    conf.set("spark.hive.exec.max.dynamic.partitions.pernode", "100000")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    year_month_day = sys.argv[1]
    """
        Get the date six months ago for the begining of that month
    """
    current_datetime = date.today()
    last_six_month_date = current_datetime - relativedelta(months=+6)
    last_six_month_datetime = str(datetime(year = last_six_month_date.year, month = last_six_month_date.month, day = 1))

    """
        Source Table from which all subsequent tables are built from
        Contains ticketclicks for the past six months
    """
    spark.sql(drop_temp_ticketclicks_table())
    spark.sql(build_temp_ticketclicks_table())
    spark.sql(insert_into_temp_ticketlicks_table(last_six_month_datetime))

    """
        Daily Ticketclicks Cumulative Table.
        Contains ticketclicks for each day by artist id.
    """
    spark.sql(build_daily_ticketclicks_by_day(year_month_day))
    spark.sql(insert_into_daily_ticketclicks_by_day())

    
    # """
    #     Daily Ticketclicks Upcoming Events Table.
    # """
    ### Only use to Seed the table
    # spark.sql(drop_upcoming_events_ticketclicks_table())
    # spark.sql(build_upcoming_events_ticketclicks_table(path))
    # spark.sql(seed_upcoming_events_ticketclicks_table())

    path = f's3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/upcoming_events_ticketclicks_by_day/{year_month_day}'
    spark.sql(build_upcoming_events_ticketclicks_table(path))
    spark.sql(select_upcoming_events_ticketclicks_table_from(last_six_month_datetime)).write.mode(
        "overwrite").parquet(path)
    spark.sql(update_location_upcoming_events_ticketclicks_table(path))


    """
        Daily Ticketclicks Cumulative Table.
        Contains ticketclicks for each day by artist id.
    """
    spark.sql(drop_upcoming_ticketclicks_by_event_id())
    spark.sql(build_upcoming_ticketclicks_by_event_id())
    spark.sql(insert_into_upcoming_ticketclicks_by_event_id())


    df = spark.read.table("bit_daily_artist_dashboard.upcoming_events_ticketclicks_by_day")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_upcoming_events_ticketclicks_by_day": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()