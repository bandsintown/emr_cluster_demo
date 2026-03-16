

ARTIST_ARTIST_PAGE_NJK = """
{% extends "application/base.html" %}
{% import "shared/media/image.html" as mediaMacro %}

{% block canonical_link %}
  <link rel="canonical" href="{{ domain }}artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">
{% endblock %}

{% block meta_description %}
  <meta name="description" content="Find tickets for {{artist.name}} concerts near you. Browse {{yearRange}} tour dates, artist information, reviews, photos, and more.">
{% endblock %}

{% block title %}
  {{artist.name}} Concert Tour Dates &amp; Shows: {{yearRange}} Tickets | Hypebot
{% endblock %}

{% block json_ld %}
  <script type="application/ld+json">
    {% include "artist/components/eventsJsonLd.njk" %}
  </script>

  <script type="application/ld+json">
    {% include "artist/components/artistJsonLd.njk" %}
  </script>

  <script type="application/ld+json">
    {% include "artist/components/FAQJsonLd.njk" %}
  </script>
{% endblock %}

{% block styles %}
  <style>
    {% include "artist/styles.css" %}
  </style>
{% endblock %}

{% block scripts %}
  <script type="text/javascript">
    window.addEventListener('DOMContentLoaded', function(){
      // will not show reviews if there are less than 8
      // since we are hiding the first 3 reviews
      if ("{{ reviewsWithComments | length }}" <= 8) {
        return document.getElementById('showMore').style.display = "none";
      }
      document.getElementById("showMore").addEventListener('click', async event => {
        const hideElements = document.getElementsByClassName("hide")
        if(hideElements) {
          Object.keys(hideElements).forEach(key => {
            hideElements[key].style.display = "block";
          });
        }
        document.getElementById("showMore").style.display = "none";
      });
    }, false);
  </script>
{% endblock %}

{% block breadcrumbs %}
  <a href="/search/artists/{{ artist.nameFirstLetter | urlencode }}">
    Artists Starting with {{ "#" if artist.nameFirstLetter == "%23" else artist.nameFirstLetter | upper }}
  </a>
  &gt;
  <a href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">
    {{artist.name}} Upcoming Concerts
  </a>
{% endblock %}

{% block content %}
  <div class="topSection">
    <div class="artistImage">
      {{ mediaMacro.image(artist.mediaId, artist.name) }}
    </div>
    <div class="rightColumn">
      {% if artist.dead %}
        <div>
          <h1>{{artist.name}}</h1>
          <div class="artistDesc">
            {{ artist.formattedBio }}
          </div>
        </div>
      {% else %}
        <div>
          <h1>{{artist.name}} Tour Dates and Upcoming Concerts</h1>
          <div class="artistDesc">
            Welcome to the official artist page for {{artist.name}} – your premier destination for
            the latest concert tickets, tour announcements, and exclusive shows near you. Dive into
            the music, explore the artist’s reviews and photos, and never miss another concert
            moment. Stay updated, stay connected, and be the first to grab tickets for an
            unforgettable musical experience.
          </div>
        </div>
      {% endif %}
      <div class="artistInfo">
        <div class="infoSpan">
          <span class="type">On tour</span>
          {% if artist.onTour and events %}
            <span class="onTour">Yes</span>
          {% else %}
            <span class="onTour">No</span>
          {% endif %}
        </div>
        <div class="infoSpan">
          <span class="type">Followers</span>
          <span class="follower">{{ "{:,}".format(artist.trackerCount) }}</span>
        </div>
        {% if artist.genres %}
          <div class="infoSpan">
            <span class="type">Category</span>
            <span class="category">{{ artist.genres | join(", ") }}</span>
          </div>
        {% endif %}
      </div>
    </div>
  </div>

  <div class="eventList">
    {% if events %}
      <div>
        <div class="sectionHeader">Concerts</div>
        <p>
          See all upcoming events on <a class="artistLink" href="https://www.bandsintown.com/a/{{artist.id}}-{{artist.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=artist">Bandsintown</a> and get tickets.
        </p>
        {# {% for event in events %}
          {% include "artist/components/event/event.njk" %}
        {% endfor %} #}
      </div>
    {% else %}
      {% if similarArtists %}
        <div class="sectionHeader">Similar Artists On Tour</div>
        <div class="similarArtistsWrapper">
          {% for artist in similarArtists %}
            {% include "artist/components/similarArtists/similarArtists.njk" %}
          {% endfor %}
        </div>
      {% endif %}
    {% endif %}
  </div>

  <div class="sectionHeader">About {{artist.name}}</div>
  <div class="artistBio">{{ artist.formattedBio }}</div>
  <a class="followArtist" href="https://www.bandsintown.com/a/{{artist.id}}-{{artist.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=artist&trigger=follow">
    Follow on Bandsintown
    <img src="/assets/arrowRight.svg">
  </a>

  {% if artist.genres %}
    <div class="sectionHeader">Genres</div>
    <div>{{ artist.genres | join(", ") }}</div>
  {% endif %}

  {% if artist.bandMembers %}
    <div class="sectionHeader">Band members</div>
    <div>{{ artist.bandMembers | join(", ", "name")}}</div>
  {% endif %}

  {% if reviewsWithMedia %}
    <div class="sectionHeader">Photos</div>
    <div class="livePhotosWrapper">
      {% for review in reviewsWithMedia %}
        <img class="livePhoto" src="https://media.bandsintown.com/300x300/{{review.mediaId}}.webp" alt="concert photo" />
      {% endfor %}
    </div>
  {% endif %}

  {% if reviewsWithComments %}
    <div class="sectionHeader">What fans are saying</div>
    <div class="reviewsWrapper">
      {% for review in reviewsWithComments %}
        {% if (loop.index > 0 and loop.index < 14) or loop.length <= 3  %}
          {% include "artist/components/artistReview/artistReview.njk" %}
        {% endif %}
      {% endfor %}

      <button id="showMore">Show More Reviews</button>
    </div>
  {% endif %}

  {% if events and similarArtists %}
    <div class="sectionHeader">Similar Artists On Tour</div>
    <div class="similarArtistsWrapper">
      {% for artist in similarArtists %}
        {% include "artist/components/similarArtists/similarArtists.njk" %}
      {% endfor %}
    </div>
  {% endif %}

  {% if tourCities %}
    <div class="sectionHeader">{{artist.name}} Tour Cities</div>
    <div class="tourCitiesWrapper">
      {% for city in tourCities %}
        <a class="tourCity" href="/cities/popular/{{city.nameSlug}}">
          {{ city.name }}
        </a>
      {% endfor %}
    </div>
  {% endif %}

  {% include "artist/components/FAQ/FAQ.njk" %}
{% endblock %}

"""


