

CITY_BASE_HTML = """
{% extends "application/base.html" %}
{% import "shared/media/image.html" as mediaMacro %}

{% block canonical_link %}
  <link rel="canonical" href="{{ domain }}cities/{{ genre.labelSlug }}/{{ city.nameSlug }}" />
{% endblock %}

{% block meta_description %}
  <meta
    name="description"
    content="Browse upcoming {{ genre.label | lower }} concerts in {{ city.name }}. Find local tour dates, event information, and more"
  />
{% endblock %}

{% block title %}
  Upcoming {{ genre.label }} Concerts &amp; Events in {{ city.name }} | Hypebot
{% endblock %}

{% block json_ld %}
  {% if faqNbrUpcomingEvents > 0 %}
    <script type="application/ld+json">
      {% include "city/FAQ/FAQJsonLd.njk" %}
    </script>
  {% endif %}
{% endblock %}

{% block styles %}
  <style>
    {% include "city/styles.css" %}
  </style>
{% endblock %}

{% block breadcrumbs %}
  <a href="/cities/popular/{{ city.nameSlug }}">Concerts in {{ city.name }}</a>
  &gt;
  <a href="/cities/{{ genre.labelSlug }}/{{ city.nameSlug }}">{{ genre.label }}</a>
{% endblock %}

{% block content %}
{% endblock %}

"""


CITY_GENRE_EVENTS_HTML = """
{% extends "city/base.html" %}

{% block content %}
  <div class="citySlugTitle">{{genre.label}} Concerts & Shows in {{city.name}}</div>
  <div class="cityHint">
    Know what you like? Discover upcoming {{genre.label | lower}} concerts and shows in
    {{city.name}}. From legendary {{genre.label | lower}} artists to emerging local talent, explore
    artists in your preferred genre, and check out their upcoming concerts near you. Stay updated on
    the latest {{city.name}} live music events and browse additional concert dates by genre, artist,
    and more.
  </div>

  {% include "city/genreEvents/genreEvents.njk" %}
  {% include "city/nearByCities/nearByCities.njk" %}

  {% if faqNbrUpcomingEvents > 0 %}
    {% include "city/FAQ/FAQ.njk" %}
  {% endif %}
{% endblock %}

"""


CITY_POPULAR_EVENTS_HTML = """
{% extends "city/base.html" %}

{% block content %}

  <div class="heroBanner">
    <h1 class="longHeader">{{ genre.label }} Concerts &amp; Shows in {{ city.name }}</h1>

    <div class="longHeroHint">
      Know what you like? Discover upcoming {{ genre.label | lower }} concerts and shows in {{
      city.name }}. From legendary {{ genre.label | lower }} artists to emerging local talent,
      explore artists in your preferred genre, and check out their upcoming concerts near you.
      Stay updated on the latest {{ city.city }} live music events and browse additional concert
      dates by genre, artist, and more.
    </div>
  </div>

  <div class="citySlugTitle">
    Concerts in
    <span class="cityName"> {{city.name}}</span>
  </div>

  {% if eventsPopular and eventsSellingFast %}
    {% include "city/cityEvents/cityEvents.njk" %}
  {% endif %}

  {% include "city/cityArtists/cityArtists.njk" %}
  {% include "city/nearByCities/nearByCities.njk" %}

  {% if faqNbrUpcomingEvents > 0 %}
    {% include "city/FAQ/FAQ.njk" %}
  {% endif %}

  <h2 class="gridListHeader">Upcoming popular concerts in {{ city.name }}</h2>

  {% include "city/genreEvents/genreEvents.njk" %}
{% endblock %}

"""


