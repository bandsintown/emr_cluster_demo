from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    max,
    row_number,
    struct,
    collect_list,
)
from pyspark.sql.window import Window


def main():
    conf = SparkConf()
    conf.setAppName("Similar Artists for SEO")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    qualified_artists = spark.read.parquet(
        "s3a://bit-emr-cluster/dev/rene/qualified_artists"
    )
    sims_df = spark.read.table("bit_artist_recommendations.similar_artists_batch")

    sims_on_tour = sims_df.filter(sims_df.sim_on_tour == True)
    rank_window = Window.partitionBy(col("artist_id")).orderBy(col("rank").asc())

    similar_artists = (
        sims_on_tour.withColumn("rank_asc", row_number().over(rank_window))
        .filter(col("rank_asc") <= 12)
        .join(qualified_artists, sims_df.sim_artist_id == qualified_artists.id)
        .select(
            sims_df.artist_id,
            sims_df.rank,
            struct(
                sims_df.sim_artist_id.alias("id"),
                sims_df.rank,
                qualified_artists.name,
                qualified_artists.mediaId,
                qualified_artists.nameSlug,
                qualified_artists.nameFirstLetter,
            ).alias("similarArtist"),
        )
    )

    similar_artists.withColumn(
        "similarArtists", collect_list("similarArtist").over(rank_window)
    ).groupBy("artist_id").agg(
        max("similarArtists").alias("similarArtists")
    ).write.mode(
        "overwrite"
    ).parquet(
        "s3a://bit-emr-cluster/dev/rene/similar_artists"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()