ARTIST_STYLES_CSS = """
.heroBanner{background:url(/assets/hero.webp);background-blend-mode:overlay;background-color:#d8d8d8;background-position:50%;background-position-y:83%;background-repeat:no-repeat;background-size:cover;height:211px;padding:40px 0 0 63px}h1{font-size:36px;margin-block-end:0;margin-block-start:0}.heroHint,.longHeroHint{font-size:18px;margin-top:10px}.longHeroHint{margin-right:15px}@media screen and (max-width:800px){.longHeader{font-size:22px}.longHeroHint{font-size:14px;margin-right:5px}}@media screen and (max-width:700px){.heroBanner{align-items:center;display:flex;flex-direction:column;justify-content:center;padding:0 20px}h1{font-size:32px}}@media screen and (max-width:400px){h1{font-size:22px}.heroHint,.longHeader{font-size:14px}.longHeroHint{font-size:12px}}.reviewWrapper{align-items:flex-start;border-bottom:2px solid #ccc;display:flex;flex-direction:column;font-variant-numeric:lining-nums proportional-nums;gap:2px;margin-bottom:30px;padding-bottom:30px}.userFirstName{font-weight:700}.venueLocation,.venueName{color:#000;display:block;font-weight:700;text-decoration:none;width:-moz-fit-content;width:fit-content}.venueLocation{font-weight:400}.reviewDate{color:#666}.show{display:block}.hide{display:none}.concertRow{background-color:#e7e7e7;color:#000;cursor:pointer;display:flex;flex-wrap:wrap;gap:20px;margin-bottom:7px;padding:16px;text-decoration:none}.concertRow:hover{background-color:#fff}.date{display:table-cell;font-weight:400;text-align:center;vertical-align:middle}.month{font-size:11px;text-transform:uppercase}.day{font-size:25px}.location,.title{font-size:18px;font-style:normal;font-weight:700;line-height:normal}.location{font-weight:400}.titleLocation{flex:1;min-width:200px}.ticketButton{align-items:center;background:#776db1;border-radius:100px;color:#fff;cursor:pointer;display:flex;font-size:16px;font-style:normal;font-weight:700;justify-content:center;line-height:19px;text-align:center;text-decoration:none;text-transform:capitalize;transition:background-color .3s,color .3s;width:-moz-fit-content;width:fit-content}.ticketButton:hover{opacity:.8}.ticketButton span{font-weight:400;padding:10px 36px}.textSection{font-size:18px;font-weight:700;margin-top:30px;text-decoration:underline}.venueRow{line-height:2rem}.similarArtistWrapper{align-items:center;color:#000;display:flex;flex-direction:column;margin:0 20px 20px 0;text-decoration:none;@media screen and (max-width:700px){flex-direction:row;gap:30px}}.similarArtistWrapper:hover{opacity:.8}.similarArtistImage{border-radius:100px;height:150px;width:150px;@media screen and (max-width:700px){height:50px;width:50px}}.similarArtistName{font-weight:700;margin-top:10px;@media screen and (max-width:700px){font-size:20px;font-weight:400;margin-top:0}}.topSection{display:flex;gap:20px;margin-top:50px}.topSection h1{font-size:24px;font-style:normal;font-weight:700;line-height:normal}.artistImage img{border-radius:100px;height:200px;width:200px}.rightColumn{display:flex;flex-direction:column;justify-content:center}.artistDesc{font-size:18px;font-style:normal;font-weight:400;line-height:normal}.artistInfo{display:flex;flex-direction:row;font-weight:700;gap:20px;margin:20px 0}.infoSpan{display:flex;flex-wrap:wrap;gap:5px}.type{line-height:1.3}.category,.follower,.onTour{color:#776db1;display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.3;max-width:610px}.sectionHeader{font-size:22px;font-style:italic;font-weight:400;margin:30px 0}.livePhotosWrapper{display:flex;overflow-x:scroll}.livePhoto{height:300px;margin-right:10px;width:300px}.similarArtistsWrapper{display:flex;flex-wrap:wrap;@media screen and (max-width:700px){flex-direction:column}}.tourCitiesWrapper{display:flex;flex-wrap:wrap}.tourCity{border:1px solid #776db1;border-radius:50px;color:#776db1;cursor:pointer;margin:0 10px 15px 0;padding:10px 20px;text-decoration:none;text-transform:capitalize}.tourCity:hover{background-color:#776db1;color:#fff;cursor:pointer}.artistBio{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.56}.artistLink{color:#776db1;text-decoration:none}#showMore,.followArtist{align-items:center;color:#776db1;cursor:pointer;display:flex;margin-top:10px;text-decoration:none}#showMore{background:none;border:none;font:inherit;outline:inherit;padding:0}@media screen and (max-width:700px){.topSection{flex-wrap:wrap}.artistInfo{flex-direction:column}}
"""


