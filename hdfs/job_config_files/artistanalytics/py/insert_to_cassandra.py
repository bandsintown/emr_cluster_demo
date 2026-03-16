import sys
import boto3

from pyspark import SparkConf
from pyspark.sql import SparkSession
from datetime import datetime, timedelta, timezone
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import dict_factory

REGION_NAME = "us-east-1"
cloudwatch_log_group = "ManagerArtistStatsAPI"
cloudwatch = boto3.client('cloudwatch',region_name=REGION_NAME)

def send_to_cloudwatch_metrics(counters):
     for key,value in counters.items():
          metrics=[{'MetricName':key, "Value":int(value)}]
          cloudwatch.put_metric_data(Namespace=cloudwatch_log_group, MetricData=metrics)

if len(sys.argv) < 3:
    sys.stderr.write("Usage: {} <YEAR-MONTH-DATE> <DAYS> {}".format(sys.argv[0],chr(10)))
    exit(-1)

DAYS_FROM = int(sys.argv[1])
INSERT_COLS = sys.argv[2]
PRIMARY_KEY = sys.argv[3]
CLUSTER_ORDER_KEY = sys.argv[4]
HIVE_TABLE = sys.argv[5]
CASSANDRA_TABLE = sys.argv[6]
FULL_TABLE_INDEXATION = sys.argv[7]

DAYS_TO = -1
if CASSANDRA_TABLE == 'artist_ticketclicks_by_day':
    DAYS_TO = 1

TODAY = datetime.now(tz = timezone.utc).date()
START = (TODAY + timedelta(days=-DAYS_FROM)).strftime('%Y-%m-%d')
END = (TODAY + timedelta(days=DAYS_TO)).strftime('%Y-%m-%d')
WHERE_STATEMENT = f"WHERE `{CLUSTER_ORDER_KEY}` BETWEEN '{START}' AND '{END}'" if FULL_TABLE_INDEXATION == "FALSE" else ""

## Need to move to secrets
USERNAME = "hadoop"
PASSWORD = "Fh8Tec72"


def build_update_string(new_row: dict, cols: str) -> str:
    keys = cols.split(",")
    key_values = [str(new_row.get(col)) if type(new_row.get(col)) != str else "'{}'".format(new_row.get(col)) for col in keys]
    cassandra_values = ",".join(map(str, key_values))
    primary_key_value = str(new_row.get(f"{PRIMARY_KEY}"))
    cluster_order_key_value = str(new_row.get(f"{CLUSTER_ORDER_KEY}"))
    insert_statement = f"""
        INSERT INTO {CASSANDRA_TABLE} ({PRIMARY_KEY}, {CLUSTER_ORDER_KEY}, {cols}) 
        VALUES ({primary_key_value}, '{cluster_order_key_value}', {cassandra_values})
    """
    return insert_statement

def send(iterator):
    auth_provider = PlainTextAuthProvider(
        username = USERNAME, 
        password = PASSWORD
    )
    cluster = Cluster (
        [
            'cassandra1.prod.bandsintown.com', 
            'cassandra2.prod.bandsintown.com', 
            'cassandra3.prod.bandsintown.com'
        ],
        auth_provider = auth_provider,
        protocol_version = 3
    )

    session = cluster.connect("bands")
    session.row_factory = dict_factory
    docs=[]
    for row in iterator:
        if row[f"{PRIMARY_KEY}"] is not None and row[f"{CLUSTER_ORDER_KEY}"] is not None:
            doc = build_update_string(
                row.asDict(), 
                INSERT_COLS
            )
            docs.append(doc)
            if len(docs) >= 1000:
                session.execute(
                    """
                        BEGIN BATCH
                        {}
                        APPLY BATCH;
                    """.format("\n".join(docs)), 
                    timeout = None
                )
                inserted_count.add(len(docs))
                docs = []
    if len(docs) > 0:
        session.execute(
            """
                BEGIN BATCH
                {}
                APPLY BATCH;
            """.format("\n".join(docs)), 
            timeout=None
        )
        inserted_count.add(len(docs))

def main():
    conf = SparkConf()
    conf.setAppName(f'Insert Artist Metrics into {CASSANDRA_TABLE}')
    spark = SparkSession.builder.config(conf=conf).enableHiveSupport().getOrCreate()
    sc = spark.sparkContext

    global inserted_count
    inserted_count = sc.accumulator(0)

    spark.sql(f"""
        SELECT 
            {PRIMARY_KEY},
            {CLUSTER_ORDER_KEY},
            {INSERT_COLS}
        FROM {HIVE_TABLE}
        {WHERE_STATEMENT}
        ORDER BY {PRIMARY_KEY}, {CLUSTER_ORDER_KEY}
    """).repartition(f"{PRIMARY_KEY}").foreachPartition(send)

    # write to cloudwatch
    send_to_cloudwatch_metrics(
        {
            f"insert_into_cassandra_{CASSANDRA_TABLE}_inserted_count" : inserted_count.value
        }
    )

    print(f"""
        inserted count : {inserted_count.value}
    """)

    spark.stop()
    exit()

if __name__ == "__main__":
    main()