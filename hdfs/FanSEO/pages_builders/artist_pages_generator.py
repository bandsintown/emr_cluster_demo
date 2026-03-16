import boto3

from pyspark import SparkFiles
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import col
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    ArrayType,
    DateType,
    BooleanType,
    DoubleType,
    FloatType,
)


REGION_NAME = "us-east-1"
S3_BUCKET = "concerts.hypebot.com"


class ForeachWriter:
    def __init__(self, footer_artists, footer_cities, popular_cities):
        self.footer_artists = footer_artists
        self.footer_cities = footer_cities
        self.popular_cities = popular_cities

    def open(self, partition_id, epoch_id):
        session = boto3.Session(region_name=REGION_NAME)
        self.s3_client = session.resource("s3")
        return True

    def process(self, row):
        html_template = jinja_env.get_template("artist/artistPage.njk")
        page_context = context_builder(row)
        page_context["footerArtists"] = self.footer_artists
        page_context["footerCities"] = self.footer_cities
        page_context["venue"] = None

        tour_cities = page_context["tourCities"]
        page_context["tourCities"] = self.compact_tour_cities(tour_cities)
        rendered = html_template.render(page_context)

        s3_path = "latest/artist"
        slug = f"{row.artistId}-{row.artist.nameSlug}"
        self.upload_to_s3(f"{s3_path}/{row.artist.nameFirstLetter}/{slug}", rendered)

    def compact_tour_cities(self, tour_cities):
        filtered_tour_cities = map(
            lambda city: city if Row(city["nameSlug"]) in self.popular_cities else None,
            tour_cities,
        )

        return list(filter(None, filtered_tour_cities))

    def close(self, error):
        if error:
            raise error

    def upload_to_s3(self, path, body):
        self.s3_client.Object(S3_BUCKET, path).put(Body=body, ContentType="text/html")


