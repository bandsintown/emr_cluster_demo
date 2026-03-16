

HOME_ARTIST_NJK = """
<a class="artist" href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">
  <div class="artistImage">
    {{ mediaMacro.image(artist.mediaId, artist.name) }}
  </div>
  <div class="nameInfo">
    <div class="artistName">{{ artist.name }}</div>
  </div>
</a>

"""


HOME_BASE_HTML = """
{% extends "application/base.html" %}
{% import "shared/media/image.html" as mediaMacro %}

{% block canonical_link %}
  <link rel="canonical" href="{{ domain }}">
{% endblock %}

{% block meta_description %}
  <meta name="description" content="Get concert tickets for upcoming concerts near you. Browse live events by artist, venue, city, and more.">
{% endblock %}

{% block title %}
  Concerts Near You: Live Music, Upcoming Shows, &amp; Tickets | Hypebot
{% endblock %}

{% block styles %}
  <style>
    {% include "home/styles.css" %}
  </style>
{% endblock %}

{% block hero %}
  <div class="heroBanner">
    <h1>Find concert tickets for your favorite artists</h1>

    <div class="heroHint">
      Dive into the live music scene. Explore upcoming concerts, shows, and events from the
      artists you love.
    </div>
  </div>
{% endblock %}

{% block content %}
  <div class="sectionContainer">
    <div class="textInfoContainer">
      <h2>Top trending artists</h2>
      <div>Stay ahead of the curve with the most popular artists of the moment.</div>
    </div>
    <div class="artistList">
      {% for artist in trendingArtists %}
        {% include "home/artist.njk" %}
      {% endfor %}
    </div>
  </div>

  <div class="sectionContainer">
    <div class="textInfoContainer">
      <h2>Most popular artists</h2>
      <div>
        Discover our curated list of today’s most popular artists loved by fans worldwide.
      </div>
    </div>
    <div class="artistList">
      {% for artist in mostPopularArtists %}
        {% include "home/artist.njk" %}
      {% endfor %}
    </div>
  </div>

  <div class="sectionContainer">
    <div class="textInfoContainer">
      <h2>Artists on tour</h2>
      <div>
        Find artists currently on tour. Explore upcoming concert dates, reviews, photos, and
        more.
      </div>
    </div>
    <div class="artistList">
      {% for artist in onTourArtists %}
        {% include "home/artist.njk" %}
      {% endfor %}
    </div>
  </div>

  <div class="staticSection">
    <h2 class="title">Discover upcoming concerts near you with Hypebot</h2>
    <p class="text">
      <b>Experience the magic of live music.</b> Browse upcoming concerts near you with venue
      locations ranging from Los Angeles to New York. Whether it's an intimate stage or a massive
      arena tour, Hypebot makes sure you never miss a chance to catch your favorite artists live.
    </p>
    <p class="text">
      <b>Since 2004, Hypebot has been chronicling the music industry's evolution. </b> We’ve
      reported on the latest trends, technologies, and news surrounding how music is discovered,
      consumed, marketed, and monetized. We've earned our reputation as the go-to source for staying
      updated on all things music-related, delivering insights that resonate with industry
      professionals and passionate music fans alike.
    </p>
    <p class="text">
      <b>At Hypebot, we go beyond the headlines. </b> Stay in the loop with the latest upcoming
      events, and browse nearby tour dates, venues, and ticket information. Plus, get access to fan
      reviews, photos from shows, and exclusive content that puts you at the heart of the live music
      scene.
    </p>
  </div>
{% endblock %}

"""


HOME_STYLES_CSS = """
.heroBanner{background:url(/assets/hero.webp);background-blend-mode:overlay;background-color:#d8d8d8;background-position:50%;background-position-y:83%;background-repeat:no-repeat;background-size:cover;height:211px;padding:40px 0 0 63px}h1{font-size:36px;margin-block-end:0;margin-block-start:0}.heroHint,.longHeroHint{font-size:18px;margin-top:10px}.longHeroHint{margin-right:15px}@media screen and (max-width:800px){.longHeader{font-size:22px}.longHeroHint{font-size:14px;margin-right:5px}}@media screen and (max-width:700px){.heroBanner{align-items:center;display:flex;flex-direction:column;justify-content:center;padding:0 20px}h1{font-size:32px}}@media screen and (max-width:400px){h1{font-size:22px}.heroHint,.longHeader{font-size:14px}.longHeroHint{font-size:12px}}.sectionContainer{align-items:center;border-bottom:1px solid #c4c4c4;display:flex}.textInfoContainer{margin-right:20px;max-width:290px}h2{font-size:24px;margin-block-end:0;margin-block-start:0;margin-bottom:5px}.artist{position:relative}.nameInfo{align-items:center;background:linear-gradient(0deg,#000,transparent);border-bottom-left-radius:12px;border-bottom-right-radius:12px;color:#eee;display:flex;height:35px;justify-content:center;position:absolute;top:115px;width:100%}.artistName{display:-webkit-box;overflow:hidden;text-overflow:ellipsis;-webkit-line-clamp:2;-webkit-box-orient:vertical;text-align:center}.artistList{display:flex;gap:18px;margin-bottom:30px;margin-top:30px;overflow-x:auto;width:100%}.artistImage img{border-radius:12px;height:150px;width:150px}.artistList a,.artistList a:visited{color:#000;text-decoration:none}.artistList::-webkit-scrollbar-track{background-color:#f5f5f5;border-radius:6px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3)}.artistList::-webkit-scrollbar-thumb{background-color:#ccc;border-radius:6px;-webkit-box-shadow:inset 0 0 6px rgba(0,0,0,.3)}.staticSection{margin-top:50px}.text{line-height:24px;margin-bottom:26px}@media screen and (max-width:700px){.sectionContainer{align-items:flex-start;flex-direction:column}.textInfoContainer{margin-right:unset;max-width:unset}h2{margin-top:20px}}
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
    "home/artist.njk": HOME_ARTIST_NJK,
    "home/base.html": HOME_BASE_HTML,
    "home/styles.css": HOME_STYLES_CSS,
    "application/base.html": APPLICATION_BASE_HTML,
    "application/footer.html": APPLICATION_FOOTER_HTML,
    "application/header.html": APPLICATION_HEADER_HTML,
    "application/styles.css": APPLICATION_STYLES_CSS,
    "shared/styles.css": SHARED_STYLES_CSS,
    "shared/media/image.html": SHARED_MEDIA_IMAGE_HTML
}