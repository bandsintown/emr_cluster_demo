import requests
from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, SQLContext
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

username = "hadoop"
password = "Fh8Tec72"


def send(iterator):
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(
        [
            "cassandra1.prod.bandsintown.com",
            "cassandra2.prod.bandsintown.com",
            "cassandra3.prod.bandsintown.com",
        ],
        auth_provider=auth_provider,
    )

    session = cluster.connect("bands")
    docs = []
    for row in iterator:
        if row.artist_id is not None and row.artist_id > 0:
            doc = "INSERT INTO release_optin_user_locations_by_artist (artist_id, country, region_code, city, longitude, latitude, optin_count) VALUES ({}, {}, {}, {}, {}, {}, {});".format(
                row.artist_id,
                (
                    "''"
                    if row.country is None
                    else "'{}'".format(row.country.replace("'", "''"))
                ),
                (
                    "''"
                    if row.region_code is None
                    else "'{}'".format(row.region_code.replace("'", "''"))
                ),
                (
                    "''"
                    if row.city is None
                    else "'{}'".format(row.city.replace("'", "''"))
                ),
                "null" if row.longitude is None else row.longitude,
                "null" if row.latitude is None else row.latitude,
                row.optin_count,
            )
            docs.append(doc)
            if len(docs) >= 1000:
                session.execute(
                    """BEGIN BATCH
                {}
                APPLY BATCH;""".format(
                        "\n".join(docs)
                    ),
                    timeout=None,
                )
                docs = []
    if len(docs) > 0:
        session.execute(
            """BEGIN BATCH
            {}
            APPLY BATCH;""".format(
                "\n".join(docs)
            ),
            timeout=None,
        )


def send_v2(iterator):
    auth_provider = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster(
        [
            "cassandra1.prod.bandsintown.com",
            "cassandra2.prod.bandsintown.com",
            "cassandra3.prod.bandsintown.com",
        ],
        auth_provider=auth_provider,
    )

    session = cluster.connect("bands")
    docs = []
    for row in iterator:
        if row.artist_id is not None and row.artist_id > 0:
            doc = "INSERT INTO release_optin_user_locations_by_artist_by_type (artist_id, release_type, country, region_code, city, longitude, latitude, optin_count) VALUES ({}, {}, {}, {}, {}, {}, {}, {});".format(
                row.artist_id,
                "'{}'".format(row.release_type),
                (
                    "''"
                    if row.country is None
                    else "'{}'".format(row.country.replace("'", "''"))
                ),
                (
                    "''"
                    if row.region_code is None
                    else "'{}'".format(row.region_code.replace("'", "''"))
                ),
                (
                    "''"
                    if row.city is None
                    else "'{}'".format(row.city.replace("'", "''"))
                ),
                "null" if row.longitude is None else row.longitude,
                "null" if row.latitude is None else row.latitude,
                row.optin_count,
            )
            docs.append(doc)
            if len(docs) >= 1000:
                session.execute(
                    """BEGIN BATCH
                {}
                APPLY BATCH;""".format(
                        "\n".join(docs)
                    ),
                    timeout=None,
                )
                docs = []
    if len(docs) > 0:
        session.execute(
            """BEGIN BATCH
            {}
            APPLY BATCH;""".format(
                "\n".join(docs)
            ),
            timeout=None,
        )


def main():
    conf = SparkConf()
    conf.setAppName("Release Optin User Locations By Artist Indexations")

    conf.set("spark.executor.instances", "3")
    conf.set("spark.executor.cores", "3")
    conf.set("spark.executor.memory", "3g")
    conf.set("spark.driver.memory", "4g")
    conf.set("spark.dynamicAllocation.enabled", "false")
    # conf.set('spark.kryoserializer.buffer', '256m')
    # conf.set('spark.yarn.maxAppAttempts', '1')

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    df = spark.read.parquet(
        "/bit_daily/artist_dashboard/release_optin_user_locations_by_artist"
    )
    df.foreachPartition(send)

    df = spark.read.parquet(
        "/bit_daily/artist_dashboard/release_optin_user_locations_by_artist_by_type"
    )
    df.foreachPartition(send_v2)


if __name__ == "__main__":
    main()