from datetime import datetime
from operator import itemgetter

CURRENT_YEAR = datetime.now().year
YEAR_RANGE_FOR_SEO = f"{CURRENT_YEAR}-{CURRENT_YEAR + 1}"

GENRES = [
    {"label": "Alternative", "labelSlug": "alternative"},
    {"label": "Blues", "labelSlug": "blues"},
    {"label": "Christian/Gospel", "labelSlug": "christian-gospel"},
    {"label": "Classical", "labelSlug": "classical"},
    {"label": "Country", "labelSlug": "country"},
    {"label": "Electronic", "labelSlug": "electronic"},
    {"label": "Folk", "labelSlug": "folk"},
    {"label": "Hip Hop", "labelSlug": "hip-hop"},
    {"label": "Jazz", "labelSlug": "jazz"},
    {"label": "Metal", "labelSlug": "metal"},
    {"label": "Pop", "labelSlug": "pop"},
    {"label": "Punk", "labelSlug": "punk"},
    {"label": "R&B/Soul", "labelSlug": "rnb-soul"},
    {"label": "Reggae", "labelSlug": "reggae"},
    {"label": "Rock", "labelSlug": "rock"},
    {"label": "Popular", "labelSlug": "popular"},
]

FOOTER_CITIES_COLLECTION = [
    {"nameSlug": "new-york-ny", "name": "New York, NY"},
    {"nameSlug": "indianola-ia", "name": "Indianola, IA"},
    {"nameSlug": "chicago-il", "name": "Chicago, IL"},
    {"nameSlug": "saint-paul-mn", "name": "Saint Paul, MN"},
    {"nameSlug": "nashville-tn", "name": "Nashville, TN"},
    {"nameSlug": "st-petersburg-fl", "name": "St. Petersburg, FL"},
    {"nameSlug": "winnipeg-mb", "name": "Winnipeg, MB"},
    {"nameSlug": "hamilton-on", "name": "Hamilton, ON"},
    {"nameSlug": "calgary-ab", "name": "Calgary, AB"},
    {"nameSlug": "quebec-qc", "name": "Quebec, QC"},
    {"nameSlug": "london-on", "name": "London, ON"},
    {"nameSlug": "oshawa-on", "name": "Oshawa, ON"},
    {"nameSlug": "ottawa-on", "name": "Ottawa, ON"},
    {"nameSlug": "toronto-on", "name": "Toronto, ON"},
    {"nameSlug": "vancouver-bc", "name": "Vancouver, BC"},
    {"nameSlug": "niagara-falls-on", "name": "Niagara Falls, ON"},
    {"nameSlug": "montreal-qc", "name": "Montreal, QC"},
    {"nameSlug": "edmonton-ab", "name": "Edmonton, AB"},
    {"nameSlug": "mexico-city-mexico", "name": "Mexico City, Mexico"},
    {"nameSlug": "guadalajara-mexico", "name": "Guadalajara, Mexico"},
    {"nameSlug": "monterrey-mexico", "name": "Monterrey, Mexico"},
    {"nameSlug": "cardiff-united-kingdom", "name": "Cardiff, United Kingdom"},
    {"nameSlug": "london-united-kingdom", "name": "London, United Kingdom"},
    {"nameSlug": "edinburgh-united-kingdom", "name": "Edinburgh, United Kingdom"},
    {"nameSlug": "bristol-united-kingdom", "name": "Bristol, United Kingdom"},
    {"nameSlug": "birmingham-united-kingdom", "name": "Birmingham, United Kingdom"},
    {"nameSlug": "glasgow-united-kingdom", "name": "Glasgow, United Kingdom"},
    {"nameSlug": "brighton-united-kingdom", "name": "Brighton, United Kingdom"},
    {"nameSlug": "prague-czechia", "name": "Prague, Czechia"},
    {"nameSlug": "copenhagen-denmark", "name": "Copenhagen, Denmark"},
    {"nameSlug": "cologne-germany", "name": "Cologne, Germany"},
    {"nameSlug": "nuremberg-germany", "name": "Nuremberg, Germany"},
    {"nameSlug": "munich-germany", "name": "Munich, Germany"},
    {"nameSlug": "athens-greece", "name": "Athens, Greece"},
    {"nameSlug": "dublin-ireland", "name": "Dublin, Ireland"},
    {"nameSlug": "milan-italy", "name": "Milan, Italy"},
    {"nameSlug": "turin-italy", "name": "Turin, Italy"},
    {"nameSlug": "rome-italy", "name": "Rome, Italy"},
    {"nameSlug": "krakow-poland", "name": "Krakow, Poland"},
    {"nameSlug": "bucharest-romania", "name": "Bucharest, Romania"},
    {"nameSlug": "stockholm-sweden", "name": "Stockholm, Sweden"},
    {"nameSlug": "dubendorf-switzerland", "name": "Dubendorf, Switzerland"},
    {"nameSlug": "istanbul-turkey", "name": "Istanbul, Turkey"},
    {"nameSlug": "hong-kong", "name": "Hong Kong, Hong Kong"},
    {"nameSlug": "shibuya-japan", "name": "Shibuya, Japan"},
    {"nameSlug": "tokyo-japan", "name": "Tokyo, Japan"},
    {"nameSlug": "jakarta-indonesia", "name": "Jakarta, Indonesia"},
    {"nameSlug": "brisbane-australia", "name": "Brisbane, Australia"},
    {"nameSlug": "buenos-aires-argentina", "name": "Buenos Aires, Argentina"},
    {"nameSlug": "santiago-chile", "name": "Santiago, Chile"},
]


