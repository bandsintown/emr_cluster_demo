import boto3
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
import sys

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

############################### FOLLOWERS GROUPED BY DAY ######################################
def build_artist_nb_contacts_by_day_table(year_month_day):
    return f"""
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_contacts_by_day (
            artist_id INT,
            day STRING,
            contact_count INT
        )
        LOCATION 's3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/artist_contacts_by_day'
    """

def insert_overwrite_into_artist_nb_contacts_by_day_table():        
    return """
        INSERT OVERWRITE bit_daily_artist_dashboard.artist_nb_contacts_by_day
        SELECT 
            contacts.artist_id,
            contacts.day,
            COUNT(DISTINCT contacts.email) AS contact_count
        FROM (
            SELECT
                atr.artist_id,
                CASE 
                    WHEN atr.optin_date IS NOT NULL THEN TO_DATE(atr.optin_date)
                    ELSE TO_DATE(atr.upload_date)
                END AS day,
                atr.email
            FROM fan_search.artist_contacts_batchview AS atr
            WHERE follower = FALSE
                AND email_user = TRUE
                AND bounced = FALSE
        ) AS contacts
        GROUP BY
            contacts.artist_id,
            contacts.day;
    """

def build_artist_nb_contacts_by_day_cumulative_table():
    return  """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_contacts_by_day_cumulative (
            artist_id INT,
            day STRING,
            contact_count INT
        )
        STORED AS PARQUET
        LOCATION '/bit_daily/artist_dashboard/artist_contacts_by_day_cumulative'
    """

def insert_overwrite_into_artist_nb_contacts_by_day_cumulative_table():
    return """
        INSERT OVERWRITE bit_daily_artist_dashboard.artist_nb_contacts_by_day_cumulative
        SELECT DISTINCT
            A.artist_id,
            A.day,
            SUM(A.contact_count) OVER (PARTITION BY A.artist_id ORDER BY A.day) AS contacts_count
        FROM (
            SELECT
                artist_id,
                day,
                contact_count
            FROM bit_daily_artist_dashboard.artist_nb_contacts_by_day
        ) A;
    """
##################################################################################################

def main():
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist Contacts')
    conf.set("spark.hive.exec.dynamic.partition", "true")
    conf.set("spark.hive.exec.dynamic.partition.mode", "nonstrict")
    conf.set("spark.hive.exec.max.dynamic.partitions", "100000")
    conf.set("spark.hive.exec.max.dynamic.partitions.pernode", "100000")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    year_month_day = sys.argv[1]
    """
        Creates a table that contains number of contacts gained for each day
    """
    spark.sql(build_artist_nb_contacts_by_day_table(year_month_day))
    spark.sql(insert_overwrite_into_artist_nb_contacts_by_day_table())

    """
        Creates a table that contains the accumilation of contacts for each day
    """
    spark.sql(build_artist_nb_contacts_by_day_cumulative_table())
    spark.sql(insert_overwrite_into_artist_nb_contacts_by_day_cumulative_table())

    df = spark.read.table("bit_daily_artist_dashboard.artist_nb_contacts_by_day_cumulative")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_contacts_by_day_records": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()
