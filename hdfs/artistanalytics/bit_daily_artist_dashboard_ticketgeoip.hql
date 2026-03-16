USE bit_daily_artist_dashboard;


CREATE TABLE IF NOT EXISTS temp_artists_cities_ticletclicks (
    artist_id INT,
    city STRING,
    region STRING,
    country STRING, 
    nb INT
) 
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' 
LOCATION  '/bit_daily/artist_dashboard/temp_artists_cities_ticletclicks/';


DROP TABLE IF EXISTS bit_daily_artist_dashboard.artists_clicks_geo;
CREATE TABLE IF NOT EXISTS artists_clicks_geo (
    artist_id INT,
    artist_name STRING,
    country STRING,
    region STRING,
    city STRING,
    longitude DECIMAL(20,10),
    latitude DECIMAL(20,10),
    cnt INT
)
LOCATION  '/bit_daily/artist_dashboard/artists_clicks_geo/'
TBLPROPERTIES ("auto.purge"="true");

INSERT INTO TABLE bit_daily_artist_dashboard.artists_clicks_geo  
SELECT 
    tact.artist_id,  
    '',
    tact.country, 
    tact.region, 
    LOWER(tact.city), 
    citylist.longitude, 
    citylist.latitude, 
    tact.nb 
FROM bit_daily_artist_dashboard.temp_artists_cities_ticletclicks tact
JOIN bit_production_db.countries_regions_cities AS citylist 
    ON (LOWER(citylist.city) = LOWER(tact.city) 
        AND LOWER(citylist.region)=LOWER(tact.region) 
        AND LOWER(citylist.country)=LOWER(tact.country)) 
WHERE LOWER(tact.country) IN ('united states', 'canada')
    AND LOWER(citylist.country) IN ('united states', 'canada');


INSERT INTO TABLE bit_daily_artist_dashboard.artists_clicks_geo 
SELECT 
    tact.artist_id,
    '',
    tact.country,
    tact.region,
    LOWER(tact.city),
    A.longitude,
    A.latitude,
    tact.nb
FROM bit_daily_artist_dashboard.temp_artists_cities_ticletclicks tact
JOIN (
    SELECT 
        country,
        region,
        city,
        longitude,
        latitude
    FROM (
        SELECT 
            country,
            region,
            city,
            longitude,
            latitude,
            rank() OVER (PARTITION BY country,city ORDER BY city_id DESC) AS rank 
        FROM bit_production_db.countries_regions_cities
    ) ranked_countries_regions_cities
    WHERE ranked_countries_regions_cities.rank = 1
) A ON (LOWER(A.city) = LOWER(tact.city)
    AND LOWER(A.country)=LOWER(tact.country)) 
WHERE LOWER(tact.country) NOT IN ('united states', 'canada') 
    AND tact.city!='';
