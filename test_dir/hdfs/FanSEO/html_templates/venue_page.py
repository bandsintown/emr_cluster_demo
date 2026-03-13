

VENUE_STYLES_CSS = """
.heroBanner{background:url(/assets/hero.webp);background-blend-mode:overlay;background-color:#d8d8d8;background-position:50%;background-position-y:83%;background-repeat:no-repeat;background-size:cover;height:211px;padding:40px 0 0 63px}h1{font-size:36px;margin-block-end:0;margin-block-start:0}.heroHint,.longHeroHint{font-size:18px;margin-top:10px}.longHeroHint{margin-right:15px}@media screen and (max-width:800px){.longHeader{font-size:22px}.longHeroHint{font-size:14px;margin-right:5px}}@media screen and (max-width:700px){.heroBanner{align-items:center;display:flex;flex-direction:column;justify-content:center;padding:0 20px}h1{font-size:32px}}@media screen and (max-width:400px){h1{font-size:22px}.heroHint,.longHeader{font-size:14px}.longHeroHint{font-size:12px}}.reviewWrapper{align-items:flex-start;border-bottom:2px solid #ccc;display:flex;flex-direction:column;font-variant-numeric:lining-nums proportional-nums;gap:2px;margin-bottom:30px;padding-bottom:30px}.userFirstName{font-weight:700}.venueLocation,.venueName{color:#000;display:block;font-weight:700;text-decoration:none;width:-moz-fit-content;width:fit-content}.venueLocation{font-weight:400}.reviewDate{color:#666}.show{display:block}.hide{display:none}.concertRow{background-color:#e7e7e7;color:#000;cursor:pointer;display:flex;flex-wrap:wrap;gap:20px;margin-bottom:7px;padding:16px;text-decoration:none}.concertRow:hover{background-color:#fff}.date{display:table-cell;font-weight:400;text-align:center;vertical-align:middle}.month{font-size:11px;text-transform:uppercase}.day{font-size:25px}.location,.title{font-size:18px;font-style:normal;font-weight:700;line-height:normal}.location{font-weight:400}.titleLocation{flex:1;min-width:200px}.ticketButton{align-items:center;background:#776db1;border-radius:100px;color:#fff;cursor:pointer;display:flex;font-size:16px;font-style:normal;font-weight:700;justify-content:center;line-height:19px;text-align:center;text-decoration:none;text-transform:capitalize;transition:background-color .3s,color .3s;width:-moz-fit-content;width:fit-content}.ticketButton:hover{opacity:.8}.ticketButton span{font-weight:400;padding:10px 36px}.textSection{font-size:18px;font-weight:700;margin-top:30px;text-decoration:underline}.venueRow{line-height:2rem}.similarArtistWrapper{@media screen and (max-width:700px){flex-direction:row;gap:30px}}.similarArtistImage{border-radius:100px;height:150px;width:150px;@media screen and (max-width:700px){height:50px;width:50px}}.similarArtistName{@media screen and (max-width:700px){font-size:20px;font-weight:400;margin-top:0}}.artistImage img{border-radius:100px;height:200px;width:200px}.artistDesc{font-size:18px;font-style:normal;font-weight:400;line-height:normal}.artistInfo{display:flex;flex-direction:row;font-weight:700;gap:20px;margin:20px 0}.type{line-height:1.3}.category,.follower,.onTour{color:#776db1;display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.3;max-width:610px}.similarArtistsWrapper{@media screen and (max-width:700px){flex-direction:column}}.artistBio{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.56}#showMore,.followArtist{align-items:center;color:#776db1;cursor:pointer;display:flex;margin-top:10px;text-decoration:none}#showMore{background:none;border:none;font:inherit;outline:inherit;padding:0}@media screen and (max-width:700px){.topSection{flex-wrap:wrap}.artistInfo{flex-direction:column}}.topSection{display:flex;gap:20px;margin-top:50px}.topSection h1{font-size:24px;font-style:normal;font-weight:700;line-height:normal}.venueImage img{height:200px;width:200px}.rightColumn{display:flex;flex-direction:column;justify-content:center}.venueDesc{font-size:18px;font-style:normal;font-weight:400;line-height:normal}.venueInfo{display:flex;flex-direction:row;gap:20px;margin:20px 0}.infoSpan{display:flex;flex-direction:column;flex-wrap:wrap;font-weight:700;gap:5px}.infoSpan a{color:#776db1;text-decoration:none}.sectionHeader{font-size:22px;font-style:italic;font-weight:400;margin:30px 0}.livePhotosWrapper{display:flex;overflow-x:scroll}.livePhoto{height:300px;margin-right:10px;width:300px}.similarArtistsWrapper{display:flex;flex-wrap:wrap;@media screen and (max-width:700px){flex-direction:column}}.tourCitiesWrapper{display:flex;flex-wrap:wrap}.tourCity{border:1px solid #776db1;border-radius:50px;color:#776db1;cursor:pointer;margin:0 10px 15px 0;padding:10px 20px;text-decoration:none;text-transform:capitalize}.tourCity:hover{background-color:#776db1;color:#fff;cursor:pointer}.venueBio{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.56}#showMore,.followVenue{align-items:center;color:#776db1;cursor:pointer;display:flex;margin-top:10px;text-decoration:none}@media screen and (max-width:700px){.topSection{flex-wrap:wrap}.venueInfo{flex-direction:column}}.similarArtistWrapper{align-items:center;color:#000;display:flex;flex-direction:column;margin:0 20px 20px 0;text-decoration:none;@media screen and (max-width:700px){flex-direction:row;gap:30px}}.similarArtistWrapper:hover{opacity:.8}.nearByVenueImage{height:150px;width:150px;@media screen and (max-width:700px){height:50px;width:50px}}.similarArtistName{font-weight:700;margin-top:10px;max-width:150px;@media screen and (max-width:700px){font-size:20px;font-weight:400;margin-top:0}}
"""


