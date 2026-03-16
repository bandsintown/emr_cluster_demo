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
def build_artist_nb_fans_by_day_table(year_month_day):
    return f"""
        CREATE TABLE IF NOT EXISTS bit_daily_shared.artist_nb_fans_by_day (
            artist_id INT,
            day STRING,
            tracker_count INT
        )
        LOCATION 's3a://bit-bigdata-daily-state-cycle/bit_daily_artist_dashboard/artist_followers_by_day'
    """

def insert_overwrite_into_artist_nb_fans_by_day_table():
    return """
        INSERT OVERWRITE bit_daily_shared.artist_nb_fans_by_day
        SELECT
            atr.artist_id,
            TO_DATE(regexp_replace(regexp_replace(atr.created_at,'Z',''),'T',' ')),
            COUNT(DISTINCT atr.user_id) AS tracker_count
        FROM fan_search.tracked_artists AS atr
        WHERE atr.tracked=true
        GROUP BY
            atr.artist_id,
            TO_DATE(regexp_replace(regexp_replace(atr.created_at,'Z',''),'T',' '));
    """

def build_artist_nb_fans_by_day_cumulative_table():
    return  """
        CREATE TABLE IF NOT EXISTS bit_daily_shared.artist_nb_fans_by_day_cumulative (
            artist_id INT,
            `date` STRING,
            cnt INT
        )
        LOCATION '/bit_daily/shared/artistfansbydaycumulative'
    """

def insert_overwrite_into_artist_nb_fans_by_day_cumulative_table():
    return """
        INSERT OVERWRITE bit_daily_shared.artist_nb_fans_by_day_cumulative
        SELECT
            A.artist_id,
            A.`date`,
            SUM(A.cnt) OVER (PARTITION BY A.artist_id ORDER BY A.`date`) AS cnt
        FROM (
            SELECT
                artist_id,
                day AS `date`,
                tracker_count AS CNT
            FROM bit_daily_shared.artist_nb_fans_by_day
        ) A;
    """

def build_dashboard_artist_nb_fans_by_day_cumulative_table():
    return  """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_nb_fans_by_day_cumulative (
            artist_id INT,
            `date` STRING,
            cnt INT
        )
        LOCATION '/bit_daily/artist_dashboard/artistfansbydaycumulative'
    """

def insert_overwrite_into_dashboard_artist_nb_fans_by_day_cumulative_table():
    return """
        INSERT OVERWRITE bit_daily_artist_dashboard.artist_nb_fans_by_day_cumulative
        SELECT fanbyday.*
        FROM bit_daily_shared.artist_nb_fans_by_day_cumulative fanbyday
        JOIN bit_daily_data_snapshot.public_artists d
            ON (d.artist_id= fanbyday.artist_id)
        WHERE (d.tracker_count>1000 OR (d.tracker_count>100 AND d.managed=1));
    """
##################################################################################################

def main():
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist Followers')
    conf.set("spark.hive.exec.dynamic.partition", "true")
    conf.set("spark.hive.exec.dynamic.partition.mode", "nonstrict")
    conf.set("spark.hive.exec.max.dynamic.partitions", "100000")
    conf.set("spark.hive.exec.max.dynamic.partitions.pernode", "100000")
    year_month_day = sys.argv[1]
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    
    """
        Creates a table that contains number of followers gained for each day
    """
    spark.sql(build_artist_nb_fans_by_day_table(year_month_day))
    spark.sql(insert_overwrite_into_artist_nb_fans_by_day_table())

    """
        Creates a table that contains the accumilation of followers for each day
    """
    spark.sql(build_artist_nb_fans_by_day_cumulative_table())
    spark.sql(insert_overwrite_into_artist_nb_fans_by_day_cumulative_table())

    """
        Same as the accumilation table above but also has a filter based on tracker count
    """
    spark.sql(build_dashboard_artist_nb_fans_by_day_cumulative_table())
    spark.sql(insert_overwrite_into_dashboard_artist_nb_fans_by_day_cumulative_table())

    df = spark.read.table("bit_daily_artist_dashboard.artist_nb_fans_by_day_cumulative")
    record_count = df.count()

    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_followers_by_day_records": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()
