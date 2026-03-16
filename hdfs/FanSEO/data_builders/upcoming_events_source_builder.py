from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from pyspark.sql.functions import (
    col,
    struct,
    collect_set,
    udf,
    to_date,
    expr,
    date_format,
    lit,
    when,
    collect_list,
    flatten,
    trim,
    to_timestamp,
    regexp_replace,
    lower,
)
import unicodedata
import re


def strip_accents(text):
    if not text:
        return text
    normalized_text = "".join(
        char
        for char in unicodedata.normalize("NFKD", text)
        if unicodedata.category(char) != "Mn"
    )
    if not str(normalized_text).strip():
        normalized_text = text
    return str(normalized_text).strip().lower()


def slugify(string):
    if not string:
        return string

    text_to_slugify = strip_accents(string).lower()
    separator = "-"
    re_duplicate_separator = r"-{2,}"
    re_leading_trailing_separator = r"^-|-$"

    text_to_slugify = re.sub(
        r"[^a-z0-9\-_]+", separator, text_to_slugify, flags=re.IGNORECASE
    )
    text_to_slugify = re.sub(
        re_duplicate_separator, separator, text_to_slugify, flags=re.IGNORECASE
    )
    text_to_slugify = re.sub(
        re_leading_trailing_separator, "", text_to_slugify, flags=re.IGNORECASE
    )

    return text_to_slugify


def main():
    conf = SparkConf()
    conf.setAppName("Upcoming Events Grouped by Artist")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    normalize_text = udf(strip_accents, StringType())
    slugify_text = udf(slugify, StringType())

    events = spark.read.table("bit_daily_data_snapshot.events_batch")

    grouped_events = (
        events.withColumn(
            "computedEndsAt",
            date_format(
                to_timestamp(events.starts_at + expr("INTERVAL 3 HOURS")),
                "yyyy-MM-dd'T'HH:mm:ss'Z'",
            ),
        )
        .select(
            events.artist_id,
            struct(
                events.artist_event_int_id.alias("id"),
                events.title,
                events.media_id.alias("mediaId"),
                events.num_collected_tickets.alias("numCollectedTickets"),
                events.streaming_event.alias("streamingEvent"),
                events.rsvp_count.alias("rsvpCount"),
                events.announcement_date_time.alias("announcedAt"),
                events.starts_at.alias("startsAt"),
                when(events.ends_at.isNull(), col("computedEndsAt"))
                .otherwise(events.ends_at)
                .alias("endsAt"),
                date_format(to_date(events.starts_at), "dd").alias("day"),
                date_format(to_date(events.starts_at), "MMM").alias("month"),
                date_format(to_date(events.starts_at), "yyyy").alias("year"),
                date_format(to_date(events.starts_at), "MMM dd, yyyy").alias("date"),
                events.artist_id.alias("artistId"),
                events.artist_media_id.alias("artistMediaId"),
                events.artist_name.alias("artistName"),
                slugify_text(col("artist_name")).alias("artistNameSlug"),
                when(
                    slugify_text(col("artist_name")).startswith("the-"),
                    slugify_text(col("artist_name")).substr(5, 1),
                )
                .otherwise(
                    regexp_replace(
                        slugify_text(col("artist_name")).substr(1, 1),
                        r"([^a-zA-Z])",
                        "#",
                    )
                )
                .alias("artistNameFirstLetter"),
                events.artist_genres.alias("artistGenres"),
                events.artist_on_tour.alias("artistOnTour"),
                events.artist_tracker_count.alias("artistTrackerCount"),
                events.venue_name.alias("venueName"),
                events.venue_city.alias("city"),
                events.venue_country.alias("venueCountry"),
                events.venue_latitude.alias("latitude"),
                events.venue_longitude.alias("longitude"),
                events.venue_address.alias("streetAddress"),
                events.venue_address.alias("venueAddress"),
                events.venue_region.alias("venueRegion"),
                events.venue_location.alias("venueLocation"),
                slugify_text(col("venue_location")).alias("venueLocationSlug"),
                events.venue_postal_code.alias("postalCode"),
                when(
                    (
                        (trim(events.venue_region) == "")
                        | (trim(events.venue_region) == "null")
                        | (trim(events.venue_region) == "non")
                    ),
                    when(trim(events.venue_country) == "", lit(None)).otherwise(
                        events.venue_country
                    ),
                )
                .otherwise(events.venue_region)
                .alias("region"),
            ).alias("event_info"),
        )
        .withColumn("event_year", col("event_info.year"))
        .groupBy("artist_id", "event_year")
        .agg(collect_set("event_info").alias("events"))
        .groupBy("artist_id")
        .agg(
            collect_list(struct("event_year", "events")).alias("events_by_year"),
            flatten(collect_set("events")).alias("events"),
        )
    )

    grouped_events.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/grouped_events"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()