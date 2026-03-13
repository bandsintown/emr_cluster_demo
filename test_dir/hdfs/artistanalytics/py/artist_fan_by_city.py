from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import StructField, StructType, StringType, FloatType
from pyspark.sql.functions import col,coalesce,broadcast

def main():
    conf = SparkConf()
    conf.setAppName('Artist Fans By City')
    conf.set("spark.executor.cores", "2")
    conf.set("spark.executor.memory", "8g")
    conf.set("spark.yarn.executor.memoryOverhead","3500")
    # conf.set("spark.submit.deployMode", "cluster")
    conf.set("spark.yarn.am.waitTime", "900s")
    conf.set("spark.sql.shuffle.partitions", "300")
    conf.set("spark.default.parallelism", "300")
    # conf.set("hive.metastore.uris",
    #          "thrift://ip-172-30-61-37.ec2.internal:9083")
    # conf.set("spark.sql.warehouse.dir", "/user/hive/warehouse")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    normalization_schema = StructType([
        StructField('city', StringType()),
        StructField('region_code', StringType()),
        StructField('country', StringType()),
        StructField('latitude', FloatType()),
        StructField('longitude', FloatType())
    ])

    spark.read.table('fan_search.users_popular_location').select(
        'user_id',
        coalesce(col('popular_location'), col('location')).cast(normalization_schema).alias('location')
    ).createOrReplaceTempView("users_popular_location")

    spark.sql("select user_id,location.city,location.region_code,location.country,location.latitude,location.longitude  from users_popular_location  cluster by user_id"
             ).createOrReplaceTempView("users_last_known_location")

    spark.sql("select * From fan_search.tracked_artists where tracked cluster by user_id"
             ).createOrReplaceTempView("artist_tracking")

    df_big_artists = spark.sql("""
        SELECT 
            a.artist_id, 
            a.artist_name 
        FROM bit_daily_artist_dashboard.artist_list a 
        CLUSTER BY a.artist_id
    
    """)



    spark.sql("""select u.city,u.region_code,u.country,u.latitude,u.longitude,u.user_id,t.artist_id
                 from  artist_tracking t join users_last_known_location u on t.user_id = u.user_id
                 cluster by u.city,u.region_code,u.country,u.latitude,u.longitude"""
             ).createOrReplaceTempView("artist_tracking_raw")



    df_artist_tracking_by_city = spark.sql("""select city,region_code,country,latitude,longitude,artist_id, count(distinct user_id) cnt
                 from  artist_tracking_raw t
                 group by city,region_code,country,latitude,longitude,artist_id"""
             )

    df_artist_tracking_by_city.alias('u').join(
        df_big_artists.alias('a'),
        col("a.artist_id") == col("u.artist_id")
    ).select([
        "a.artist_id",
        "a.artist_name",
        "u.country",
        "u.region_code",
        "u.city",
        "u.longitude",
        "u.latitude",
        "u.cnt"
    ]).write.mode("overwrite").option("delimiter", "\u0001").option("header", "false").csv('/bit_weekly/artist_dashboard/artistfansbycity/')



if __name__ == "__main__":
    main()
