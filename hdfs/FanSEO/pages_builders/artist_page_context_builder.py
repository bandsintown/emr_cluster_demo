import datetime
from datetime import datetime

CURRENT_YEAR = datetime.now().year
YEAR_RANGE_FOR_SEO = f"{CURRENT_YEAR}-{CURRENT_YEAR + 1}"
FALLBACK_IMAGE_URL = (
    "https://assets.prod.bandsintown.com/images/festival-fallback.jpg",
)



def build_template_context(row):
    """
    Build the context required to render the `artist_page` Jinja template
    (./html_templates/artist_page.py).

    A `row` has these attributes:
    * `artistId`
    * `artist`
    * `events`
    * `reviewsWithComments`
    * `reviewsWithMedia`

    You can see the schema in `./artist_pages_generator.py`
    """
    next_event = row.events[1] if row.events and len(row.events) > 1 else None

    return {
        "env": "production",
        "domain": "https://concerts.hypebot.com/",
        "artist": row.artist,
        "events": sorted(row.events, key=lambda e: e["startsAt"]) if row.events else [],
        "reviewsWithComments": (
            row.reviewsWithComments[:10] if row.reviewsWithComments else []
        ),
        "reviewsWithMedia": row.reviewsWithMedia[:10] if row.reviewsWithMedia else [],
        "similarArtists": row.similarArtists[:12] if row.similarArtists else [],
        "tourCities": build_tour_cities(row),
        "language": "en",
        "yearRange": YEAR_RANGE_FOR_SEO,
        "currentYear": CURRENT_YEAR,
        "copyrightYear": CURRENT_YEAR,
        # FAQ attributes
        "nextEvent": next_event,
        "eventsByYear": sort_events_by_year(row),
    }


def sort_events_by_year(row):
    if not row.eventsByYear:
        return []

    row.eventsByYear.sort(key=lambda e: e[0])
    for year, events in row.eventsByYear:
        events.sort(key=lambda e: e["startsAt"])

    return row.eventsByYear


def build_tour_cities(row):
    if row.events:
        tour_cities = []

        for event in row.events:
            if event.venueLocation and event.venueLocationSlug:
                city = {
                    "nameSlug": event.venueLocationSlug,
                    "name": event.venueLocation,
                }
                if city not in tour_cities:
                    tour_cities.append(city)

        return tour_cities

    return []
