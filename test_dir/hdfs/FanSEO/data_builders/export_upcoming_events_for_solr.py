from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import explode, concat, col, lit

EVENTS_PARQUET_PATH = "s3a://bit-emr-cluster/dev/rene/grouped_events"


def main():
    """
    Build the Parquet file to be indexed into Solr with the FanSEOCityPagesWorkflow.
    Writes to `s3a://bit-emr-cluster/dev/rene/events`.

    Depends on the `s3a://bit-emr-cluster/dev/rene/grouped_events` data.
    This is created with the
    `/hdfs/FanSEO/data_builders/upcoming_events_source_builder.py` via the
    FanSEOWorkflow
    """
    conf = SparkConf()
    conf.setAppName("Fan SEO Upcoming Events for Solr")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    events_df = spark.read.parquet(EVENTS_PARQUET_PATH)
    exploded_events = (
        events_df.select(explode(events_df.events).alias("events"))
        .select(
            "events.id",
            "events.title",
            "events.mediaId",
            "events.numCollectedTickets",
            "events.streamingEvent",
            "events.rsvpCount",
            "events.announcedAt",
            "events.startsAt",
            "events.endsAt",
            "events.day",
            "events.month",
            "events.year",
            "events.date",
            "events.artistId",
            "events.artistMediaId",
            "events.artistName",
            "events.artistNameSlug",
            "events.artistNameFirstLetter",
            "events.artistGenres",
            "events.artistOnTour",
            "events.artistTrackerCount",
            "events.venueName",
            "events.city",
            "events.venueCountry",
            "events.latitude",
            "events.longitude",
            "events.streetAddress",
            "events.venueAddress",
            "events.venueRegion",
            "events.venueLocation",
            "events.venueLocationSlug",
            "events.postalCode",
            "events.region",
        )
        .withColumn("latlong", concat(col("latitude"), lit(","), col("longitude")))
    )

    exploded_events.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/events"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()