VENUE_VENUE_PAGE_NJK = """
{% extends "application/base.html" %}
{% import "shared/media/image.html" as mediaMacro %}

{% block canonical_link %}
  <link rel="canonical" href="{{domain}}venue/{{venue.id}}-{{venue.nameSlug}}">
{% endblock %}

{% block meta_description %}
  <meta
    name="description"
    content="Find tickets for upcoming concerts at {{venue.name}} in {{venue.location}}. Browse venue details, event schedules, fan reviews, photos, and more.">
{% endblock %}

{% block title %}
  {{venue.name}} Concert Tickets & {{currentYear}} Event Schedule - {{venue.location}} | Hypebot
{% endblock %}

{% block styles %}
  <style>
    {% include "venue/styles.css" %}
  </style>
{% endblock %}

{% block scripts %}
  <script type="text/javascript">
    window.addEventListener('DOMContentLoaded', function(){
      if ("{{ reviewsWithComments | length }}" <= 5) {
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
  <a href="/search/venues/{{venue.nameFirstLetter | urlencode}}">
    Venues Starting with {{"#" if venue.nameFirstLetter == "%23" else venue.nameFirstLetter | upper}}
  </a>
  &gt;
  <a href="/venue/{{venue.nameFirstLetter | urlencode}}/{{venue.id}}-{{venue.nameSlug}}">
    {{venue.name}} Upcoming Concerts
  </a>
{% endblock %}

{% block content %}
  <div class="topSection">
    <div class="venueImage">
      {{ mediaMacro.image(venue.mediaId, venue.name) }}
    </div>
    <div class="rightColumn">
      <div>
        <h1>{{venue.name}} Upcoming Concerts & Events</h1>
        <div class="venueDesc">
          Explore all upcoming events happening at {{venue.name}} in {{currentYear}}-{{nextYear}}.
          Explore the venue's concert schedule, view photos, and buy tickets to see your favorite artists live in
          {{venue.location}}.
        </div>
      </div>
      <div class="venueInfo">
        <div class="infoSpan">
          <div>{{venue.streetAddress}}</div>
          <div>{{venue.city}}, {{venue.region}}</div>
          <div>{{venue.country}}</div>
        </div>
        {% if venue.link %}
        <div class="infoSpan">
          <a href={{venue.link}} class="infoSpan">
            {{venue.link}}
          </a>
        </div>
        {% endif %}
        {% if venue.phone %}
          <div class="infoSpan">
            {{venue.phone}}
          </div>
        {% endif %}
      </div>
    </div>
  </div>

  <div class="eventList">
    {% if events %}
      <div>
        <div class="sectionHeader">Concert Schedule & Tickets</div>
        {% for event in events %}
          {% include "artist/components/event/event.njk" %}
        {% endfor %}
      </div>
    {% else %}
      {# NO EVENTS #}
      {% if venueArtists %}
        <div class="sectionHeader">Artists Playing At {{venue.name}}</div>
        <div class="similarArtistsWrapper">
          {% for artist in venueArtists %}
            {% include "artist/components/similarArtists/similarArtists.njk" %}
          {% endfor %}
        </div>
      {% endif %}
    {% endif %}
  </div>

  <div class="sectionHeader">About {{venue.name}}</div>
  <div class="venueBio">{{venue.description}}</div>
  <a class="followVenue" href="https://www.bandsintown.com/v/{{venue.id}}-{{venue.nameSlug}}?came_from=900&utm_medium=web&utm_source=static-site-hypebot&utm_campaign=venue&trigger=follow">
    Follow on Bandsintown
    <img src="/assets/arrowRight.svg">
  </a>

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
        {% if (loop.index > 0 and loop.index < 11)  %}
          {% include "artist/components/artistReview/artistReview.njk" %}
        {% endif %}
      {% endfor %}

      <a id="showMore">Show More Reviews</a>
    </div>
  {% endif %}

  {% if events and venueArtists %}
    <div class="sectionHeader">Artists Playing At {{venue.name}}</div>
    <div class="similarArtistsWrapper">
      {% for artist in venueArtists %}
        {% include "artist/components/similarArtists/similarArtists.njk" %}
      {% endfor %}
    </div>
  {% endif %}

  {% if events and venuesNearby %}
    <div class="sectionHeader">Nearby Venues</div>
    <div class="similarArtistsWrapper">
      {% for venue in venuesNearby %}
        <a class="similarArtistWrapper" href="/venue/{{venue.nameFirstLetter | urlencode}}/{{venue.id}}-{{venue.nameSlug}}">
          {{ mediaMacro.image(venue.mediaId, venue.name, 'nearByVenueImage') }}
          <div class="similarArtistName">{{venue.name}}</div>
        </a>
      {% endfor %}
    </div>
  {% endif %}

  {% if nearbyCities %}
    <div class="sectionHeader">Nearby Cities</div>
    <div class="tourCitiesWrapper">
      {% for city in nearbyCities %}
        <a class="tourCity" href="/cities/popular/{{city.urlSlug}}">
          {{ city.name }}
        </a>
      {% endfor %}
    </div>
  {% endif %}
{% endblock %}

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
    "venue/styles.css": VENUE_STYLES_CSS,
    "venue/venuePage.njk": VENUE_VENUE_PAGE_NJK,
    "application/base.html": APPLICATION_BASE_HTML,
    "application/footer.html": APPLICATION_FOOTER_HTML,
    "application/header.html": APPLICATION_HEADER_HTML,
    "application/styles.css": APPLICATION_STYLES_CSS,
    "shared/styles.css": SHARED_STYLES_CSS,
    "shared/media/image.html": SHARED_MEDIA_IMAGE_HTML
}