from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.types import StringType
from pyspark.sql.functions import (
    struct,
)
import unicodedata
import re


def main():
    conf = SparkConf()
    conf.setAppName("Artist Upcoming Events")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    qualified_artists = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/qualified_artists"
    )

    similar_artists = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/similar_artists"
    )
    grouped_events = spark.read.parquet("s3a://bit-emr-cluster/dev/rene/grouped_events")

    artist_pages_data = (
        qualified_artists.join(
            grouped_events,
            qualified_artists.id == grouped_events.artist_id,
            "left_outer",
        )
        .join(
            similar_artists,
            qualified_artists.id == similar_artists.artist_id,
            "left_outer",
        )
        .select(
            qualified_artists.id.alias("artistId"),
            grouped_events.events,
            grouped_events.events_by_year.alias("eventsByYear"),
            qualified_artists.reviewsWithComments,
            qualified_artists.reviewsWithMedia,
            similar_artists.similarArtists,
            struct(
                qualified_artists.bandMembers,
                qualified_artists.bio,
                qualified_artists.formattedBio,
                qualified_artists.genres,
                qualified_artists.hometown,
                qualified_artists.id,
                qualified_artists.links,
                qualified_artists.mediaId,
                qualified_artists.name,
                qualified_artists.nameFirstLetter,
                qualified_artists.nameSlug,
                qualified_artists.onTour,
                qualified_artists.trackerCount,
                qualified_artists.verified,
                qualified_artists.dead,
            ).alias("artist"),
        )
    )

    artist_pages_data.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/artist_pages_data"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()