CITY_STYLES_CSS = """
.heroBanner{background:url(/assets/hero.webp);background-blend-mode:overlay;background-color:#d8d8d8;background-position:50%;background-position-y:83%;background-repeat:no-repeat;background-size:cover;height:211px;padding:40px 0 0 63px}h1{font-size:36px;margin-block-end:0;margin-block-start:0}.heroHint,.longHeroHint{font-size:18px;margin-top:10px}.longHeroHint{margin-right:15px}@media screen and (max-width:800px){.longHeader{font-size:22px}.longHeroHint{font-size:14px;margin-right:5px}}@media screen and (max-width:700px){.heroBanner{align-items:center;display:flex;flex-direction:column;justify-content:center;padding:0 20px}h1{font-size:32px}}@media screen and (max-width:400px){h1{font-size:22px}.heroHint,.longHeader{font-size:14px}.longHeroHint{font-size:12px}}.artist{position:relative}.artistImage img,.nameInfo{border-radius:50%;height:150px;width:150px}.nameInfo{align-items:center;background:linear-gradient(0deg,#000,transparent);color:#eee;display:flex;flex-direction:column;justify-content:center;position:absolute;top:0;z-index:10}.artistName{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;font-weight:700;margin-top:75px;max-width:116px;text-align:center}.artistList{display:flex;gap:18px;margin-bottom:30px;margin-top:30px;overflow-x:auto;width:100%}.artistList a,.artistList a:visited{color:#000;text-decoration:none}.artistList::-webkit-scrollbar-track{background-color:#f5f5f5;border-radius:6px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3)}.artistList::-webkit-scrollbar-thumb{background-color:#ccc;border-radius:6px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3)}.event{position:relative}.eventImage img{border-radius:12px;height:150px;width:150px}.nameInfoCity{align-items:center;background:linear-gradient(0deg,#000,transparent);border-bottom-left-radius:12px;border-bottom-right-radius:12px;color:#eee;display:flex;flex-direction:column;height:35px;height:52px;justify-content:center;position:absolute;top:115px;top:100px;width:100%}.eventName{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;font-weight:700;text-align:center}.eventDate{font-weight:400}.eventList{display:flex;gap:18px;margin-bottom:30px;margin-top:30px;overflow-x:auto;width:100%}.eventList::-webkit-scrollbar-track{background-color:#f5f5f5;border-radius:6px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3)}.eventList::-webkit-scrollbar-thumb{background-color:#ccc;border-radius:6px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3)}.faqLink{color:#776db1}.genreEvent{align-items:center;color:#000;display:flex;flex-direction:row;gap:20px;margin-bottom:30px;margin-right:44px;text-decoration:none}.genreEventTitle{font-size:15px;font-weight:700}.genreEventVenueName{font-size:13px;font-weight:500;margin-bottom:16px}.genreEventDateTime{margin-bottom:16px}.genreEventDateTime,.genreEventRsvpCount{align-items:center;display:flex;font-size:13px;font-weight:400;gap:5px}.genreEventImage img{border-radius:12px;height:150px;width:150px}.genreEventTitle,.genreEventVenueName{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical}.genreEventList{-moz-columns:3;column-count:3}@media screen and (max-width:1000px){.genreEventList{-moz-columns:2;column-count:2}}@media screen and (max-width:600px){.genreEventList{-moz-columns:1;column-count:1}.genreEvent{margin-right:20px}}@media screen and (max-width:400px){.genreEventImage img{border-radius:12px;height:110px;width:110px}}.gridListHeader{margin:30px 0}.nearbyCitiesContainer{margin-bottom:30px;margin-top:30px}.cityHeader{margin-bottom:30px}.cityList{align-content:center;align-items:center;display:flex;flex-wrap:wrap;gap:20px}@media screen and (max-width:400px){.cityList{align-content:unset;align-items:unset;flex-direction:column}.square{display:none}}.cityLink{color:#000;text-decoration:none}.square{background:#c4c4c4;border-radius:100px;height:15px;width:15px}.square:last-of-type{display:none}.cityGenre{text-transform:capitalize}.genreWrapper{display:flex;flex-wrap:wrap;gap:8px;margin:30px 0}.genreLink{align-items:center;border:1px solid #776db1;border-radius:20px;color:#776db1;display:flex;justify-content:center;padding:8px 16px;text-decoration:none}.active{background:#776db1;color:#fff}.sectionContainer{align-items:center;border-bottom:1px solid #c4c4c4;display:flex}.textInfoContainer{margin-right:20px;max-width:290px}h2{font-size:24px;margin-block-end:0;margin-block-start:0;margin-bottom:5px}.citySlugTitle{font-size:24px;font-weight:700;margin-top:30px}.citySlugTitle .cityName{color:#776db1;font-size:24px;font-weight:700;text-transform:capitalize}@media screen and (max-width:700px){.sectionContainer{align-items:flex-start;flex-direction:column}.textInfoContainer{margin-right:unset;max-width:unset}h2{margin-top:20px}}
"""


CITY_CITY_ARTISTS_CITY_ARTIST_NJK = """
<a class="artist" href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">
  <div class="artistImage">
    {{ mediaMacro.image(artist.mediaId, artist.name) }}
  </div>
  <div class="nameInfo">
    <div class="artistName">{{ artist.name }}</div>
  </div>
</a>

"""


