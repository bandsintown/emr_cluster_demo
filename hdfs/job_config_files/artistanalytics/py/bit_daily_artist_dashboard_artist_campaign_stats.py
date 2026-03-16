import boto3
from dateutil.parser import parse
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import StringType, IntegerType
from pyspark.sql.functions import udf, sum as spark_sum, coalesce, lit, col

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)


def drop_hive_table():
    return """
        DROP TABLE IF EXISTS bit_daily_artist_dashboard.artist_campaign_stats
    """

def build_hive_table():
    query = """
        CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.artist_campaign_stats (
            artist_id INT,
            day STRING,
            message_uid STRING,
            campaign_name STRING,
            total_impressions INT,
            total_clicks INT,
            total_unique_impressions INT,
            total_unique_clicks INT,
            total_delivered_nb INT
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


def main():
    conf = SparkConf()
    conf.setAppName('BIT Daily Artist Dashboard Artist Campaign Stats By Day')
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    """UDFs"""
    ts_udf = udf(lambda z: convert_timestamp_to_date(z), StringType())
    
    spark.sql(build_hive_table())
    df = spark.read.table("bit_ptt.ptt_stats").select(
        "artist_id",
        "message_uid",
        "impressions_nb",
        "clicks_nb",
        "unique_impressions_nb",
        "unique_clicks_nb",
        "delivered_nb"
    )

    df_campaigns = spark.read.table("fan_search.artist_messages").select(
        "artist_id",
        "campaign_name",
        "message_uid",
        col("scheduled_at").alias("timestamp")
    ).filter(
        (col("message_status") == "sent") & (col("message_type") == "email_builder")
    )

    df = df.groupBy("artist_id", "message_uid")\
        .agg(
            spark_sum("impressions_nb").cast(IntegerType()).alias("total_impressions"),
            spark_sum("clicks_nb").cast(IntegerType()).alias("total_clicks"),
            spark_sum("unique_impressions_nb").cast(IntegerType()).alias("total_unique_impressions"),
            spark_sum("unique_clicks_nb").cast(IntegerType()).alias("total_unique_clicks"),
            spark_sum("delivered_nb").cast(IntegerType()).alias("total_delivered_nb")
        )

    df = df.join(df_campaigns, (df.artist_id == df_campaigns.artist_id) & (df.message_uid == df_campaigns.message_uid), "inner").select(
        df.artist_id,
        ts_udf(df_campaigns.timestamp).alias("day"),
        df.message_uid,
        df_campaigns.campaign_name,
        coalesce(df.total_impressions, lit(0)).alias("total_impressions"),
        coalesce(df.total_clicks, lit(0)).alias("total_clicks"),
        coalesce(df.total_unique_impressions, lit(0)).alias("total_unique_impressions"),
        coalesce(df.total_unique_clicks, lit(0)).alias("total_unique_clicks"),
        coalesce(df.total_delivered_nb, lit(0)).alias("total_delivered_nb")
    )

    record_count = df.count()
    output = "/bit_daily/artist_dashboard/artist_campaign_stats"
    df.write.mode("overwrite").parquet(output)

    spark.sql("""
        ALTER TABLE bit_daily_artist_dashboard.artist_campaign_stats 
        SET LOCATION '/bit_daily/artist_dashboard/artist_campaign_stats'
    """)
    """write to cloudwatch"""
    send_to_cloudwatch_metrics(
        {
            "bit_daily_artist_dashboard_artist_campaign_stats": record_count,
        }
    )

    spark.stop()
    exit()

if __name__ == "__main__":
    main()