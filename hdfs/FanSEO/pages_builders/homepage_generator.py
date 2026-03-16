import boto3
import requests
import json
import unicodedata
import re
from datetime import datetime
from pyspark import SparkFiles
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession


SEARCH_API_URL = "https://search-api.prod.bandsintown.com/v2/_search"
SEARCH_API_AUTH = "Basic bGFtYmRhOndCQTJJVzJQNVc="

REGION_NAME = "us-east-1"
S3_BUCKET = "concerts.hypebot.com"
S3_DEV_BUCKET = "bit-bigdata-state-cycle"
BOTO_SESSION = boto3.Session(region_name=REGION_NAME)
S3_CLIENT = BOTO_SESSION.resource("s3")
CURRENT_YEAR = datetime.now().year


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


def get_trending_artists():
    auth_header = {"Authorization": SEARCH_API_AUTH}
    payload = {
        "query": json.dumps(
            {
                "filter": "charts",
                "location": "any",
                "entities": [
                    {"type": "artist", "order": "relevance", "limit": 10, "offset": 0}
                ],
            }
        )
    }
    res = requests.get(SEARCH_API_URL, headers=auth_header, params=payload, timeout=3)

    if res.status_code == 200:
        data = res.json()

        artists = data.get("artists", [])

        if artists:
            trending_artists = list(map(build_artist_for_render, artists))
            return trending_artists

        return []

    return []


def get_most_popular_artists():
    auth_header = {"Authorization": SEARCH_API_AUTH}
    payload = {
        "query": json.dumps(
            {
                "filter": "tracked artists",
                "location": "any",
                "entities": [
                    {"type": "artist", "order": "relevance", "limit": 10, "offset": 0}
                ],
            }
        )
    }
    res = requests.get(SEARCH_API_URL, headers=auth_header, params=payload, timeout=3)

    if res.status_code == 200:
        data = res.json()

        artists = data.get("artists", [])

        if artists:
            popular_artists = list(map(build_artist_for_render, artists))
            return popular_artists

        return []

    return []


def get_on_tour_artists():
    auth_header = {"Authorization": SEARCH_API_AUTH}
    payload = {
        "query": json.dumps(
            {
                "filter": "on tour",
                "location": "any",
                "entities": [
                    {"type": "artist", "order": "relevance", "limit": 10, "offset": 0}
                ],
            }
        )
    }
    res = requests.get(SEARCH_API_URL, headers=auth_header, params=payload, timeout=3)

    if res.status_code == 200:
        data = res.json()

        artists = data.get("artists", [])

        if artists:
            on_tour_artists = list(map(build_artist_for_render, artists))
            return on_tour_artists

        return []

    return []


def build_artist_for_render(artist):
    artist_id = artist.get("id")
    artist_name = artist.get("name", "")
    artist_name_slug = slugify(artist_name)
    artist_name_first_letter = artist_name_slug[0:1]

    if artist_name_slug.startswith("the-"):
        artist_name_first_letter = artist_name_slug[4:5]

    artist_media_id = artist.get("media_id")

    if all(
        [
            artist_id,
            artist_name,
            artist_name_slug,
            artist_name_first_letter,
            artist_media_id,
        ]
    ):
        return {
            "name": artist_name,
            "nameFirstLetter": artist_name_first_letter,
            "id": artist_id,
            "nameSlug": artist_name_slug,
            "mediaId": artist_media_id,
        }

    return None


def render_template(jinja_env, homepage_data):
    html_template = jinja_env.get_template("home/base.html")
    return html_template.render(
        {
            "env": "production",
            "domain": "https://concerts.hypebot.com/",
            "footerArtists": homepage_data.get("footer_artists", []),
            "footerCities": homepage_data.get("footer_cities", []),
            "mostPopularArtists": homepage_data.get("most_popular_artists", []),
            "trendingArtists": homepage_data.get("trending_artists", []),
            "onTourArtists": homepage_data.get("on_tour_artists", []),
            "copyrightYear": CURRENT_YEAR,
            "currentYear": CURRENT_YEAR,
        },
    )


def process(rendered, is_dev):
    s3_path = "latest"
    upload_to_s3(f"{s3_path}/index.html", rendered, is_dev)


def upload_to_s3(path, body, is_dev):
    if is_dev:
        dev_path = "dev_theo/fan_seo/index.html"
        S3_CLIENT.Object(S3_DEV_BUCKET, dev_path).put(Body=body, ContentType="text/html")
    else:
        S3_CLIENT.Object(S3_BUCKET, path).put(Body=body, ContentType="text/html")


def main(is_dev):
    conf = SparkConf()
    conf.setAppName("Fan SEO template generation")

    conf.set("spark.dynamicAllocation.enabled", "false")
    conf.set("spark.executor.cores", "1")
    conf.set("spark.executor.instances", "1")
    conf.set("spark.executor.memory", "1g")

    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext
    sc.addPyFile("s3a://bit-emr-cluster/dev/rene/packages/jinja2.zip")
    sc.addPyFile("s3a://bit-emr-cluster/hdfs/FanSEO/html_templates/homepage.py")
    sc.addPyFile(
        "s3a://bit-emr-cluster/hdfs/FanSEO/pages_builders/city_pages/city_pages_context_builder.py"
    )

    import jinja2
    import homepage
    import city_pages_context_builder

    jinja_env = jinja2.Environment(loader=jinja2.DictLoader(homepage.TEMPLATES))
    footer_artists_path = "s3a://bit-emr-cluster/dev/rene/qualified_footer_artists"
    footer_artists_collection = spark.read.parquet(footer_artists_path).collect()
    footer_cities_collection = city_pages_context_builder.FOOTER_CITIES_COLLECTION
    homepage_data = {
        "footer_artists": footer_artists_collection,
        "footer_cities": footer_cities_collection,
        "most_popular_artists": get_most_popular_artists(),
        "trending_artists": get_trending_artists(),
        "on_tour_artists": get_on_tour_artists(),
    }

    rendered_homepage = render_template(jinja_env, homepage_data)

    process(rendered_homepage, is_dev)

    spark.stop()

    exit()


if __name__ == "__main__":
    import sys
    is_dev = False
    if len(sys.argv) > 1:
        is_dev = sys.argv[1].lower() == 'true'
    
    main(is_dev)