CITY_CITY_ARTISTS_CITY_ARTISTS_NJK = """
<div class="sectionContainer">
  <div class="textInfoContainer">
    <h2>Top trending artists</h2>
    <div>Stay ahead of the curve with the most popular artists of the moment.</div>
  </div>
  <div class="artistList">
    {% for artist in artistsTrending %}
      {% include "city/cityArtists/cityArtist.njk" %}
    {% endfor %}
  </div>
</div>
<div class="sectionContainer">
  <div class="textInfoContainer">
    <h2>Most popular artists</h2>
    <div>Discover our curated list of today’s most popular artists loved by fans worldwide.</div>
  </div>
  <div class="artistList">
    {% for artist in artistsMostPopular %}
      {% include "city/cityArtists/cityArtist.njk" %}
    {% endfor %}
  </div>
</div>
<div class="sectionContainer">
  <div class="textInfoContainer">
    <h2>Artists on tour</h2>
    <div>Find artists currently on tour. Explore upcoming concert dates, reviews, photos, and more.</div>
  </div>
  <div class="artistList">
    {% for artist in artistsOnTour %}
      {% include "city/cityArtists/cityArtist.njk" %}
    {% endfor %}
  </div>
</div>

"""


CITY_CITY_EVENTS_CITY_EVENT_NJK = """
<a class="event" href="/artist/{{ event.artistNameFirstLetter | urlencode }}/{{ event.artistId }}-{{ event.artistNameSlug }}">
  <div class="eventImage">
    {{ mediaMacro.image(event.mediaId, event.title) }}
  </div>
  <div class="nameInfoCity">
    <div class="eventName">{{ event.title or event.artistName }}</div>
    <div class="eventDate">{{ event.date }}</div>
  </div>
</a>

"""


CITY_CITY_EVENTS_CITY_EVENTS_NJK = """
<div class="sectionContainer">
  <div class="textInfoContainer">
    <h2>Popular events</h2>
    <div>
      Explore the most popular concerts in {{city.name}}. Browse upcoming shows at your local venue.
    </div>
  </div>

  <div class="eventList">
    {% for event in eventsPopular %}
      {% include "city/cityEvents/cityEvent.njk" %}
    {% endfor %}
  </div>
</div>

<div class="sectionContainer">
  <div class="textInfoContainer">
    <h2>{{city.city}} concert tickets selling fast</h2>
    <div>
      Don't miss out on your chance to see your favorite artist. Get concert tickets while you can.
    </div>
  </div>

  <div class="eventList">
    {% for event in eventsSellingFast %}
      {% include "city/cityEvents/cityEvent.njk" %}
    {% endfor %}
  </div>
</div>

"""


CITY_GENRE_EVENTS_CALENDAR_ICON_NJK = """
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="18" viewBox="0 0 16 18" fill="none">
<path id="Vector" d="M5.5 8.16675H3.83333V9.83342H5.5V8.16675ZM8.83333 8.16675H7.16667V9.83342H8.83333V8.16675ZM12.1667 8.16675H10.5V9.83342H12.1667V8.16675ZM13.8333 2.33341H13V0.666748H11.3333V2.33341H4.66667V0.666748H3V2.33341H2.16667C1.24167 2.33341 0.508333 3.08341 0.508333 4.00008L0.5 15.6667C0.5 16.5834 1.24167 17.3334 2.16667 17.3334H13.8333C14.75 17.3334 15.5 16.5834 15.5 15.6667V4.00008C15.5 3.08341 14.75 2.33341 13.8333 2.33341ZM13.8333 15.6667H2.16667V6.50008H13.8333V15.6667Z" fill="black"/>
</svg>

"""


CITY_GENRE_EVENTS_GENRE_EVENT_NJK = """
<a class="genreEvent" href="/artist/{{ event.artistNameFirstLetter | urlencode }}/{{ event.artistId }}-{{ event.artistNameSlug }}">
  <div class="genreEventImage">
    {{ mediaMacro.image(event.mediaId, event.title) }}
  </div>
  <div class="infoContainer">
    <div class="genreEventTitle">{{ event.title or event.artistName }}</div>
    <div class="genreEventVenueName">{{ event.venueName }}</div>
    <div class="genreEventDateTime">
      {% include "city/genreEvents/calendarIcon.njk" %}
      {{ event.date }}
    </div>
    <div class="genreEventRsvpCount">
      {% include "city/genreEvents/peopleIcon.njk" %}
      {{ event.rsvpCount }}
    </div>
  </div>
</a>

"""


