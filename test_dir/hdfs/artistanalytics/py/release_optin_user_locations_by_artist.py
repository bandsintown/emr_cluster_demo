from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import StructField, StructType, StringType, FloatType
from pyspark.sql.functions import col, coalesce

ARCHIVE_ACTIONS = ["deleted", "merged"]


def main():
    conf = SparkConf()
    conf.setAppName("Release Optin User Locations By Artist")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    normalization_schema = StructType(
        [
            StructField("city", StringType()),
            StructField("region_code", StringType()),
            StructField("country", StringType()),
            StructField("latitude", FloatType()),
            StructField("longitude", FloatType()),
        ]
    )

    spark.read.table("fan_search.users_popular_location").select(
        "user_id",
        coalesce(col("popular_location"), col("location"))
        .cast(normalization_schema)
        .alias("location"),
    ).createOrReplaceTempView("users_popular_location")

    spark.sql(
        """
        SELECT
            user_id,
            location.city,
            location.region_code,
            location.country,
            location.latitude,
            location.longitude
        FROM users_popular_location
        CLUSTER BY user_id
    """
    ).createOrReplaceTempView("users_last_known_location")

    spark.sql(
        """
        SELECT *
        FROM fan_search.artist_release_optins
        WHERE action NOT IN ('deleted', 'merged')
        CLUSTER BY user_id
    """
    ).createOrReplaceTempView("release_optins")

    spark.sql(
        """
        SELECT
            o.user_id,
            o.artist_id,
            coalesce(r.release_type, 'default') AS release_type
        FROM fan_search.artist_release_optins o
        JOIN fan_search.artist_releases r ON o.release_id = r.release_id
        WHERE action NOT IN ('deleted', 'merged')
        CLUSTER BY user_id
    """
    ).createOrReplaceTempView("release_type_optins")

    df_ba = spark.sql(
        """
        SELECT
            a.artist_id,
            a.artist_name
        FROM bit_daily_artist_dashboard.artist_list a
        CLUSTER BY a.artist_id
    """
    )

    spark.sql(
        """
        SELECT
            u.city,
            u.region_code,
            u.country,
            u.latitude,
            u.longitude,
            u.user_id,
            t.artist_id
        FROM release_optins  t
        JOIN users_last_known_location u
            ON t.user_id = u.user_id
        CLUSTER BY
            u.city,
            u.region_code,
            u.country,
            u.latitude,
            u.longitude
    """
    ).createOrReplaceTempView("release_optins_raw")

    spark.sql(
        """
        SELECT
            u.city,
            u.region_code,
            u.country,
            u.latitude,
            u.longitude,
            u.user_id,
            t.release_type,
            t.artist_id
        FROM release_type_optins  t
        JOIN users_last_known_location u
            ON t.user_id = u.user_id
        CLUSTER BY
            u.city,
            u.region_code,
            u.country,
            u.latitude,
            u.longitude
    """
    ).createOrReplaceTempView("release_type_optins_raw")

    df_tbc = spark.sql(
        """
        SELECT
            city,
            region_code,
            country,
            latitude,
            longitude,
            artist_id,
            count(distinct user_id) optin_count
        FROM release_optins_raw t
        GROUP BY
            city,
            region_code,
            country,
            latitude,
            longitude,
            artist_id
    """
    )

    df_tbc.join(df_ba, df_ba.artist_id == df_tbc.artist_id).select(
        df_ba.artist_id,
        df_tbc.country,
        df_tbc.region_code,
        df_tbc.city,
        df_tbc.longitude,
        df_tbc.latitude,
        df_tbc.optin_count,
    ).write.mode("overwrite").parquet(
        "/bit_daily/artist_dashboard/release_optin_user_locations_by_artist"
    )

    df_tbc = spark.sql(
        """
        SELECT
            city,
            region_code,
            country,
            latitude,
            longitude,
            release_type,
            artist_id,
            count(distinct user_id) optin_count
        FROM release_type_optins_raw t
        GROUP BY
            city,
            region_code,
            country,
            latitude,
            longitude,
            release_type,
            artist_id
    """
    )

    df_tbc.join(df_ba, df_ba.artist_id == df_tbc.artist_id).select(
        df_ba.artist_id,
        df_tbc.country,
        df_tbc.region_code,
        df_tbc.city,
        df_tbc.longitude,
        df_tbc.latitude,
        df_tbc.release_type,
        df_tbc.optin_count,
    ).write.mode("overwrite").parquet(
        "/bit_daily/artist_dashboard/release_optin_user_locations_by_artist_by_type"
    )


if __name__ == "__main__":
    main()