ARTIST_COMPONENTS_FAQ_JSON_LD_NJK = """
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Is {{artist.name | escape}} on tour?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text":
          {% if artist.onTour and events %}
            "Yes, {{artist.name | escape}} is currently on tour. If you’re interested in attending an upcoming {{artist.name | escape}} concert, make sure to grab your tickets in advance. The {{artist.name | escape}} tour is scheduled for {{events | length}} dates across {{tourCities | length}} cities. Get information on all upcoming tour dates and tickets for {{yearRange}} with Hypebot."
          {% else %}
            "No, {{artist.name | escape}} is not currently on tour and doesn’t have any tour dates scheduled for {{yearRange}}. Browse related artists and follow {{artist.name | escape}} for the latest updates on upcoming concert tours."
          {% endif %}
      }
    }
    {% if artist.onTour and events %}
      ,{
        "@type": "Question",
        "name": "How many upcoming tour dates is {{artist.name | escape}} scheduled to play?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "{{artist.name | escape}} is scheduled to play {{events | length}} shows between {{yearRange}}. Buy concert tickets to a nearby show through Hypebot."
        }
      }
      ,{
        "@type": "Question",
        "name": "When does the {{artist.name | escape}} tour start?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "{{artist.name | escape}}’s tour starts {{(events | first).date}} and ends on {{(events | last).date}}.  They will play {{tourCities | length}} cities; their most recent concert was held in {{(events | first).city}} at {{(events | first).venueName | escape }} and their next upcoming concert will be in {{nextEvent.city}} at {{nextEvent.venueName | escape}}."
        }
      }
      ,{
        "@type": "Question",
        "name": "What venues is {{artist.name | escape}} performing at?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "As part of the {{artist.name | escape}} tour, {{artist.name | escape}} is scheduled to play across the following venues and cities: {% if events and eventsByYear %} {% for year, events in eventsByYear %} <h4>{{year}} Tour Dates:</h4><ul> {% for event in events %} <li>{{ event.month}} {{event.day}} - {{ event.city }}, {{ event.region or event.venueCountry }} @ {{ event.venueName | escape}}</li>{% endfor %}</ul>{% endfor %}{% endif %}"
        }
      }
    {% endif %}
    ,{
      "@type": "Question",
      "name": "On average, how much are {{artist.name | escape}} ticket prices?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{artist.name | escape}} concert ticket prices range from {{priceRange}}, depending on the city and venue. The average ticket price is {{averagePrice}}."
      }
    }
    {% if artist.onTour and events %}
      ,{
        "@type": "Question",
        "name": "Where can I buy {{artist.name | escape}} concert tickets",
        "acceptedAnswer": {
          "@type": "Answer",
          "text": "{{artist.name | escape}} tickets are on sale from the following verified sellers: Ticketmaster, Livenation, etc. Secure your tickets in advance before they sell out!"
        }
      }
      ,{
        "@type": "Question",
        "name": "Are {{artist.name | escape}} concert tickets sold out?",
        "acceptedAnswer": {
          "@type": "Answer",
          "text":
          {% if isSoldOut %}
            "Yes, concert tickets for upcoming {{artist.name | escape}} shows are currently sold out from official, verified ticket sellers. In the meantime, browse similar artists with {{yearRange}} tour dates in nearby venues."
          {% else %}
            "Concert tickets are still available for upcoming {{artist.name | escape}} shows from verified ticket sellers. Don’t miss your chance to see {{artist.name | escape}} live in concert; buy tickets in advance!"
          {% endif %}
        }
      }
    {% endif %}
  ]
}

"""