CITY_GENRE_EVENTS_GENRE_EVENTS_NJK = """
<div class="genreEventList">
  {% for event in eventsByGenre[genre.labelSlug] %}
    {% include "city/genreEvents/genreEvent.njk" %}
  {% else %}
    No upcoming events. Try something else
  {% endfor %}
</div>

"""


CITY_GENRE_EVENTS_PEOPLE_ICON_NJK = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="12" viewBox="0 0 20 12" fill="none">
  <path id="Vector" d="M13.7507 6.83342C12.7507 6.83342 11.1923 7.11675 10.0007 7.66675C8.80899 7.10842 7.25065 6.83342 6.25065 6.83342C4.44232 6.83342 0.833984 7.73342 0.833984 9.54175V11.8334H19.1673V9.54175C19.1673 7.73342 15.559 6.83342 13.7507 6.83342ZM10.4173 10.5834H2.08399V9.54175C2.08399 9.09175 4.21732 8.08342 6.25065 8.08342C8.28399 8.08342 10.4173 9.09175 10.4173 9.54175V10.5834ZM17.9173 10.5834H11.6673V9.54175C11.6673 9.15842 11.5007 8.82508 11.234 8.52508C11.9673 8.27508 12.8673 8.08342 13.7507 8.08342C15.784 8.08342 17.9173 9.09175 17.9173 9.54175V10.5834ZM6.25065 6.00008C7.85899 6.00008 9.16732 4.69175 9.16732 3.08342C9.16732 1.47508 7.85899 0.166748 6.25065 0.166748C4.64232 0.166748 3.33399 1.47508 3.33399 3.08342C3.33399 4.69175 4.64232 6.00008 6.25065 6.00008ZM6.25065 1.41675C7.16732 1.41675 7.91732 2.16675 7.91732 3.08342C7.91732 4.00008 7.16732 4.75008 6.25065 4.75008C5.33399 4.75008 4.58399 4.00008 4.58399 3.08342C4.58399 2.16675 5.33399 1.41675 6.25065 1.41675ZM13.7507 6.00008C15.359 6.00008 16.6673 4.69175 16.6673 3.08342C16.6673 1.47508 15.359 0.166748 13.7507 0.166748C12.1423 0.166748 10.834 1.47508 10.834 3.08342C10.834 4.69175 12.1423 6.00008 13.7507 6.00008ZM13.7507 1.41675C14.6673 1.41675 15.4173 2.16675 15.4173 3.08342C15.4173 4.00008 14.6673 4.75008 13.7507 4.75008C12.834 4.75008 12.084 4.00008 12.084 3.08342C12.084 2.16675 12.834 1.41675 13.7507 1.41675Z" fill="black"/>
</svg>

"""


CITY_NEAR_BY_CITIES_NEAR_BY_CITIES_NJK = """
<div class="nearbyCitiesContainer">
  <div class="cityHeader">
    <h2>
      More <span class="cityGenre">{{ genre.label }}</span> Concerts near {{ city.name }}
    </h2>
  </div>

  <div class="cityList">
    {% for city in city.nearbyCities %}
      <a class="cityLink" href="/cities/{{ genre.labelSlug }}/{{ city.nameSlug }}">
        {{ city.name }}
      </a>
      <div class="square"></div>
    {% endfor %}
  </div>
</div>

