from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import sys
import logging
import argparse
import pymysql
from pymysql import Error

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




def execute_upsert_query(jdbc_url, db_user, db_password, final_table, staging_table, update_key, columns):
    """Executes the MySQL SQL query to merge data from staging to final table using PyMySQL.

    args:
    jdbc_url: JDBC connection string
    db_user: MySQL user name
    db_password:
    final_table: final table name
    staging_table: staging table name
    update_key: update key
    columns: column names
    """

    # 1. Parse connection details from the JDBC URL
    try:
        # Splits the URL to extract components needed for PyMySQL
        # Example: 'jdbc:mysql://host:port/dbname?params'
        url_parts = jdbc_url.split('//')[-1]
        host_port = url_parts.split('/')[0]
        host = host_port.split(':')[0]

        # Basic check for port, defaults to 3306 if not explicitly in URL
        try:
            port = int(host_port.split(':')[-1])
        except ValueError:
            port = 3306

        db_name = url_parts.split('/')[-1].split('?')[0]

    except (IndexError, ValueError):
        # Assuming 'logger' is defined globally
        logger.error("Could not parse DB host/name/port from JDBC URL. Check format.")
        raise

    # 2. Construct the SQL UPSERT query
    update_cols = [c for c in columns if c != update_key]

    # Creates the ON DUPLICATE KEY UPDATE clause
    set_clause = ", ".join([f"{column} = s.{column}" for column in update_cols])

    upsert_sql = f"""
    INSERT INTO {final_table} ({', '.join(columns)})
    SELECT {', '.join(columns)} FROM {staging_table} s
    ON DUPLICATE KEY UPDATE
        {set_clause};
    """

    logger.info(f"Executing UPSERT SQL: {upsert_sql}")

    conn = None
    try:
        # 3. Establish a direct Python-to-MySQL connection using PYMYSQL
        conn = pymysql.connect(  # <-- CHANGE 3: Use pymysql.connect
            host=host,
            port=port,
            database=db_name,
            user=db_user,
            password=db_password,
            # Ensure encoding is set for the connection. 'utf8mb4' is best.
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # 4. Execute the DML query
        cursor.execute(upsert_sql)
        conn.commit()

        logger.info(f"UPSERT operation completed successfully. Rows affected: {cursor.rowcount}")

    except Error as e:  # <-- CHANGE 4: Use pymysql.Error
        logger.error(f"Failed to execute UPSERT query via PyMySQL connector: {e}")
        # Reraise to fail the job
        raise

    finally:
        # 5. Clean up connection
        # PyMySQL connection check: conn.open is preferred over conn.is_connected()
        if conn and conn.open:
            cursor.close()
            conn.close()


def main(args)->None:
    logger.info("Starting Dynamic PySpark Export Job.")

    # 1. Initialize Spark Session
    spark = SparkSession.builder \
        .appName(f"SqoopExportEquivalent_{args.final_table}") \
        .enableHiveSupport() \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    spark.sql("""ADD JAR s3a://bit-emr-cluster/hdfs/job_config_files/jars/mysql-connector-java-8.0.20.jar""")

    # Define the explicit mapping from Hive (Source) to MySQL (Target)
    # Based on your table inspection and the error message.
    column_mapping = {
        "artist_id": "ID",
        "artist_name": "Name",
        "managed": "Is_Managed",
        "tracker_count": "Tracker_Count",
        "on_tour": "On_Tour",
        "nb_upcoming_events": "Upcoming_Events",
        "url": "URL",
        "media_id": "Media_ID"
    }

    # 2. Read the data and Rename Columns
    try:
        df = spark.read.table(args.source_table)

        # Determine the columns to select and rename based on the target order
        target_columns_list = args.columns.split(',')

        # Find the Hive name corresponding to the MySQL target name
        # We perform a reverse lookup to build the select statement
        source_cols_to_select = {v: k for k, v in column_mapping.items()}

        renamed_cols = []
        for target_name in target_columns_list:
            hive_name = source_cols_to_select.get(target_name)
            if hive_name is None:
                raise ValueError(f"Column '{target_name}' not found in mapping for Hive source.")
            # col(hive_name).alias(target_name) is the correct aliasing logic
            renamed_cols.append(col(hive_name).alias(target_name))

        # Select and rename the columns in the DataFrame
        df = df.select(renamed_cols)

        logger.info(f"Successfully read {df.count()} records and renamed columns for export.")

    except Exception as e:
        logger.error(f"Error reading data from HDFS: {e}")
        spark.stop()
        sys.exit(1)

    # --- 3. Write Data to the Staging Table (MISSING STEP ADDED) ---
    staging_table = f"{args.final_table}_staging"

    logger.info(f"Writing data to staging table: {staging_table}")

    final_jdbc_url = f"{args.jdbc_url}&useUnicode=true&characterEncoding=UTF-8"
    table_options = "ENGINE=InnoDB DEFAULT CHARACTER SET=utf8mb4 COLLATE=utf8mb4_unicode_ci"

    # Use the renamed DataFrame (df) to write to the MySQL staging table
    df.write.format("jdbc").options(
        url=final_jdbc_url,
        driver=args.db_driver,
        dbtable=staging_table,  # Target the staging table
        user=args.db_user,
        password=args.db_password,
        createTableOptions= table_options
    ).mode("overwrite").save()

    # 4. Execute the UPSERT merge query
    # Pass the target columns (which are now correct for the MySQL table)
    execute_upsert_query(
        args.jdbc_url,
        args.db_user,
        args.db_password,
        args.final_table,
        staging_table,  # Pass the dynamically defined staging table
        args.update_key,
        target_columns_list  # Pass the list of target MySQL columns
    )

    spark.stop()


if __name__ == "__main__":
    # Define arguments that will be passed by SparkSubmitOperator
    parser = argparse.ArgumentParser(description="Dynamic PySpark Export Job")

    # --- JDBC CONNECTION ARGS (NEEDED FOR ARGS.JDBC_URL, etc.) ---
    parser.add_argument("--jdbc_url", required=True, help="The JDBC connection URL for the database.")
    parser.add_argument("--db_user", required=True, help="Database username.")
    parser.add_argument("--db_password", required=True, help="Database password.")
    parser.add_argument("--db_driver", default="com.mysql.cj.jdbc.Driver", help="JDBC driver class name.")
    # -------------------------------------------------------------

    parser.add_argument("--final_table", required=True, help="The final production table name.")
    parser.add_argument("--source_table", required=True, help="The source table in HDFS/S3.")
    parser.add_argument("--update_key", required=True, help="The primary key column for UPSERT.")
    parser.add_argument("--columns", required=True,
                        help="Comma-separated list of column names for selection and ordering.")

    main(parser.parse_args())