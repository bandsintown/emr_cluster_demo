import requests
from pyspark import SparkContext,SparkConf
from pyspark.sql import SparkSession, SQLContext
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

username = "hadoop"
password = "Fh8Tec72"

def send(iterator):
    geolocations = {}

    auth_provider = PlainTextAuthProvider(
        username=username, password=password)
    cluster = Cluster(['cassandra1.prod.bandsintown.com', 'cassandra2.prod.bandsintown.com', 'cassandra3.prod.bandsintown.com'],
                    auth_provider=auth_provider)

    session = cluster.connect("bands")
    docs=[]
    for row in iterator:
        if row.artist_id is not None and row.artist_id > 0:
            doc = "INSERT INTO upcoming_event_rsvps_ticketclicks_by_event_date (artist_id, event_date, city, country, region, rsvp_count, ticketclick_count, venue_name) VALUES ({}, {}, {}, {}, {}, {}, {}, {});".format(
                row.artist_id,
                "'{}'".format(row.event_date),
                "''" if row.city is None else "'{}'".format(row.city.replace("'","''")),
                "''" if row.country is None else "'{}'".format(row.country.replace("'","''")),
                "''" if row.region is None else "'{}'".format(row.region.replace("'","''")),
                row.rsvp_count,
                row.ticketclick_count,
                "''" if row.venue_name is None else "'{}'".format(row.venue_name.replace("'","''"))
            )
            docs.append(doc)
            if len(docs) >= 1000:
                session.execute("""BEGIN BATCH
                {}
                APPLY BATCH;""".format("\n".join(docs)), timeout=None)
                docs = []
    if len(docs) > 0:
        session.execute("""BEGIN BATCH
            {}
            APPLY BATCH;""".format("\n".join(docs)), timeout=None)
            

def main():
    conf = SparkConf()
    conf.setAppName('Insert Artist Metrics into upcoming_event_rsvps_ticketclicks_by_event_date')

    conf.set("spark.executor.instances","3")
    conf.set("spark.executor.cores","3")
    conf.set("spark.executor.memory","3g")
    conf.set('spark.driver.memory','4g')
    conf.set("spark.dynamicAllocation.enabled","false")
    # conf.set('spark.kryoserializer.buffer', '256m')
    # conf.set('spark.yarn.maxAppAttempts', '1')


    spark = SparkSession.builder.config(
        conf=conf).enableHiveSupport().getOrCreate()

    data = spark.sql(
        """
        SELECT * 
        FROM bit_daily_artist_dashboard.upcoming_event_rsvps_ticketclicks_by_event_date
        """
    )
    data.foreachPartition(send)


if __name__ == '__main__':
    main()