ARTIST_COMPONENTS_ARTIST_JSON_LD_NJK = """
{
  "@context": "http://schema.org",
  "@type": "MusicGroup",
  "name": "{{ artist.name | escape }}"
  {% if artist.hometown -%}
    ,"location": { "@type": "Place", "name": "{{ artist.hometown | escape }}" }
  {%- endif %}
  {% if artist.genres -%}
    ,"genre": "{{ artist.genres | join(", ") }}"
  {%- endif %}
  {% if artist.links -%}
    ,"sameAs": "{{ artist.links[0].link }}"
  {%- endif %}
  {% if artist.bandMembers -%}
      ,"employees": { "@type": "Person", "name": "{{ artist.bandMembers | join(", ", "name")  | escape }}" }
  {%- endif %}
  {% if artist.trackerCount -%}
      ,"interactionCount": "{{ "{:,}".format(artist.trackerCount) }} Followers"
  {%- endif %}
}

"""


ARTIST_COMPONENTS_EVENTS_JSON_LD_NJK = """
{% if events %}
  [
    {% for event in events %}
      {
        "@context": "http://schema.org",
        "@type": "MusicEvent",
        "name": "{{(event.title or artist.name) | escape}} @ {{event.venueName | escape }}",
        "startDate": "{{ event.startsAt or "" }}",
        "endDate": "{{ event.endsAt or "" }}",
        "url": "https://www.bandsintown.com/e/{{event.id}}-{{artist.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=event",
        "location": {
          "@type": "Place",
          "name": "{{event.venueName | escape }}",
          "address": {
            "@type": "PostalAddress",
            "addressRegion": "{{event.region | escape }}",
            "addressLocality": "{{event.city | escape  }}",
            "streetAddress": "{{event.venueAddress | escape }}",
            "postalCode": "{{event.postalCode }}"
          },
          "geo": {
            "@type": "GeoCoordinates",
            "latitude": "{{event.latitude}}",
            "longitude": "{{event.longitude}}"
          }
        },
        "performer": {
          "@type": "PerformingGroup",
          "name": "{{ (artist.name or 'Anonymous') | escape }}"
        },
        "description": "{{ (event.title or artist.name or 'Anonymous') | escape }}",
        "image":
          {% if event.mediaId %}
            "https://photos.bandsintown.com/thumb/{{event.mediaId}}.jpeg"
          {% else %}
            "https://assets.prod.bandsintown.com/images/festival-fallback.jpg"
          {% endif %},
        "eventAttendanceMode":
          {% if event.streamingEvent -%}
            "http://schema.org/OnlineEventAttendanceMode"
          {% else %}
            "http://schema.org/OfflineEventAttendanceMode"
          {%- endif %},
        "eventStatus": "http://schema.org/EventScheduled",
        "offers": {
          "@type": "Offer",
          "url": "https://www.bandsintown.com/e/{{event.id}}-{{artist.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=event",
          "availability": "https://schema.org/InStock",
          "validFrom": "{{event.announcedAt}}",
          "price": 65,
          "priceCurrency": "USD"
        },
        "organizer": {
          "@type": "Organization",
          "name": "{{ (artist.name or 'anonymous') | escape }}",
          "url": "https://www.bandsintown.com/a/{{artist.id}}-{{artist.nameSlug}}?came_from=900"
        }
      }{{ "," if not loop.last }}
    {% endfor %}
  ]
{% endif %}

"""


