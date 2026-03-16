from pyspark import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    concat,
    lower as _lower,
    udf,
    when,
    lit,
)
from pyspark.sql.types import *


POPULAR_CITIES_PATH = (
    "s3a://bit-emr-cluster/permanent_tables/dynamo_popular_cities_parsed"
)


FOOTER_CITIES_SLUGS = [
    "new-york-ny",
    "indianola-ia",
    "chicago-il",
    "saint-paul-mn",
    "nashville-tn",
    "st-petersburg-fl",
    "winnipeg-mb",
    "hamilton-on",
    "calgary-ab",
    "quebec-qc",
    "london-on",
    "oshawa-on",
    "ottawa-on",
    "toronto-on",
    "vancouver-bc",
    "niagara-falls-on",
    "montreal-qc",
    "edmonton-ab",
    "mexico-city-mexico",
    "guadalajara-mexico",
    "monterrey-mexico",
    "cardiff-united-kingdom",
    "london-united-kingdom",
    "edinburgh-united-kingdom",
    "bristol-united-kingdom",
    "birmingham-united-kingdom",
    "glasgow-united-kingdom",
    "brighton-united-kingdom",
    "prague-czechia",
    "copenhagen-denmark",
    "cologne-germany",
    "nuremberg-germany",
    "munich-germany",
    "athens-greece",
    "dublin-ireland",
    "milan-italy",
    "turin-italy",
    "rome-italy",
    "krakow-poland",
    "bucharest-romania",
    "stockholm-sweden",
    "dubendorf-switzerland",
    "istanbul-turkey",
    "hong-kong",
    "shibuya-japan",
    "tokyo-japan",
    "jakarta-indonesia",
    "brisbane-australia",
    "buenos-aires-argentina",
    "santiago-chile",
]


NEARBY_CITIES_SCHEMA = ArrayType(
    StructType(
        [
            StructField("country", StringType()),
            StructField("city", StringType()),
            StructField("name", StringType()),
            StructField("nameSlug", StringType()),
            StructField("url", StringType()),
            StructField("regionCode", StringType()),
        ]
    )
)


@udf(returnType=NEARBY_CITIES_SCHEMA)
def compute_nearby_cities(nearby_cities):
    result = []

    for city in nearby_cities:
        computed_city_name = f"{city.city}, {city.country}"

        if city.country.lower() == "united states" or city.country.lower() == "canada":
            computed_city_name = f"{city.city}, {city.region_code}"

        struct = {
            "country": city.country,
            "city": city.city,
            "name": computed_city_name,
            "nameSlug": city.url,
            "url": city.url,
            "regionCode": city.region_code,
        }

        result.append(struct)

    return result


def main():
    conf = SparkConf()
    conf.setAppName("Fan SEO Popular Cities")
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

    popular_cities_df = spark.read.parquet(POPULAR_CITIES_PATH)

    city_pages = popular_cities_df.select(
        col("city"),
        col("country"),
        col("country_code").alias("countryCode"),
        col("region_code").alias("regionCode"),
        col("url"),
        col("url").alias("nameSlug"),
        col("latitude"),
        col("longitude"),
        concat(col("latitude"), lit(","), col("longitude")).alias("latlong"),
        when(
            (_lower(col("country_code")) == "us")
            | (_lower(col("country_code")) == "ca"),
            concat(col("city"), lit(", "), col("region_code")),
        )
        .otherwise(concat(col("city"), lit(", "), col("country")))
        .alias("name"),
        compute_nearby_cities(col("nearby_cities")).alias("nearbyCities"),
    )

    city_pages.write.mode("overwrite").parquet(
        "s3a://bit-emr-cluster/dev/rene/city_pages/popular_cities_with_nearby_cities"
    )

    spark.stop()
    exit()


if __name__ == "__main__":
    main()