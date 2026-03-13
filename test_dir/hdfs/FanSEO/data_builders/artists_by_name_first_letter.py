from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    struct,
    collect_set,
)
from pyspark.sql.types import StringType
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
    conf.setAppName("Artist Name Groups")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    qualified_artists = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/qualified_artists"
    )

    artist_groups = (
        (
            qualified_artists.select(
                struct(
                    qualified_artists.id,
                    qualified_artists.name,
                    qualified_artists.nameSlug,
                    qualified_artists.nameFirstLetter,
                ).alias("artist")
            )
        )
        .groupBy("artist.nameFirstLetter")
        .agg(collect_set("artist").alias("artists"))
    )

    artist_groups.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/artists_by_name_first_letter"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()