ARTIST_COMPONENTS_ARTIST_REVIEW_ARTIST_REVIEW_NJK = """
{% set reviewClass = ('show' if loop.index <=5 else 'hide') %}

<div class="reviewWrapper {{ reviewClass }}">
  <div class="userFirstName">{{ review.userFirstName or "Anonymous" }}</div>
  <div class="rating">{{ review.rating }} / 5</div>
  <div class="comment">{{ review.comment | escape }}</div>

  {% if review.venueName %}
    <a class="venueName" href="https://www.bandsintown.com/v/{{review.venueId}}-{{review.venueNameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=venue">
      {{ review.venueName }}
    </a>
  {% endif %}

  {% if review.venueLocation %}
    <a class="venueLocation" href="/cities/popular/{{review.venueLocationSlug}}">
      {{ review.venueLocation }}
    </a>
  {% endif %}

  <div class="reviewDate">{{ review.date }}</div>
</div>

"""


ARTIST_COMPONENTS_EVENT_EVENT_NJK = """
<script type="text/javascript">
  window.addEventListener('DOMContentLoaded', function(){
    document.getElementById("{{ event.id }}").addEventListener('click', async event => {
      event.preventDefault();
      window.open("https://www.bandsintown.com/t/{{ event.id }}?came_from=900&utm_medium=web&&utm_source=static-site-hypebot&utm_campaign=ticket");
    });
  }, false);
</script>

{% if artist %}
<a class="concertRow" href="https://www.bandsintown.com/e/{{event.id}}-{{artist.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=event">
{% elif venue %}
<a class="concertRow" href="https://www.bandsintown.com/e/{{event.id}}-{{venue.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=event">
{% else %}
<a class="concertRow" href="https://www.bandsintown.com/e/{{event.id}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=event">
{% endif %}
  <div class="date">
    <div class="month">{{ event.month }}</div>
    <div class="day">{{ event.day }}</div>
  </div>
  <div class="titleLocation">
    <div class="title">
      {# If we're on the artist page, show event's venue name  #}
      {% if artist %}
        {{ event.title or event.venueName }}
      {# If we're on the venue page, show the event's artist name  #}
      {% elif venue %}
        {{ event.title or event.artistName}}
      {# Fallback to repeating venue name in weird cases #}
      {% else %}
        {{ event.title or event.venueName }}
      {% endif %}
    </div>
    <div class="location">{{ event.city }}</div>
  </div>
  <div class="tickets">
    <div class="ticketButton" id="{{ event.id }}">
      <span>Tickets</span>
    </div>
  </div>
</a>

"""


