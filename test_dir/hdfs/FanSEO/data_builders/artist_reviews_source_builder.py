from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    lower,
    lit,
    collect_list,
    trim,
    struct,
    when,
    concat,
    udf,
    size,
    split,
    row_number,
    max,
    to_date,
    date_format,
)
from pyspark.sql.window import Window
from pyspark.sql.types import (
    StringType,
    IntegerType,
)

import unicodedata
import re

ARCHIVE_ACTIONS = ["delete", "deleted", "merged", "FLAGGED", "BLACKLISTED"]


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
    conf.setAppName("Artist Reviews for SEO")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    slugify_text = udf(slugify, StringType())

    events_df = spark.read.table("fan_search.events")

    users_df = spark.read.table("fan_search.users").select(
        "id",
        "first_name",
        "display_name",
        "media_id",
        when(
            lower(trim(col("location")["country"])).isin(
                "united states", "united states of america", "us", "usa"
            ),
            when(
                (
                    (col("location")["city"].isNotNull())
                    & (col("location")["region"].isNotNull())
                ),
                concat(col("location")["city"], lit(", "), col("location")["region"]),
            ).otherwise(col("location")["country"]),
        )
        .otherwise(
            when(
                (
                    (col("location")["city"].isNotNull())
                    & (col("location")["region"].isNotNull())
                ),
                concat(col("location")["city"], lit(", "), col("location")["region"]),
            ).otherwise(lit(None))
        )
        .cast(StringType())
        .alias("location"),
    )

    event_reviews_df = (
        spark.read.table("fan_search.event_reviews")
        .filter(~col("action").isin(ARCHIVE_ACTIONS))
        .withColumn(
            "comment_word_count",
            when(
                (col("comment").isNotNull()) & (col("rating") >= 3),
                size(split(trim(col("comment")), " ")),
            )
            .otherwise(lit(None))
            .cast(IntegerType()),
        )
    )

    review_comment_word_count_win = Window.partitionBy(col("artist_id")).orderBy(
        col("comment_word_count").desc()
    )
    review_timestamp_win = Window.partitionBy(col("artist_id")).orderBy(
        col("timestamp").desc()
    )

    event_reviews_df.filter(event_reviews_df.rating >= 3).join(
        events_df, event_reviews_df.event_id == events_df.event_id, "inner"
    ).select(
        events_df.artist_id,
        events_df.venue_id,
        events_df.venue_name,
        events_df.venue_location,
        event_reviews_df.comment_word_count,
        event_reviews_df.rating,
        event_reviews_df.comment,
        event_reviews_df.media_id,
        event_reviews_df.user_id,
        event_reviews_df.timestamp,
    ).write.mode(
        "overwrite"
    ).parquet(
        "s3a://bit-emr-cluster/dev/rene/events_with_reviews"
    )

    events_with_reviews = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/events_with_reviews"
    )

    # Sort reviews by `comment_word_count` and output to dataframe
    events_with_reviews.withColumn(
        "comment_word_count_order_desc",
        row_number().over(review_comment_word_count_win),
    ).filter(col("comment_word_count") > 0).filter(
        col("comment_word_count_order_desc") >= 10
    ).join(
        users_df, events_with_reviews.user_id == users_df.id, "inner"
    ).select(
        events_with_reviews.artist_id,
        events_with_reviews.comment_word_count,
        struct(
            events_with_reviews.venue_id.alias("venueId"),
            events_with_reviews.venue_name.alias("venueName"),
            events_with_reviews.venue_location.alias("venueLocation"),
            events_with_reviews.rating.cast(IntegerType()).alias("rating"),
            events_with_reviews.comment,
            events_with_reviews.timestamp,
            date_format(to_date(events_with_reviews.timestamp), "MMM dd, yyyy").alias(
                "date"
            ),
            slugify_text(events_with_reviews.venue_name).alias("venueNameSlug"),
            slugify_text(events_with_reviews.venue_location).alias("venueLocationSlug"),
            when(trim(users_df.first_name) == "", lit(None))
            .otherwise(trim(users_df.first_name))
            .cast(StringType())
            .alias("userFirstName"),
            when(trim(users_df.display_name) == "", lit(None))
            .otherwise(trim(users_df.display_name))
            .cast(StringType())
            .alias("userDisplayName"),
            users_df.media_id.alias("userMediaId"),
            users_df.location.alias("userLocation"),
        ).alias("review"),
    ).write.mode(
        "overwrite"
    ).parquet(
        "s3a://bit-emr-cluster/dev/rene/reviews_with_comments"
    )

    # Sort reviews by timestamp and output
    events_with_reviews.withColumn(
        "timestamp_order_desc", row_number().over(review_timestamp_win)
    ).filter(events_with_reviews.media_id.isNotNull()).filter(
        col("timestamp_order_desc") >= 10
    ).select(
        events_with_reviews.artist_id,
        events_with_reviews.timestamp,
        struct(events_with_reviews.media_id.alias("mediaId")).alias("review"),
    ).write.mode(
        "overwrite"
    ).parquet(
        "s3a://bit-emr-cluster/dev/rene/reviews_with_media"
    )

    reviews_with_comments = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/reviews_with_comments"
    )
    reviews_with_media = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/reviews_with_media"
    )

    reviews_with_comments.withColumn(
        "reviews", collect_list("review").over(review_comment_word_count_win)
    ).groupBy("artist_id").agg(max("reviews").alias("reviews")).write.mode(
        "overwrite"
    ).parquet(
        "s3a://bit-emr-cluster/dev/rene/sorted_reviews_with_comments"
    )

    reviews_with_media.withColumn(
        "reviews", collect_list("review").over(review_timestamp_win)
    ).groupBy("artist_id").agg(max("reviews").alias("reviews")).write.mode(
        "overwrite"
    ).parquet(
        "s3a://bit-emr-cluster/dev/rene/sorted_reviews_with_media"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()