import sys
from datetime import datetime, timedelta
from urllib.parse import urlparse
from pyspark.sql import SparkSession
from pyspark.conf import SparkConf
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
)
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    row_number,
    col,
    udf,
    unix_timestamp,
    count,
)


FIREHOSE_PATH = (
    "s3a://bit-data-firehose/fan-integration-hub-integrator/v1/processed-events"
)
SNAPSHOT_TABLE = "fan_integration_hub.processed_events_v1"
SNAPSHOT_TABLE_PATH = (
    "s3a://bit-master-dataset-backup/fan_integration_hub/processed_events_v1/"
)


INPUT_SCHEMA = StructType(
    [
        StructField(
            "payload",
            StructType(
                [
                    StructField(
                        "artist_optin",
                        StructType(
                            [
                                StructField("artist_id", IntegerType()),
                                StructField("artist_name", StringType()),
                                StructField("email", StringType()),
                                StructField("fan_id", IntegerType()),
                                StructField(
                                    "location",
                                    StructType(
                                        [
                                            StructField("city", StringType()),
                                            StructField("country", StringType()),
                                            StructField("region", StringType()),
                                        ]
                                    ),
                                ),
                                StructField("opt_in_timestamp", StringType()),
                                StructField("phone", StringType()),
                                StructField(
                                    "utm",
                                    StructType(
                                        [
                                            StructField("campaign", StringType()),
                                            StructField("medium", StringType()),
                                            StructField("source", StringType()),
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    StructField(
                        "event", StructType([StructField("id", IntegerType())])
                    ),
                ]
            ),
        ),
        StructField("status", StringType()),
        StructField("status_code", IntegerType()),
        StructField("webhook_url", StringType()),
        StructField("version", StringType()),
        StructField("nonce", StringType()),
        StructField("timestamp", StringType()),
    ]
)


def create_snapshot_table():
    sql = f"""
    CREATE EXTERNAL TABLE IF NOT EXISTS {SNAPSHOT_TABLE} (
        artist_id int,
        artist_name string,
        email string,
        fan_id int,
        location_city string,
        location_country string,
        location_region string,
        opt_in_timestamp string,
        phone string,
        utm_campaign string,
        utm_medium string,
        utm_source string,
        event_id int,
        status string,
        status_code int,
        webhook_url string,
        version string,
        nonce string,
        partner_company string,
        timestamp string,
        latency_ms long,
        attempt_number int,
        total_attempts int
    )
    PARTITIONED BY (ds string)
    STORED AS PARQUET
    LOCATION '{SNAPSHOT_TABLE_PATH}';
    """
    return sql


def file_exists(path):
    try:
        rdd = sc.textFile(path)
        rdd.take(1)
        return True
    except Exception:
        return False


def get_firehose_paths(days):
    files = []
    current_time = datetime.utcnow()
    for day in range(0, days):
        date = current_time - timedelta(days=day)
        path = f'{FIREHOSE_PATH}/{date.strftime("%Y")}/{date.strftime("%m")}/{date.strftime("%d")}/*/*'
        if file_exists(path):
            files.append(path)
    return files


@udf(StringType())
def get_host(url):
    if url:
        return urlparse(url).netloc
    return None


def read_new_data_from_firehose(days_past):
    files = get_firehose_paths(days_past)

    new_data = (
        spark.read.schema(INPUT_SCHEMA)
        .json(files)
        .filter(col("payload").isNotNull())
        .select(
            col("payload.artist_optin.artist_id").alias("artist_id"),
            col("payload.artist_optin.artist_name").alias("artist_name"),
            col("payload.artist_optin.email").alias("email"),
            col("payload.artist_optin.fan_id").alias("fan_id"),
            col("payload.artist_optin.location.city").alias("location_city"),
            col("payload.artist_optin.location.country").alias("location_country"),
            col("payload.artist_optin.location.region").alias("location_region"),
            col("payload.artist_optin.opt_in_timestamp").alias("opt_in_timestamp"),
            col("payload.artist_optin.phone").alias("phone"),
            col("payload.artist_optin.utm.campaign").alias("utm_campaign"),
            col("payload.artist_optin.utm.medium").alias("utm_medium"),
            col("payload.artist_optin.utm.source").alias("utm_source"),
            col("payload.event.id").alias("event_id"),
            col("status").alias("status"),
            col("status_code").alias("status_code"),
            col("webhook_url").alias("webhook_url"),
            col("version").alias("version"),
            col("nonce").alias("nonce"),
            get_host(col("webhook_url")).alias("partner_company"),
            col("timestamp").alias("timestamp"),
        )
        .withColumn(
            "latency_ms",
            (
                unix_timestamp(col("timestamp"), "yyyy-MM-dd'T'HH:mm:ssZ")
                - unix_timestamp(col("opt_in_timestamp"), "yyyy-MM-dd'T'HH:mm:ssZ")
            )
            * 1000,
        )
        .withColumn("ds", col("opt_in_timestamp").substr(1, 10))
    )

    return new_data


def main(spark, days_past):
    spark.sql(create_snapshot_table())

    days_extend_past = days_past + 5
    new_data = read_new_data_from_firehose(days_past)

    days_extend = (datetime.utcnow() - timedelta(days=days_extend_past)).strftime(
        "%Y-%m-%d"
    )
    spark.sql(f"REFRESH TABLE {SNAPSHOT_TABLE}")
    current_snapshot = (
        spark.read.table(SNAPSHOT_TABLE)
        .filter(f"ds >= '{days_extend}'")
        .select(
            "artist_id",
            "artist_name",
            "email",
            "fan_id",
            "location_city",
            "location_country",
            "location_region",
            "opt_in_timestamp",
            "phone",
            "utm_campaign",
            "utm_medium",
            "utm_source",
            "event_id",
            "status",
            "status_code",
            "webhook_url",
            "version",
            "nonce",
            "partner_company",
            "timestamp",
            "latency_ms",
            "ds",
        )
    )

    last_added = Window.partitionBy("nonce").orderBy(col("timestamp").desc())

    attempts = Window.partitionBy("artist_id", "fan_id", "opt_in_timestamp").orderBy(
        col("timestamp").asc()
    )

    new_snapshot = (
        (
            current_snapshot.union(new_data)
            .withColumn("row_number", row_number().over(last_added))
            .filter("row_number = 1")
            .drop("row_number")
        )
        .withColumn("attempt_number", row_number().over(attempts))
        .withColumn(
            "total_attempts",
            count("*").over(
                attempts.rowsBetween(
                    Window.unboundedPreceding, Window.unboundedFollowing
                )
            ),
        )
    )

    all_dates = new_snapshot.select("ds").distinct().collect()
    dates_out = [d["ds"] for d in all_dates]

    new_snapshot.write.mode("overwrite").partitionBy("ds").parquet(SNAPSHOT_TABLE_PATH)

    spark.sql(f"REFRESH TABLE {SNAPSHOT_TABLE}")
    for d in dates_out:
        spark.sql(
            f"""
        ALTER TABLE {SNAPSHOT_TABLE} ADD IF NOT EXISTS PARTITION (ds='{d}') LOCATION '{SNAPSHOT_TABLE_PATH}ds={d}'
        """
        )
    spark.sql(f"REFRESH TABLE {SNAPSHOT_TABLE}")

    spark.stop()
    sys.exit()


if __name__ == "__main__":
    conf = SparkConf()
    conf.setAppName("Fan Integration Hub Processed Events V1 Snapshot")
    conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext

    days_past = int(sys.argv[1])

    main(spark, days_past)