ARTIST_COMPONENTS_FAQ_FAQ_NJK = """
<div>
  <h2>Frequently Asked Questions About {{artist.name}}</h2>
  <div class="textSection">Concerts &amp; Tour Date Information</div>
  <h3>Is {{artist.name}} on tour?</h3>

  <div>
    {% if artist.onTour and events %}
      Yes, {{artist.name}} is currently on tour. If you’re interested in attending an upcoming
      {{artist.name}} concert, make sure to grab your tickets in advance. The {{artist.name}} tour
      is scheduled for {{events | length}} dates across {{tourCities | length}} cities. Get
      information on all upcoming tour dates and tickets for {{yearRange}} with Hypebot.
    {% else %}
      No, {{artist.name}} is not currently on tour and doesn’t have any tour dates scheduled for
      {{yearRange}}. Browse related artists and follow {{artist.name}} for the latest updates on
      upcoming concert tours.
    {% endif %}
  </div>

  {% if artist.onTour and events %}
    <h3>How many upcoming tour dates is {{artist.name}} scheduled to play?</h3>
    <div>
      {{artist.name}} is scheduled to play {{events | length}} shows between {{yearRange}}. Buy
      concert tickets to a nearby show through Hypebot.
    </div>

    <h3>When does the {{artist.name}} tour start?</h3>
    <div>
      {{artist.name}}’s tour starts {{(events | first).date}} and ends on {{(events | last).date}}.
      They will play {{tourCities | length}} cities; their most recent concert was held in
      {{(events | first).city}} at {{(events | first).venueName}} and their next upcoming concert
      will be in {{nextEvent.city}} at {{nextEvent.venueName}}.
    </div>

    {# <h3>What venues is {{artist.name}} performing at?</h3>
    <div>
      As part of the {{artist.name}} tour, {{artist.name}} is scheduled to play across the following
      venues and cities: #}

      {# EVENT LIST #}
      {# <div class="eventList">
        {% if events and eventsByYear %}
          {% for year, events in eventsByYear %}
            <div>
              <h4>{{year}} Tour Dates:</h4>
              {% for event in events %}
                <div class="venueRow">
                  {{event.month}} {{event.day}} - {{event.city}},
                  {{event.region or event.venueCountry}} @ {{ event.venueName }}
                </div>
              {% endfor %}
            </div>
          {% endfor %}
        {% endif %}
      </div>
    </div> #}
  
  {% endif %}

  {% if ticketData %}
  <div class="textSection">Ticket Information</div>
  <h3>On average, how much are {{artist.name}} ticket prices?</h3>
  <div>
    {{artist.name}} concert ticket prices range from {{priceRange}}, depending on the city and
    venue. The average ticket price is {{averagePrice}}.
  </div>
  {% if artist.onTour and events %}
    <h3>Where can I buy {{artist.name}} concert tickets</h3>
    <div>
      {{artist.name}} tickets are on sale from the following verified sellers: Ticketmaster,
      Livenation, etc.  Secure your tickets in advance before they sell out!
    </div>

    <h3>Are {{artist.name}} concert tickets sold out?</h3>
    <div>
      {% if isSoldOut %}
        Yes, concert tickets for upcoming {{artist.name}} shows are currently sold out from
        official, verified ticket sellers.  In the meantime, browse similar [genre] artists with
        {{yearRange}} tour dates in nearby venues.
      {% else %}
        Concert tickets are still available for upcoming {{artist.name}} shows from verified ticket
        sellers.  Don’t miss your chance to see {{artist.name}} live in concert; buy tickets in
        advance!
      {% endif %}
    </div>
  {% endif %}
  {% endif %}
</div>

"""


ARTIST_COMPONENTS_SIMILAR_ARTISTS_SIMILAR_ARTISTS_NJK = """
<a class="similarArtistWrapper" href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">
  {{ mediaMacro.image(artist.mediaId, artist.name, 'similarArtistImage') }}
  <div class="similarArtistName">{{ artist.name }}</div>
</a>

"""


