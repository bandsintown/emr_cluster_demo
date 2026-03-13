import json
from pyspark.sql.functions import from_json, to_json, col
from pyspark.sql.types import *

from pyspark.conf import SparkConf
from pyspark.sql import SparkSession

conf = SparkConf()
spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()

sc = spark.sparkContext

df = spark.read.parquet("s3a://bit-emr-cluster/permanent_tables/dynamo_popular_cities")


def get_nearby_cities(city_item):
    city_map = city_item.get("m", {})

    city = {
        "country": city_map.get("country", {}).get("s"),
        "dist": city_map.get("dist", {}).get("n"),
        "id": city_map.get("id", {}).get("n"),
        "city": city_map.get("city", {}).get("s"),
        "url": city_map.get("url", {}).get("s"),
        "region_code": city_map.get("region_code", {}).get("s"),
    }

    return city


nearby_cities_schema = ArrayType(
    StructType(
        [
            StructField("country", StringType()),
            StructField("dist", IntegerType()),
            StructField("id", IntegerType()),
            StructField("city", StringType()),
            StructField("url", StringType()),
            StructField("region_code", StringType()),
        ]
    )
)


schema = StructType(
    [
        StructField("id", IntegerType()),
        StructField("city", StringType()),
        StructField("region", StringType()),
        StructField("region_code", StringType()),
        StructField("country", StringType()),
        StructField("country_code", StringType()),
        StructField("latitude", StringType()),
        StructField("longitude", StringType()),
        StructField("url", StringType()),
        StructField("nearby_cities", nearby_cities_schema),
    ]
)


def row_to_dict(row):
    json_dict = {}

    for key, value in row.item.items():
        json_dict[key] = json.loads(value)

    cities = json_dict.get("nearby_cities", {}).get("l", [])
    nearby_cities = list(map(get_nearby_cities, cities))

    return {
        "id": json_dict.get("id", {}).get("n"),
        "city": json_dict.get("city", {}).get("s"),
        "region": json_dict.get("region", {}).get("s"),
        "region_code": json_dict.get("region_code", {}).get("s"),
        "country": json_dict.get("country", {}).get("s"),
        "country_code": json_dict.get("country_code", {}).get("s"),
        "latitude": json_dict.get("latitude", {}).get("s"),
        "longitude": json_dict.get("longitude", {}).get("s"),
        "url": json_dict.get("url", {}).get("s"),
        "nearby_cities": nearby_cities,
    }


parsed_rdd = df.rdd.map(row_to_dict)
parsed_df = spark.createDataFrame(parsed_rdd, schema)
parsed_df.show(n=1, truncate=False)