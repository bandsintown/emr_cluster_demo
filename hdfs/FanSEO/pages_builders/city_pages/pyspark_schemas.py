from pyspark.sql.types import *


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

POPULAR_CITIES_SCHEMA = StructType(
    [
        StructField("city", StringType()),
        StructField("country", StringType()),
        StructField("countryCode", StringType()),
        StructField("regionCode", StringType()),
        StructField("url", StringType()),
        StructField("nameSlug", StringType()),
        StructField("latitude", StringType()),
        StructField("longitude", StringType()),
        StructField("latlong", StringType()),
        StructField("name", StringType()),
        StructField("nearbyCities", NEARBY_CITIES_SCHEMA),
    ]
)
