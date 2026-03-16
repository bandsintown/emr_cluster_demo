

SEARCH_ARTISTS_BY_LETTER_NJK = """
{% extends "application/base.html" %}

{% block canonical_link %}
  <link rel="canonical" href="{{ domain }}search/artists/{{letter | urlencode}}">
{% endblock %}

{% block meta_description %}
  <meta name="description" content="Browse the top music artists with names starting with {{letter}}. Find tickets, tour dates, artist information, and more.">
{% endblock %}

{% block title %}
  Artist Names Starting With {{letter}} | Hypebot
{% endblock %}

{% block styles %}
  <style>
    {% include "search/artists/styles.css" %}
  </style>
{% endblock %}

{% block content %}
  <div class="artistList">
    <span class="letter">{{ letter }}</span>
    <div class="artistSections">
      {% for artist in artists %}
        <div>
          <a class="artistLink" href="/artist/{{ artist.nameFirstLetter | urlencode }}/{{ artist.id }}-{{ artist.nameSlug }}">
            {{ artist.name }}
          </a>
        </div>
      {% endfor %}
    </div>
  </div>
{% endblock content %}

"""


SEARCH_ARTISTS_STYLES_CSS = """
.heroBanner{background:url(/assets/hero.webp);background-blend-mode:overlay;background-color:#d8d8d8;background-position:50%;background-position-y:83%;background-repeat:no-repeat;background-size:cover;height:211px;padding:40px 0 0 63px}h1{font-size:36px;margin-block-end:0;margin-block-start:0}.heroHint,.longHeroHint{font-size:18px;margin-top:10px}.longHeroHint{margin-right:15px}@media screen and (max-width:800px){.longHeader{font-size:22px}.longHeroHint{font-size:14px;margin-right:5px}}@media screen and (max-width:700px){.heroBanner{align-items:center;display:flex;flex-direction:column;justify-content:center;padding:0 20px}h1{font-size:32px}}@media screen and (max-width:400px){h1{font-size:22px}.heroHint,.longHeader{font-size:14px}.longHeroHint{font-size:12px}}.sections ul{display:flex;gap:30px;list-style-type:none;padding-inline-start:0}.sections ul li{background-color:#efefef;padding:4px}.sections ul li.current{background-color:#cecece}.sections ul li a,.sections ul li a:visited{color:#000}.letterlist a.current{color:#027148}.letter{color:#999;font-size:28px;font-style:normal;font-weight:700;line-height:normal;text-transform:uppercase}.artistList{border-bottom:2px solid #ccc;margin:30px 0 0;padding-bottom:30px}.artistList a,.artistList a:visited{color:#000}.artistSections{-moz-columns:3;column-count:3;margin-top:5px;@media only screen and (max-width:750px){-moz-columns:2;column-count:auto;column-count:2}}.artistSections div{padding-top:5px}.artistLink{text-decoration:none}@media screen and (max-width:700px){.main{padding:15px}}
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
    "search/artists/byLetter.njk": SEARCH_ARTISTS_BY_LETTER_NJK,
    "search/artists/styles.css": SEARCH_ARTISTS_STYLES_CSS,
    "application/base.html": APPLICATION_BASE_HTML,
    "application/footer.html": APPLICATION_FOOTER_HTML,
    "application/header.html": APPLICATION_HEADER_HTML,
    "application/styles.css": APPLICATION_STYLES_CSS,
    "shared/styles.css": SHARED_STYLES_CSS,
    "shared/media/image.html": SHARED_MEDIA_IMAGE_HTML
}