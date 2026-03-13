SET hive.vectorized.execution.enabled=false;
SET hive.vectorized.execution.reduce.enabled=false;

source HiveDateVar.hql;

--- get data from s3

DROP TABLE IF EXISTS bit_daily_artist_dashboard.bit_logs_pixelactivities_3days_tmp PURGE;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.bit_logs_pixelactivities_3days_tmp (
    custom MAP<STRING,STRING>,
    type STRING,
    property STRING,
    medium STRING,
    user_agent STRING,
    nonce STRING,
    `date` STRING
)
STORED AS PARQUET
LOCATION '/bit_daily/artist_dashboard/bit_logs_pixelactivities_3days_tmp/';

INSERT INTO bit_daily_artist_dashboard.bit_logs_pixelactivities_3days_tmp
SELECT
    custom,
    type,
    property,
    medium,
    user_agent,
    nonce,
    `date`
FROM bit_logs.pixelactivities
WHERE ds >= ${hiveconf:three_days_ago_date};


DROP TABLE IF EXISTS bit_daily_artist_dashboard.bit_logs_ticketclicks_3days_tmp PURGE;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.bit_logs_ticketclicks_3days_tmp (
    artist_event_id INT,
    click_datetime STRING,
    user_agent STRING,
    app_id STRING,
    came_from INT,
    `date` TIMESTAMP
)
STORED AS PARQUET
LOCATION '/bit_daily/artist_dashboard/bit_logs_ticketclicks_3days_tmp/';

INSERT INTO bit_daily_artist_dashboard.bit_logs_ticketclicks_3days_tmp
SELECT
    artist_event_id,
    click_datetime,
    user_agent,
    app_id,
    came_from,
    `date`
FROM bit_logs.ticketclicks
WHERE `date` >= ${hiveconf:three_days_ago_date};


--- compute stats

DROP TABLE IF  EXISTS bit_daily_artist_dashboard.elp_stats;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.elp_stats (
    `date` STRING,
    type STRING,
    subtype STRING,
    artist_id INT,
    nb INT
)
LOCATION '/bit_daily/artist_dashboard/elp_stats/' 
TBLPROPERTIES ("auto.purge"="true");

--- insert page viewed

INSERT OVERWRITE TABLE bit_daily_artist_dashboard.elp_stats
SELECT 
    `date` AS `date`, 
    'views' AS type,
    NULL AS subtype,
    CAST(p.custom['artist_id'] AS INT) AS artist_id,
    COUNT(nonce) AS nb
FROM bit_daily_artist_dashboard.bit_logs_pixelactivities_3days_tmp AS p
WHERE property='jump_page'
    AND p.user_agent NOT LIKE '%Googlebot%'
    AND p.user_agent NOT LIKE '%Applebot%'
    AND p.user_agent NOT LIKE '%yandex%'
    AND p.user_agent NOT LIKE '%bing%'
    AND p.user_agent NOT LIKE '%python%'
    AND p.user_agent NOT LIKE '%baidu%'
    AND p.user_agent NOT LIKE '%bot%'
    AND p.user_agent NOT LIKE '%spider%'
    AND p.user_agent NOT LIKE '%crawler%'
    AND p.user_agent NOT LIKE '%ruby%'
    AND p.user_agent NOT LIKE '%ScoutJet%'
    AND p.user_agent NOT LIKE '%ia_archiver%'
    AND p.user_agent NOT LIKE '%ichiro%'
    AND p.user_agent NOT LIKE '%MJ12bot%'
    AND p.user_agent NOT LIKE '%PycURL%'
    AND p.user_agent NOT LIKE '%Jakarta%'
    AND p.user_agent NOT LIKE '%Yahoo%'
    AND p.user_agent NOT LIKE '%scrapy%'
    AND p.user_agent NOT LIKE '%facebookexternalhit%'
    -- AND p.user_agent NOT LIKE '%Go%'
    AND p.user_agent NOT LIKE '%WordPress%'
    AND p.user_agent NOT LIKE '%NetShelter%'
GROUP BY 
    `date`,
    CAST(p.custom['artist_id'] AS INT);

--- insert clicks others than ticket clicks

INSERT INTO TABLE bit_daily_artist_dashboard.elp_stats
SELECT
    `date` AS `date`, 
    'clicks' AS type,
    custom['utm_campaign'] AS subtype,
    CAST(p.custom['artist_id'] AS INT) AS artist_id, 
    COUNT(nonce) AS nb
FROM bit_daily_artist_dashboard.bit_logs_pixelactivities_3days_tmp AS p
WHERE (property='bit_web_v1' OR property='bit_web_v3' OR medium='mobile')
    AND (type='event' OR type='artist')
    AND custom['utm_source'] ='jump_page'
    AND custom['utm_campaign']!='ticket'
    AND custom['utm_campaign']!='null'
