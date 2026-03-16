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


################################# UNCOMING EVENT RSVP TICKETCLICKS BY EVENT DATE ###########################
def drop_upcoming_event_rsvps_ticketclicks_by_event_date():
    return """
        DROP TABLE IF EXISTS bit_daily_artist_dashboard.upcoming_event_rsvps_ticketclicks_by_event_date;
    """

def build_upcoming_event_rsvps_ticketclicks_by_event_date():
    return """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.upcoming_event_rsvps_ticketclicks_by_event_date (
            artist_id INT,
            venue_name STRING,
            event_date STRING,
            city STRING,
            region STRING,
            country STRING,
            rsvp_count INT,
            ticketclick_count INT
        )
        LOCATION '/bit_daily/artist_dashboard/upcoming_event_rsvps_ticketclicks_by_event_date/'
        TBLPROPERTIES ("auto.purge"="true");
    """

def insert_into_upcoming_event_rsvps_ticketclicks_by_event_date():
    return """
        INSERT OVERWRITE TABLE bit_daily_artist_dashboard.upcoming_event_rsvps_ticketclicks_by_event_date
        SELECT
            evl.artist_id,
            upper(regexp_replace(evl.venue_name, '\\n|\\r', ' ')),
            from_unixtime(unix_timestamp(evl.starts_at, "yyyy-MM-dd'T'HH:mm:ss'Z'")),
            regexp_replace(evl.venue_city, '\\n|\\r', ' '),
            regexp_replace(evl.venue_region, '\\n|\\r', ' '),
            regexp_replace(evl.venue_country, '\\n|\\r', ' '),
            COUNT(DISTINCT r.user_id),
            NVL(logs.ticketclicks_count, 0)
        FROM bit_daily_data_snapshot.events_batch AS evl
        JOIN bit_daily_data_snapshot.public_artists al
            ON (evl.artist_id=al.artist_id)
        LEFT OUTER JOIN (
            SELECT 
                user_id, 
                event_id
            FROM fan_search.rsvps
            WHERE status != 'cancelled'
        ) AS r
            ON (r.event_id = evl.artist_event_int_id)
        LEFT OUTER JOIN bit_daily_artist_dashboard.upcoming_ticketclicks_by_event_id AS logs
            ON (logs.artist_event_id = evl.artist_event_int_id)
        WHERE NVL(evl.streaming_event, FALSE) = FALSE
        GROUP BY
            evl.artist_id,
            upper(regexp_replace(evl.venue_name, '\\n|\\r', ' ')),
            from_unixtime(unix_timestamp(evl.starts_at, "yyyy-MM-dd'T'HH:mm:ss'Z'")),
            regexp_replace(evl.venue_city, '\\n|\\r', ' '),
            regexp_replace(evl.venue_region, '\\n|\\r', ' '),
            regexp_replace(evl.venue_country, '\\n|\\r', ' '),
            NVL(logs.ticketclicks_count,0);
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


    """
        Uncoming Event Venues RSVPs Table.
        Contains tickeclicks for the last six months grouped by venue and artist id.
    """
    spark.sql(drop_upcoming_event_rsvps_ticketclicks_by_event_date())
    spark.sql(build_upcoming_event_rsvps_ticketclicks_by_event_date())
    spark.sql(insert_into_upcoming_event_rsvps_ticketclicks_by_event_date())


    df = spark.read.table("bit_daily_artist_dashboard.upcoming_event_rsvps_ticketclicks_by_event_date")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_ue_rsvps_ticketclicks_by_event_date": record_count
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()