"""


CITY_FAQ_FAQ_NJK = """
<div class="faqContainer">
  <h2>Frequently Asked Questions About {{city.name}}</h2>

  {% if env != "production" %}
    <h3>What are the top concert venues in {{city.name}}?</h3>
    <div>
      {{city.name}} is home to iconic venues, including stadiums, amphitheaters, arenas, and intimate stages.
      Browse upcoming concerts and events at the following venues:
      <ul>
        {% for event in faqVenues %}
          <li>
            <a class="faqLink" href="/venue/{{event.nameFirstLetter | urlencode}}/{{event.id}}-{{event.nameSlug}}">
              {{event.name}}
            </a>
          </li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  <h3>Which artists are currently touring this city?</h3>
  <div>
    You'll find a variety of artists with {{city.name}} tour dates.
    Follow your favorite artists or explore new ones;
    a few notable performers touring nearby include
    {% for artist in faqArtists %}
      {# Take the first few of "top city artists" list #}
      {% if not loop.last %}
        <a class="faqLink" href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">{{artist.name}}</a>,
      {% else %}
        and <a class="faqLink" href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">{{artist.name}}</a>.
      {% endif %}
    {% endfor %}
  </div>

  <h3>How many upcoming concerts are there happening in {{city.name}}?</h3>
  <div>
    Currently, {{faqNbrUpcomingEvents}} upcoming events are scheduled in {{city.name}}
    {% if env != "production" %}
      {% if faqNbrUpcomingEvents > 0 and faqVenues %}
        at venues like

        <a class="faqLink" href="/venue/{{(faqVenues|first).nameFirstLetter | urlencode}}/{{(faqVenues|first).id}}-{{(faqVenues|first).nameSlug}}">{{(faqVenues|first).name}}</a>
      {% endif %}

      {% if faqVenues|length > 1 %}
        and <a class="faqLink" href="/venue/{{(faqVenues|last).nameFirstLetter | urlencode}}/{{(faqVenues|last).id}}-{{(faqVenues|last).nameSlug}}">{{(faqVenues|last).name}}</a>.
      {% endif %}
    {% endif %}

    Browse tour dates and buy concert tickets to a show near you with Hypebot.
  </div>

</div>

"""


CITY_FAQ_FAQ_JSON_LD_NJK = """
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What are the top concert venues in {{city.name | escape}}?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text":
          "{{city.name | escape}} is home to iconic venues, including stadiums, amphitheaters, arenas, and intimate stages.  Browse upcoming concerts and events at the following venues:  {% for venue in faqVenues %} {{venue.name | escape}}{% if not loop.last %}, {% endif %}{% endfor %}."
      }
    },
    {
      "@type": "Question",
      "name": "Which artists are currently touring this city?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "You'll find a variety of artists with {{city.name | escape}} tour dates. Follow your favorite artists or explore new ones;  a few notable performers touring nearby include {% for artist in faqArtistsInCity %}{{artist.name | escape}}{% if not loop.last %}, {% endif %}{% endfor %}."
      }
    },
    {
      "@type": "Question",
      "name": "How many upcoming concerts are there happening in {{city.name | escape}}?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Currently, {{faqNbrUpcomingEvents}} upcoming events are scheduled in {{city.name | escape}}{% if faqNbrUpcomingEvents > 0 and faqVenues %} at venues like {{(faqVenues|first).name | escape}}{% if faqVenues|length > 1 %} and {{(faqVenues|last).name | escape}}{% endif %}{% endif %}. Browse tour dates and buy concert tickets to a show near you with Hypebot."
      }
    }
  ]
}

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
    "city/base.html": CITY_BASE_HTML,
    "city/genre_events.html": CITY_GENRE_EVENTS_HTML,
    "city/popular_events.html": CITY_POPULAR_EVENTS_HTML,
    "city/styles.css": CITY_STYLES_CSS,
    "city/cityArtists/cityArtist.njk": CITY_CITY_ARTISTS_CITY_ARTIST_NJK,
    "city/cityArtists/cityArtists.njk": CITY_CITY_ARTISTS_CITY_ARTISTS_NJK,
    "city/cityEvents/cityEvent.njk": CITY_CITY_EVENTS_CITY_EVENT_NJK,
    "city/cityEvents/cityEvents.njk": CITY_CITY_EVENTS_CITY_EVENTS_NJK,
    "city/genreEvents/calendarIcon.njk": CITY_GENRE_EVENTS_CALENDAR_ICON_NJK,
    "city/genreEvents/genreEvent.njk": CITY_GENRE_EVENTS_GENRE_EVENT_NJK,
    "city/genreEvents/genreEvents.njk": CITY_GENRE_EVENTS_GENRE_EVENTS_NJK,
    "city/genreEvents/peopleIcon.njk": CITY_GENRE_EVENTS_PEOPLE_ICON_NJK,
    "city/nearByCities/nearByCities.njk": CITY_NEAR_BY_CITIES_NEAR_BY_CITIES_NJK,
    "city/FAQ/FAQ.njk": CITY_FAQ_FAQ_NJK,
    "city/FAQ/FAQJsonLd.njk": CITY_FAQ_FAQ_JSON_LD_NJK,
    "application/base.html": APPLICATION_BASE_HTML,
    "application/footer.html": APPLICATION_FOOTER_HTML,
    "application/header.html": APPLICATION_HEADER_HTML,
    "application/styles.css": APPLICATION_STYLES_CSS,
    "shared/styles.css": SHARED_STYLES_CSS,
    "shared/media/image.html": SHARED_MEDIA_IMAGE_HTML
}