APPLICATION_BASE_HTML = """
<!doctype html>
<html lang="en">
  <head>
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
    new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    })(window,document,'script','dataLayer','GTM-WNPXLRJQ');</script>
    <!-- End Google Tag Manager -->

    {% block canonical_link %}
    {% endblock %}

    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />

    {% block meta_description %}{% endblock %}

    <title>{% block title %}{% endblock %}</title>

    {% block json_ld %}{% endblock %}
    <style>
      {% include "application/styles.css" %}
    </style>
    {% block styles %}{% endblock %}
    {% block scripts %}{% endblock %}
  </head>

  <body>
    <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WNPXLRJQ"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

    <div class="main">
      {% include "application/header.html" %}

      <div class="breadcrumbs">{% block breadcrumbs %}{% endblock %}</div>

      {% block hero %}{% endblock %}

      {% block content %}{% endblock %}
    </div>

    {% include "application/footer.html" %}
  </body>
</html>

"""


APPLICATION_FOOTER_HTML = """
<div class="footerWrapper">
  {% if footerArtists %}
    <div class="footerArtists">
      <div class="columnTitle">Artists</div>
      <div class="columns-2">
        {% for artist in footerArtists %}
          <a class="footerLink" href="/artist/{{artist.nameFirstLetter | urlencode}}/{{artist.id}}-{{artist.nameSlug}}">
            {{ artist.name }}
          </a>
        {% endfor %}
      </div>
    </div>
  {% endif %}

  {% if footerCities %}
    <div class="footerCities">
      <div class="columnTitle">Cities</div>
      <div class="columns-2">
        {% for city in footerCities %}
          <a class="cityfooterLink" href="/cities/popular/{{city.nameSlug}}">
            {{ city.name }}
          </a>
        {% endfor %}
      </div>
    </div>
  {% endif %}

  {% if footerVenues %}
    <div class="footerArtists">
      <div class="columnTitle">Venues</div>
      <div class="columns-2">
        {% for venue in footerVenues %}
          <a class="footerLink" href="/venue/{{ venue.nameFirstLetter | urlencode }}/{{venue.id}}-{{venue.nameSlug}}">
            {{ venue.name }}
          </a>
        {% endfor %}
      </div>
    </div>
  {% endif %}

  <div class="footerColumn">
    <div class="aboutSection">
      <div class="columnTitle">&nbsp;</div>
      <a class="aboutBandsintown" href="https://www.hypebot.com/">© {{currentYear}} Hypebot</a>
      <a class="aboutBandsintown" href="https://www.bandsintown.com?came_from=900">Powered by Bandsintown</a>
      <a class="aboutBandsintown" href="https://corp.bandsintown.com/terms" target="_blank">Terms and Conditions</a>
      <a class="aboutBandsintown" href="https://corp.bandsintown.com/privacy" target="_blank">Privacy Policy</a>
    </div>
  </div>
</div>

"""


APPLICATION_HEADER_HTML = """
<div class="headerWrapper">
  <a href="/" class="logo" aria-label="Find more about Hypebot">
    <img
      alt="Hypebot image"
      src="https://sp-ao.shortpixel.ai/client/to_webp,q_lossy,ret_img/https://www.hypebot.com/wp-content/themes/revenue/assets/img/logo.png"
    />
  </a>

  <div>
    <div class="browseByLetterHint">Artist Search: Browse by Artist Name</div>
    <div class="letterList">
      {% for letter in ["a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","#"] %}
        <a class="letterLink" href="/search/artists/{{letter | urlencode}}">{{letter}}</a>
      {% endfor %}
    </div>
  </div>
</div>

"""