def build_context(city, events, genre, footer_artists):
    compacted_events = __compact_events_by_artist(events)
    events_by_rsvp_count = sorted(
        compacted_events, key=itemgetter("rsvpCount"), reverse=True
    )
    artists = __get_unique_artists_from_events(compacted_events)
    venues = __get_unique_venues_from_events(events)

    if len(artists) < 50:
        artists = __append_to_artists(artists, footer_artists)

    if genre.get("labelSlug") == "popular":
        events_selling_fast = sorted(
            compacted_events, key=itemgetter("numCollectedTickets"), reverse=True
        )
        artists_on_tour = sorted(artists, key=itemgetter("onTour"), reverse=True)

        return {
            "city": city,
            "genre": genre,
            "allGenres": GENRES,
            "eventsByGenre": {"popular": events_by_rsvp_count[0:30]},
            "eventsPopular": events_by_rsvp_count[0:30],
            "eventsSellingFast": events_selling_fast[0:20],
            "artistsMostPopular": artists[10:20],
            "artistsOnTour": artists_on_tour[0:10],
            "artistsTrending": artists[0:10],
            "faqArtists": artists[0:3],
            "faqNbrUpcomingEvents": len(compacted_events),
            "faqVenues": venues[0:5],
            "env": "production",
            "domain": "https://concerts.hypebot.com/",
            "currentYear": CURRENT_YEAR,
            "yearRange": YEAR_RANGE_FOR_SEO,
            "footerArtists": footer_artists,
            "footerCities": FOOTER_CITIES_COLLECTION,
        }
    else:
        return {
            "city": city,
            "genre": genre,
            "allGenres": GENRES,
            "eventsByGenre": {genre.get("labelSlug"): events_by_rsvp_count[0:30]},
            "faqArtists": artists[0:3],
            "faqNbrUpcomingEvents": len(compacted_events),
            "faqVenues": venues[0:5],
            "env": "production",
            "domain": "https://concerts.hypebot.com/",
            "yearRange": YEAR_RANGE_FOR_SEO,
            "currentYear": CURRENT_YEAR,
            "footerArtists": footer_artists,
            "footerCities": FOOTER_CITIES_COLLECTION,
        }


def __append_to_artists(artists, extra_artists):
    total_artists = 50
    number_artists_to_add = total_artists - len(artists)
    artists_on_tour = sorted(extra_artists, key=itemgetter("onTour"), reverse=True)

    return artists + artists_on_tour[0:number_artists_to_add]


def __compact_events_by_artist(events):
    artists_ids = []
    compacted_events = []

    for event in events:
        artist_id = event.get("artistId")

        if event.get("artistId") not in artists_ids:
            compacted_events.append(event)
            artists_ids.append(artist_id)

    return compacted_events


def __get_unique_artists_from_events(events):
    artists_ids = []
    artists = []

    for event in events:
        artist_id = event.get("artistId")
        if artist_id not in artists_ids:
            artists_ids.append(artist_id)

            artists.append(
                {
                    "id": event.get("artistId"),
                    "mediaId": event.get("artistMediaId"),
                    "name": event.get("artistName"),
                    "nameSlug": event.get("artistNameSlug"),
                    "nameFirstLetter": event.get("artistNameFirstLetter"),
                    "genres": event.get("artistGenres"),
                    "onTour": event.get("artistOnTour"),
                    "trackerCount": event.get("artistTrackerCount"),
                }
            )

    return artists


def __get_unique_venues_from_events(events):
    venues_ids = []
    venues = []

    for event in events:
        venue_id = event.get("venueName")
        if venue_id not in venues_ids:
            venues_ids.append(venue_id)

            venues.append(
                {
                    "name": event.get("venueName"),
                }
            )

    return venues
