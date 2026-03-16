DROP TABLE IF EXISTS bit_daily_artist_dashboard.incoming_rsvps_user_geo_info_temp;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.incoming_rsvps_user_geo_info_temp (
    artist_id INT,
    country STRING,
    region STRING,
    city STRING,
    longitude DECIMAL(20,10),
    latitude DECIMAL(20,10),
    mineventdatetime TIMESTAMP,
    nbusers INT
)
LOCATION '/bit_daily/artist_dashboard/incomingrsvpsgeoinfotemp/'
TBLPROPERTIES ("auto.purge"="true");

INSERT INTO TABLE bit_daily_artist_dashboard.incoming_rsvps_user_geo_info_temp
SELECT
    a.artist_id,
    upper(a.country),
    upper(a.region),
    upper(a.city),
    a.longitude,
    a.latitude,
    MIN(a.eventdatetime),
    COUNT(DISTINCT a.rid) AS cnt
FROM (
    SELECT
        evl.artist_id AS artist_id,
        evl.venue_country AS country,
        evl.venue_region AS region,
        evl.venue_city AS city,
        evl.venue_longitude AS longitude,
        evl.venue_latitude AS latitude,
        from_unixtime(unix_timestamp(starts_at, "yyyy-MM-dd'T'HH:mm:ss'Z'")) AS eventdatetime,
        r.user_id AS rid
    FROM bit_daily_data_snapshot.events_batch AS evl
    JOIN bit_daily_data_snapshot.public_artists ba
        ON (evl.artist_id=ba.artist_id)
    JOIN fan_search.rsvps AS r
        ON (r.event_id = evl.artist_event_int_id)
    WHERE nvl(evl.streaming_event,FALSE) = FALSE
        AND r.status != 'cancelled'
) AS a
WHERE (a.longitude IS NOT NULL OR a.latitude IS NOT NULL)
GROUP BY
    a.artist_id,
    upper(a.country),
    upper(a.region),
    upper(a.city),
    a.longitude,
    a.latitude;

DROP TABLE IF EXISTS bit_daily_artist_dashboard.incoming_rsvps_user_geo_info;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.incoming_rsvps_user_geo_info (
    artist_id INT,
    country STRING,
    region STRING,
    city STRING,
    longitude DECIMAL(20,10),
    latitude DECIMAL(20,10),
    mineventdatetime TIMESTAMP,
    nbusers INT
)
LOCATION '/bit_daily/artist_dashboard/incomingrsvpsgeoinfo/'
TBLPROPERTIES ("auto.purge"="true");

INSERT INTO TABLE bit_daily_artist_dashboard.incoming_rsvps_user_geo_info
SELECT
    artist_id,
    country,
    region,
    city,
    avg(longitude),
    avg(latitude),
    mineventdatetime,
    sum(nbusers)
FROM bit_daily_artist_dashboard.incoming_rsvps_user_geo_info_temp
GROUP BY
    artist_id,
    country,
    region,
    city,
    mineventdatetime;

DROP TABLE IF EXISTS bit_daily_artist_dashboard.incoming_tour_geo_rsvps;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.incoming_tour_geo_rsvps (
    artist_id INT,
    venue_name STRING,
    eventdatetime TIMESTAMP,
    country STRING,
    region STRING,
    city STRING,
    longitude DECIMAL(20,10),
    latitude DECIMAL(20,10),
    nbusers INT
)
LOCATION '/bit_daily/artist_dashboard/incomingtourgeorsvps/'
TBLPROPERTIES ("auto.purge"="true");

INSERT INTO TABLE bit_daily_artist_dashboard.incoming_tour_geo_rsvps
SELECT
    evl.artist_id,
    upper(regexp_replace(evl.venue_name, '\\n|\\r', ' ')),
    from_unixtime(unix_timestamp(evl.starts_at, "yyyy-MM-dd'T'HH:mm:ss'Z'")),
    regexp_replace(evl.venue_country, '\\n|\\r', ' '),
    regexp_replace(evl.venue_region, '\\n|\\r', ' '),
    regexp_replace(evl.venue_city, '\\n|\\r', ' '),
    evl.venue_longitude,
    evl.venue_latitude,
    evl.rsvp_count
FROM bit_daily_data_snapshot.events_batch AS evl
JOIN bit_daily_data_snapshot.public_artists ba
    ON (evl.artist_id = ba.artist_id)
WHERE nvl(evl.streaming_event,FALSE) = FALSE
    AND evl.venue_latitude IS NOT NULL
    AND evl.venue_longitude IS NOT NULL;

DROP TABLE IF EXISTS bit_daily_artist_dashboard.incoming_event_venues_rsvps;
CREATE TABLE IF NOT EXISTS bit_daily_artist_dashboard.incoming_event_venues_rsvps (
    artist_id INT,
    venue_name STRING,
    eventdatetime TIMESTAMP,
    country STRING,
    region STRING,
    city STRING,
    rsvpstatus STRING,
    nbusers INT
)
LOCATION '/bit_daily/artist_dashboard/eventrsvps/'
TBLPROPERTIES ("auto.purge"="true");

INSERT INTO TABLE bit_daily_artist_dashboard.incoming_event_venues_rsvps
SELECT
    evl.artist_id,
    upper(regexp_replace(evl.venue_name, '\\n|\\r', ' ')),
    from_unixtime(unix_timestamp(evl.starts_at, "yyyy-MM-dd'T'HH:mm:ss'Z'")),
    regexp_replace(evl.venue_country, '\\n|\\r', ' '),
    regexp_replace(evl.venue_region, '\\n|\\r', ' '),
    regexp_replace(evl.venue_city, '\\n|\\r', ' '),
    r.status,
    COUNT(DISTINCT r.user_id)
FROM bit_daily_data_snapshot.events_batch AS evl
JOIN bit_daily_data_snapshot.public_artists ba
    ON (evl.artist_id=ba.artist_id)
LEFT OUTER JOIN fan_search.rsvps AS r
    ON (r.event_id = evl.artist_event_int_id)
WHERE nvl(evl.streaming_event, FALSE) = FALSE
GROUP BY
    evl.artist_id,
    upper(regexp_replace(evl.venue_name, '\\n|\\r', ' ')),
    from_unixtime(unix_timestamp(evl.starts_at, "yyyy-MM-dd'T'HH:mm:ss'Z'")),
    regexp_replace(evl.venue_country, '\\n|\\r', ' '),
    regexp_replace(evl.venue_region, '\\n|\\r', ' '),
    regexp_replace(evl.venue_city, '\\n|\\r', ' '),
    r.status;

DROP TABLE IF EXISTS  bit_daily_artist_dashboard.incoming_rsvps_user_geo_info_temp;