APPLICATION_STYLES_CSS = """
html{color:#000;font-family:Roboto,Helvetica,sans-serif;font-size:16px}body{margin:unset}.main{margin:20px auto;max-width:1080px;padding:30px}@media screen and (max-width:700px){.main{padding:15px}}.headerWrapper{align-items:center;border-bottom:2px solid #ccc;display:flex;flex-wrap:wrap;padding-bottom:20px}.headerWrapper img{height:76px;margin-bottom:11px;margin-right:11px;width:226px}.letterLink{color:#686295;font-size:20px;font-weight:700;text-decoration:none;text-transform:uppercase}.letterList{display:flex;flex-wrap:wrap;gap:10px}.browseByLetterHint{font-size:18px;font-weight:700;margin-bottom:8px;margin-left:3px}.logo{margin-right:25px}.breadcrumbs{margin-top:30px}.breadcrumbs a{color:#776db1}.footerWrapper{align-content:flex-start;align-items:flex-start;align-self:stretch;background-color:#eee;-moz-columns:3;column-count:3;display:flex;gap:20px;justify-content:center;padding:50px}@media screen and (max-width:640px){.footerWrapper{-moz-columns:1;column-count:1;flex-direction:column;gap:8px;padding:15px}}.footerColumn{width:300px}.columns,.columns-1{-moz-columns:1;column-count:1}.columns-2{-moz-columns:2;column-count:2}.columns-3{-moz-columns:3;column-count:3;@media only screen and (max-width:750px){-moz-columns:1;column-count:auto;column-count:1}}.columnTitle{font-size:20px;font-weight:700;margin-bottom:10px}.cityfooterLink,.footerLink{color:#000;display:block;margin-bottom:5px;text-decoration:none;width:-moz-fit-content;width:fit-content}.footerLink:hover{text-decoration:underline}.cityfooterLink{text-transform:capitalize}.aboutBandsintown{color:#000;display:block;margin-bottom:10px;text-decoration:none}a.aboutBandsintown:hover{text-decoration:underline}
"""


SHARED_STYLES_CSS = """
.heroBanner{background:url(/assets/hero.webp);background-blend-mode:overlay;background-color:#d8d8d8;background-position:50%;background-position-y:83%;background-repeat:no-repeat;background-size:cover;height:211px;padding:40px 0 0 63px}h1{font-size:36px;margin-block-end:0;margin-block-start:0}.heroHint,.longHeroHint{font-size:18px;margin-top:10px}.longHeroHint{margin-right:15px}@media screen and (max-width:800px){.longHeader{font-size:22px}.longHeroHint{font-size:14px;margin-right:5px}}@media screen and (max-width:700px){.heroBanner{align-items:center;display:flex;flex-direction:column;justify-content:center;padding:0 20px}h1{font-size:32px}}@media screen and (max-width:400px){h1{font-size:22px}.heroHint,.longHeader{font-size:14px}.longHeroHint{font-size:12px}}
"""


SHARED_MEDIA_IMAGE_HTML = """
{% macro image(mediaId, alt = "", class = "") %}

{% if mediaId %}
  <picture>
    <source
      type="image/webp"
      srcset="https://media.bandsintown.com/150x150/{{mediaId}}.webp"
    />
    <img
      class="{{class}}"
      src="https://media.bandsintown.com/150x150/{{mediaId}}.jpg"
      alt="{{alt | escape}}" />
  </picture>
{% else %}
<picture>
  <source
    type="image/webp"
    srcset="/assets/placeHolder.webp"
  />
  <img
    class="{{class}}"
    src="/assets/placeHolder.png"
    alt="{{ alt | escape }}" />
</picture>

{% endif %}
{% endmacro %}

"""

TEMPLATES = {
    "artist/artistPage.njk": ARTIST_ARTIST_PAGE_NJK,
    "artist/styles.css": ARTIST_STYLES_CSS,
    "artist/components/FAQJsonLd.njk": ARTIST_COMPONENTS_FAQ_JSON_LD_NJK,
    "artist/components/artistJsonLd.njk": ARTIST_COMPONENTS_ARTIST_JSON_LD_NJK,
    "artist/components/eventsJsonLd.njk": ARTIST_COMPONENTS_EVENTS_JSON_LD_NJK,
    "artist/components/artistReview/artistReview.njk": ARTIST_COMPONENTS_ARTIST_REVIEW_ARTIST_REVIEW_NJK,
    "artist/components/event/event.njk": ARTIST_COMPONENTS_EVENT_EVENT_NJK,
    "artist/components/FAQ/FAQ.njk": ARTIST_COMPONENTS_FAQ_FAQ_NJK,
    "artist/components/similarArtists/similarArtists.njk": ARTIST_COMPONENTS_SIMILAR_ARTISTS_SIMILAR_ARTISTS_NJK,
    "application/base.html": APPLICATION_BASE_HTML,
    "application/footer.html": APPLICATION_FOOTER_HTML,
    "application/header.html": APPLICATION_HEADER_HTML,
    "application/styles.css": APPLICATION_STYLES_CSS,
    "shared/styles.css": SHARED_STYLES_CSS,
    "shared/media/image.html": SHARED_MEDIA_IMAGE_HTML
}
