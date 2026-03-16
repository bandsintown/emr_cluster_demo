import re
import unicodedata

from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    from_json,
    lit,
    regexp_replace,
    trim,
    udf,
    when,
)
from pyspark.sql.types import ArrayType, StringType, StructField, StructType

ARTISTS_BLOCKLIST = [
    657,  # Mika
]


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
    conf.setAppName("Qualified Artists for SEO")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    artists = spark.read.table("bit_daily_data_snapshot.public_artists")
    reviews_with_comments_df = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/sorted_reviews_with_comments"
    )
    reviews_with_media_df = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/sorted_reviews_with_media"
    )

    normalize_text = udf(strip_accents, StringType())
    slugify_text = udf(slugify, StringType())

    qualified_artists = (
        artists.filter(
            (col("tracker_count") > 100000)
            | ((col("tracker_count") >= 2000) & (col("nb_upcoming_events") > 0))
        )
        .filter((col("testing") == False) | (col("testing") == None))
        .filter(col("artist_id").isin(ARTISTS_BLOCKLIST) == False)
        .join(
            reviews_with_comments_df,
            artists.artist_id == reviews_with_comments_df.artist_id,
            "left_outer",
        )
        .join(
            reviews_with_media_df,
            artists.artist_id == reviews_with_media_df.artist_id,
            "left_outer",
        )
        .select(
            artists.artist_id.alias("id"),
            artists.name,
            artists.bio,
            when(artists.bio.isNotNull(), artists.bio)
            .otherwise(lit(""))
            .alias("formattedBio"),
            artists.genres,
            artists.hometown,
            artists.media_id.alias("mediaId"),
            artists.tracker_count.alias("trackerCount"),
            artists.verified,
            artists.is_dead.alias("dead"),
            slugify_text(artists.name).alias("nameSlug"),
            when(artists.nb_upcoming_events > 0, lit(True))
            .otherwise(lit(False))
            .alias("onTour"),
            from_json(
                artists.links,
                ArrayType(
                    StructType(
                        [
                            StructField("type", StringType()),
                            StructField("link", StringType()),
                        ]
                    )
                ),
            ).alias("links"),
            from_json(
                artists.members,
                ArrayType(StructType([StructField("name", StringType())])),
            ).alias("bandMembers"),
            when(
                slugify_text(artists.name).startswith("the-"),
                slugify_text(artists.name).substr(5, 1),
            )
            .otherwise(
                regexp_replace(
                    slugify_text(artists.name).substr(1, 1),
                    r"([^a-zA-Z])",
                    "#",
                )
            )
            .alias("nameFirstLetter"),
            reviews_with_comments_df.reviews.alias("reviewsWithComments"),
            reviews_with_media_df.reviews.alias("reviewsWithMedia"),
        )
    ).filter(trim("nameFirstLetter") != "")

    qualified_artists.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/qualified_artists"
    )

    artists_df = spark.read.parquet("s3a://bit-emr-cluster/dev/rene/qualified_artists")

    footer_artists = (
        artists_df.orderBy(artists_df.trackerCount.desc())
        .select(
            artists_df.id,
            artists_df.mediaId,
            artists_df.name,
            artists_df.nameFirstLetter,
            artists_df.nameSlug,
            artists_df.onTour,
        )
        .limit(60)
    )

    footer_artists.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/qualified_footer_artists"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()