def main():
    global jinja_env, artist_page_template, context_builder
    conf = SparkConf()
    conf.setAppName("Fan SEO template generation")

    conf.set("spark.dynamicAllocation.enabled", "false")
    conf.set("spark.executor.cores", "1")
    conf.set("spark.executor.instances", "1")
    conf.set("spark.executor.memory", "1g")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    sc.addPyFile("s3a://bit-emr-cluster/dev/rene/packages/jinja2.zip")
    sc.addPyFile("s3a://bit-emr-cluster/hdfs/FanSEO/html_templates/artist_page.py")
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/pages_builders/artist_page_context_builder.py"
    )
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/pages_builders/city_pages/city_pages_context_builder.py"
    )

    import jinja2
    import artist_page
    import artist_page_context_builder
    import city_pages_context_builder

    jinja_env = jinja2.Environment(loader=jinja2.DictLoader(artist_page.TEMPLATES))
    context_builder = artist_page_context_builder.build_template_context

    footer_artists_path = "s3a://bit-emr-cluster/dev/rene/qualified_footer_artists"
    path = "s3a://bit-emr-cluster/dev/rene/artist_pages_data"

    schema = StructType(
        [
            StructField("artistId", IntegerType()),
            StructField(
                "events",
                ArrayType(
                    StructType(
                        [
                            StructField("id", IntegerType()),
                            StructField("title", StringType()),
                            StructField("mediaId", IntegerType()),
                            StructField("numCollectedTickets", IntegerType()),
                            StructField("streamingEvent", BooleanType()),
                            StructField("rsvpCount", IntegerType()),
                            StructField("announcedAt", StringType()),
                            StructField("startsAt", StringType()),
                            StructField("endsAt", StringType()),
                            StructField("day", StringType()),
                            StructField("month", StringType()),
                            StructField("year", StringType()),
                            StructField("date", StringType()),
                            StructField("artistId", IntegerType()),
                            StructField("artistMediaId", IntegerType()),
                            StructField("artistName", StringType()),
                            StructField("artistNameSlug", StringType()),
                            StructField("artistNameFirstLetter", StringType()),
                            StructField("artistGenres", ArrayType(StringType())),
                            StructField("artistOnTour", BooleanType()),
                            StructField("artistTrackerCount", IntegerType()),
                            StructField("venueName", StringType()),
                            StructField("city", StringType()),
                            StructField("venueCountry", StringType()),
                            StructField("latitude", DoubleType()),
                            StructField("longitude", DoubleType()),
                            StructField("streetAddress", StringType()),
                            StructField("venueAddress", StringType()),
                            StructField("venueRegion", StringType()),
                            StructField("venueLocation", StringType()),
                            StructField("venueLocationSlug", StringType()),
                            StructField("postalCode", StringType()),
                            StructField("region", StringType()),
                        ]
                    )
                ),
            ),
            StructField(
                "eventsByYear",
                ArrayType(
                    StructType(
                        [
                            StructField("event_year", StringType()),
                            StructField(
                                "events",
                                ArrayType(
                                    StructType(
                                        [
                                            StructField("id", IntegerType()),
                                            StructField("title", StringType()),
                                            StructField("mediaId", IntegerType()),
                                            StructField(
                                                "numCollectedTickets", IntegerType()
                                            ),
                                            StructField(
                                                "streamingEvent", BooleanType()
                                            ),
                                            StructField("rsvpCount", IntegerType()),
                                            StructField("announcedAt", StringType()),
                                            StructField("startsAt", StringType()),
                                            StructField("endsAt", StringType()),
                                            StructField("day", StringType()),
                                            StructField("month", StringType()),
                                            StructField("year", StringType()),
                                            StructField("date", StringType()),
                                            StructField("artistId", IntegerType()),
                                            StructField("artistMediaId", IntegerType()),
                                            StructField("artistName", StringType()),
                                            StructField("artistNameSlug", StringType()),
                                            StructField(
                                                "artistNameFirstLetter", StringType()
                                            ),
                                            StructField(
                                                "artistGenres", ArrayType(StringType())
                                            ),
                                            StructField("artistOnTour", BooleanType()),
                                            StructField(
                                                "artistTrackerCount", IntegerType()
                                            ),
                                            StructField("venueName", StringType()),
                                            StructField("city", StringType()),
                                            StructField("venueCountry", StringType()),
                                            StructField("latitude", DoubleType()),
                                            StructField("longitude", DoubleType()),
                                            StructField("streetAddress", StringType()),
                                            StructField("venueAddress", StringType()),
                                            StructField("venueRegion", StringType()),
                                            StructField("venueLocation", StringType()),
                                            StructField(
                                                "venueLocationSlug", StringType()
                                            ),
                                            StructField("postalCode", StringType()),
                                            StructField("region", StringType()),
                                        ]
                                    )
                                ),
                            ),
                        ]
                    )
                ),
            ),
            StructField(
                "reviewsWithComments",
                ArrayType(
                    StructType(
                        [
                            StructField("venueId", IntegerType()),
                            StructField("venueName", StringType()),
                            StructField("venueLocation", StringType()),
                            StructField("rating", IntegerType()),
                            StructField("comment", StringType()),
                            StructField("timestamp", StringType()),
                            StructField("date", StringType()),
                            StructField("venueNameSlug", StringType()),
                            StructField("venueLocationSlug", StringType()),
                            StructField("userFirstName", StringType()),
                            StructField("userDisplayName", StringType()),
                            StructField("userMediaId", IntegerType()),
                            StructField("userLocation", StringType()),
                        ]
                    )
                ),
            ),
            StructField(
                "reviewsWithMedia",
                ArrayType(
                    StructType(
                        [
                            StructField("mediaId", IntegerType()),
                        ]
                    ),
                ),
            ),
            StructField(
                "similarArtists",
                ArrayType(
                    StructType(
                        [
                            StructField("id", IntegerType()),
                            StructField("rank", IntegerType()),
                            StructField("name", StringType()),
                            StructField("mediaId", IntegerType()),
                            StructField("nameSlug", StringType()),
                            StructField("nameFirstLetter", StringType()),
                        ]
                    ),
                ),
            ),
            StructField(
                "artist",
                StructType(
                    [
                        StructField(
                            "bandMembers",
                            ArrayType(StructType([StructField("name", StringType())])),
                        ),
                        StructField("bio", StringType()),
                        StructField("formattedBio", StringType()),
                        StructField("genres", ArrayType(StringType())),
                        StructField("hometown", StringType()),
                        StructField("id", IntegerType()),
                        StructField(
                            "links",
                            ArrayType(
                                StructType(
                                    [
                                        StructField("type", StringType()),
                                        StructField("link", StringType()),
                                    ]
                                )
                            ),
                        ),
                        StructField("mediaId", IntegerType()),
                        StructField("name", StringType()),
                        StructField("nameFirstLetter", StringType()),
                        StructField("nameSlug", StringType()),
                        StructField("onTour", BooleanType()),
                        StructField("trackerCount", IntegerType()),
                        StructField("verified", BooleanType()),
                        StructField("dead", IntegerType()),
                    ]
                ),
            ),
        ]
    )

    footer_artists_collection = spark.read.parquet(footer_artists_path).collect()
    footer_cities_collection = city_pages_context_builder.FOOTER_CITIES_COLLECTION
    popular_cities_collection = (
        spark.read.parquet(
            "s3a://bit-emr-cluster/dev/rene/city_pages/popular_cities_with_nearby_cities"
        )
        .select(col("nameSlug"))
        .collect()
    )

    query = (
        spark.readStream.schema(schema)
        .parquet(path)
        .writeStream.trigger(once=True)
        .foreach(
            ForeachWriter(
                footer_artists=footer_artists_collection,
                footer_cities=footer_cities_collection,
                popular_cities=popular_cities_collection,
            )
        )
        .outputMode("update")
        .start()
    )

    query.awaitTermination()

    spark.stop()

    exit()


if __name__ == "__main__":
    main()