GROUP BY 
    `date`,
    CAST(p.custom['artist_id'] AS INT),
    custom['utm_campaign'];


---- insert ticket clicks from ticket log only since there are not that many left in pixel
INSERT INTO TABLE bit_daily_artist_dashboard.elp_stats
SELECT 
    t.`date` AS `date`,
    'clicks' AS type,
    'tickets' AS subtype,
    CAST(evl.artist.id AS INT) AS artist_id,
    COUNT(t.click_datetime) AS nb
FROM bit_daily_artist_dashboard.bit_logs_ticketclicks_3days_tmp AS t
JOIN bit_daily_data_snapshot.events AS evl 
    ON (evl.artist_event_int_id=t.artist_event_id and actor='artist')
WHERE t.came_from = 269
    AND lower(t.user_agent) NOT LIKE '%googlebot%' 
    AND lower(t.user_agent) NOT LIKE '%applebot%'
    AND lower(t.user_agent) NOT LIKE '%yandex%'
    AND lower(t.user_agent) NOT LIKE '%bing%'
    AND lower(t.user_agent) NOT LIKE '%python%'
    AND lower(t.user_agent) NOT LIKE '%baidu%'
    AND lower(t.user_agent) NOT LIKE '%bot%'
    AND lower(t.user_agent) NOT LIKE '%spider%'
    AND lower(t.user_agent) NOT LIKE '%crawler%'
    AND lower(t.user_agent) NOT LIKE '%ruby%'
    AND lower(t.user_agent) NOT LIKE '%scoutJet%'
    AND lower(t.user_agent) NOT LIKE '%ia_archiver%'
    AND lower(t.user_agent) NOT LIKE '%ichiro%'
    AND lower(t.user_agent) NOT LIKE '%mj12bot%'
    AND lower(t.user_agent) NOT LIKE '%pycurl%'
    AND lower(t.user_agent) NOT LIKE '%jakarta%'
    AND lower(t.user_agent) NOT LIKE '%yahoo%'
    AND lower(t.user_agent) NOT LIKE '%scrapy%'
    AND lower(t.user_agent) NOT LIKE '%facebookexternalhit%'
    -- AND lower(t.user_agent) NOT LIKE '%go%'
    AND lower(t.user_agent) NOT LIKE '%wordpress%'
    AND lower(t.user_agent) NOT LIKE '%netshelter%'
    AND t.user_agent NOT LIKE '%Mozilla/5.0 (X11\; Linux x86_64) AppleWebKit/537.36 (KHTML, LIKE Gecko) Ubuntu Chromium/45.0.2454.101 Chrome/45.0.2454.101 Safari/537.36%'
    AND t.user_agent NOT LIKE '%Mozilla/5.0 (X11\; Ubuntu\; Linux x86_64\; rv:41.0) Gecko/20100101 Firefox/41.0%'
GROUP BY 
    t.`date`, 
    CAST(evl.artist.id AS INT);



--- activities 
ADD JAR s3://bit-emr-cluster/hdfs/bit_events/job_config_files/jar/brickhouse-0.7.1-SNAPSHOT.jar;
CREATE TEMPORARY FUNCTION to_json AS 'brickhouse.udf.json.ToJsonUDF';

DROP TABLE IF EXISTS bit_daily_artist_dashboard.play_my_city_stats;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.play_my_city_stats
TBLPROPERTIES ("auto.purge"="true")
AS
WITH activities_3days AS (
    SELECT
        id AS activity_id,
        SUBSTR(act.created_at,1,10) AS activity_date,
        IF(SPLIT(actor,':')[0]='user',SPLIT(actor,':')[1],NULL) AS user_id,
        IF(SPLIT(actor,':')[0]='artist',SPLIT(actor,':')[1],
        IF(SPLIT(object,':')[0]='artist',SPLIT(object,':')[1],NULL)) AS artist_id,
        to_json(data) AS data
    FROM fan_search.activities AS act
    WHERE SUBSTR(act.created_at,1,10) >=  ${hiveconf:three_days_ago_date}
        AND type='user'
        AND verb='request'
)

SELECT
    a.activity_date,
    a.artist_id,
    TRIM(get_json_object(data,'$.place.city')) AS city,
    TRIM(get_json_object(data,'$.place.region_code')) AS region,
    TRIM(get_json_object(data,'$.place.country')) AS country,
    get_json_object(data,'$.place.latitude') AS latitude,
    get_json_object(data,'$.place.longitude') AS longitude,
    COUNT(activity_date) AS nb
FROM activities_3days AS a
GROUP BY
    a.activity_date,
    a.artist_id,
    TRIM(get_json_object(data,'$.place.city')),
    TRIM(get_json_object(data,'$.place.region_code')),
    TRIM(get_json_object(data,'$.place.country')),
    get_json_object(data,'$.place.latitude'),
    get_json_object(data,'$.place.longitude');