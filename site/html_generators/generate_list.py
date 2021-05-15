import re
import json
import operator
import datetime
import argparse
from itertools import chain
from hashlib import sha256
from os import path
from urllib.parse import urljoin

import yaml
from yattag import Doc, indent
from requests import Request

import constants
import generate_navbar
from manual_crawler import crawl


class cache:
    """class to manage caching API requests for MAL names"""
    def __init__(self, crawler):
        self.jsonpath = "../mal_name_cache.json"
        self.write_to_cache_const = 5
        self.write_to_cache_periodically = self.write_to_cache_const
        self.crawler = crawler
        if not path.exists(self.jsonpath):
            open(self.jsonpath, "a").close()
        with open(self.jsonpath, "r") as js_f:
            try:
                self.items = json.load(js_f)
            except json.JSONDecodeError:  # file is empty or broken
                self.items = {}

    def update_json_file(self):
        with open(self.jsonpath, "w") as f:
            json.dump(self.items, f)

    def _mal_crawl_name(self, mal_id):
        """Downloads the name of the MAL id"""
        print("[Cache][Crawler] Downloading name for MAL ID {}".format(mal_id))
        return self.crawler.get_anime(mal_id)["title"]

    def download_name(self, id):
        self.write_to_cache_periodically -= 1
        if self.write_to_cache_periodically < 0:
            self.write_to_cache_periodically = self.write_to_cache_const
            self.update_json_file()
        return self._mal_crawl_name(id)

    def __contains__(self, id):
        """defines the 'in' keyword on cache."""
        return str(id) in self.items

    def get(self, id):
        if self.__contains__(id):
            # print("[Cache] Found name for id {} in cache".format(id))
            return self.items[str(id)]
        else:
            self.items[str(id)] = self.download_name(id)
            return self.items[str(id)]

    def __iter__(self):
        return self.items.__iter__()


crawler = crawl(wait=5, retry_max=3)
download_names = False
mal_cache = cache(crawler)


def format_duration(dur):
    """Formats duration (from minutes) into a readable format"""
    if float(dur) >= 1.0:
        return "{} min".format(int(dur))
    else:
        return "{} sec".format(round(dur * 60))


def join_urls(*parts_url):
    """joins a variable argument urlpath to a url"""
    parts_url = list(map(str, parts_url))  # convert to strings
    while len(parts_url) > 2:
        parts_url = list(
            chain([urljoin(parts_url[0], parts_url[1]) + "/"], parts_url[2:]))
    if len(parts_url) == 2:
        url = urljoin(parts_url[0], parts_url[1])
    else:
        if isinstance(parts_url, tuple) or isinstance(parts_url, list):
            return parts_url[0]
        else:
            url = parts_url
    return url


# not needed, youtu.be/<video_id> forwards to correct video.
def create_youtube(id):
    """Turns a youtube video id to a link."""
    base_url = join_urls("https://youtu.be", "watch")
    return str(Request("GET", base_url, params={"v": str(id)}).prepare().url)


def create_id(name, octothorpe):
    name = re.sub(r"[^\w]", "", name)  # remove problematic characters
    return "{}{}{}".format("#" if octothorpe else "", str(name),
                           sha256(name.encode()).hexdigest()[:10])


def sort_list(sources, list_order):
    if list_order == constants.order.REC:
        return sources
    else:
        for c in sources:
            if isinstance(c["date"], str):
                c["date"] = datetime.datetime.strptime(c["date"],
                                                       "%Y-%m-%d").date()
        return sorted(sources, key=operator.itemgetter("date"), reverse=True)


def create_page(sources, list_order):
    """Creates the table from YAML"""
    global download_names
    doc, tag, text = Doc().tagtext()
    doc.asis("<!DOCTYPE html>")
    with tag("html", ("lang", "en")):
        with tag("head"):
            with tag("title"):
                text(constants.SHORT_NAME)
            doc.asis("<!-- Required meta tags -->")
            doc.asis('<meta charset="utf-8">')
            doc.asis(
                '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">'
            )
            doc.asis("<!-- bootstrap CSS -->")
            doc.asis(
                """<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">"""
            )
            doc.asis("""<link rel="stylesheet" href="./css/list.css">""")
            doc.asis("<!-- Fonts -->")
            doc.asis(
                '<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">'
            )
        with tag("body"):
            doc.asis("<!-- navbar -->")
            doc.asis(
                generate_navbar.navbar(active=constants.LIST_TAB,
                                       sorttab=list_order))
            doc.asis("<!-- note -->")
            with tag("div", ("class", "container py-3 mb-0"), ("id", "note")):
                with tag("p", ("class", "text-center mb-0")):
                    text(
                        "This is not an exhaustive list, just my recommendations."
                    )
            doc.asis("<!-- list -->")
            with tag("main", klass="container", id="main-container"):
                sources = sort_list(sources, list_order)
                for s in sources:
                    with tag("div", ("class", "anime-row-container")):
                        with tag(
                                "div",
                                klass="row anime-row align-items-center border"
                        ):  # row for each anime
                            # name/tags/info button
                            with tag("div", klass="col-sm"):
                                # name
                                with tag("h6"):
                                    text(str(s["name"]))
                                    # tags
                                    for t in sorted(s["tags"]):
                                        if t.lower() in [
                                                "anthology",
                                                "arthouse",
                                                "commercial",
                                                "film",
                                                "music video",
                                                "series",
                                        ]:
                                            tag_slug = t.lower().strip().replace(" ", "-")
                                            with tag(
                                                    "span",
                                                    klass="badge tag {}".
                                                    format(tag_slug),
                                            ):
                                                with tag(
                                                    "a",
                                                    ("href", "javascript:void(0)"),
                                                    ("class", "badge-link"),
                                                    ("data-toggle", "tooltip"),
                                                    ("data-original-title", "filter page to shorts tagged '{}'".format(t.strip().lower())),
                                                    ("onclick", "filterBadge('{}', this)".format(tag_slug))):
                                                        text(t.capitalize())
                                        else:
                                            print("Warning, Unknown tag:", t)
                                    if list_order == constants.order.DATE:
                                        with tag("span",
                                                 klass="badge badge-info"):
                                            text(str(s["date"]))
                                    # if this has extra info
                                    if s["extra_info"] is not None:
                                        with tag(
                                                "a",
                                            ("role", "button"),
                                            ("class", "more-info-expand ml-2"),
                                            (
                                                "href",
                                                create_id(
                                                    name="{}-extra-info".
                                                    format(s["name"]),
                                                    octothorpe=True,
                                                ),
                                            ),
                                            ("aria-expanded", "false"),
                                            ("data-toggle", "collapse"),
                                        ):
                                            text("ⓘ")

                            # time (durations/episodes)
                            if s["duration"] is not None and s[
                                    "episodes"] is not None:
                                dur, eps = s["duration"], s["episodes"]
                                with tag("div", ("class", "time col-md-1")):
                                    if eps == 1:
                                        with tag("span", klass="badge"):
                                            text("{}".format(
                                                format_duration(dur)))
                                    elif eps == 0:  # unknown ep count
                                        with tag("span", klass="badge"):
                                            text("{} x ? eps".format(
                                                format_duration(dur)))
                                    else:
                                        with tag("span", klass="badge"):
                                            text("{} x {} eps".format(
                                                format_duration(dur), eps
                                            ))  # display as multiple episodes
                            else:
                                print("Undefined duration/episodes:", s)

                            # buttons
                            with tag(
                                    "div",
                                    klass=
                                    "circular-buttons-container col-md-4 col-lg-3 col-xl-3",
                            ):
                                # databases
                                if s["database"] is not None:
                                    for db in s["database"]:
                                        # MAL
                                        if "mal" in db:
                                            # if multiple entries
                                            if isinstance(db["mal"], list):
                                                # place button
                                                list_hash_id = create_id(
                                                    name="{}{}".format(
                                                        str(s["name"]),
                                                        "".join(
                                                            list(
                                                                map(
                                                                    str,
                                                                    db["mal"]))
                                                        ),
                                                    ),
                                                    octothorpe=True,
                                                )
                                                with tag(
                                                        "a",
                                                    ("role", "button"),
                                                    ("href", list_hash_id),
                                                    ("aria-expanded", "false"),
                                                    ("data-toggle",
                                                     "collapse"),
                                                ):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            "./images/mal_icon.png",
                                                        ),
                                                        (
                                                            "alt",
                                                            "{} (MyAnimeList)".
                                                            format(s["name"]),
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )

                                            else:
                                                # if single entry
                                                mal_url = join_urls(
                                                    "https://myanimelist.net",
                                                    "anime",
                                                    db["mal"],
                                                )
                                                with tag("a", href=mal_url):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            """./images/mal_icon.png""",
                                                        ),
                                                        (
                                                            "alt",
                                                            "{} (MyAnimeList)".
                                                            format(s["name"]),
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )
                                        # add elifs for other databases here
                                        # (if expading later)
                                        else:
                                            print(
                                                "Warning, found unknown database:",
                                                db)

                                # streaming
                                if s["streaming"] is not None:
                                    for vid in s["streaming"]:
                                        if "youtube" in vid:
                                            # if list of videos
                                            if isinstance(
                                                    vid["youtube"], list):
                                                # print("Creating list for", s['name'])
                                                list_hash_id = create_id(
                                                    name="{}{}".format(
                                                        str(s["name"]),
                                                        "".join(
                                                            list(
                                                                map(
                                                                    str,
                                                                    vid["youtube"]
                                                                ))),
                                                    ),
                                                    octothorpe=True,
                                                )
                                                with tag(
                                                        "a",
                                                    ("role", "button"),
                                                    ("href", list_hash_id),
                                                    ("aria-expanded", "false"),
                                                    ("data-toggle",
                                                     "collapse"),
                                                ):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            "./images/yt_icon.png",
                                                        ),
                                                        (
                                                            "alt",
                                                            "{} (Youtube)".
                                                            format(s["name"]),
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )
                                                    if s["cc"]:
                                                        with tag(
                                                                "span",
                                                            ("class",
                                                             "badge cc"),
                                                            ("data-toggle",
                                                             "tooltip"),
                                                            (
                                                                "data-original-title",
                                                                "Videos have Subtitles",
                                                            ),
                                                        ):
                                                            text("CC")
                                            else:
                                                # single video
                                                with tag(
                                                        "a",
                                                        href=join_urls(
                                                            "https://youtu.be"
                                                            if "playlist"
                                                            not in
                                                            vid["youtube"] else
                                                            "https://youtube.com",
                                                            vid["youtube"],
                                                        ),
                                                ):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            "./images/yt_icon.png",
                                                        ),
                                                        (
                                                            "alt",
                                                            "{} (Youtube)".
                                                            format(s["name"]),
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )
                                                    if s["cc"]:
                                                        with tag(
                                                                "span",
                                                            ("class",
                                                             "badge cc"),
                                                            ("data-toggle",
                                                             "tooltip"),
                                                            (
                                                                "data-original-title",
                                                                "Video has Subtitles",
                                                            ),
                                                        ):
                                                            text("CC")

                                        elif "vimeo" in vid:
                                            # if list of videos
                                            if isinstance(vid["vimeo"], list):
                                                list_hash_id = create_id(
                                                    name="{}{}".format(
                                                        str(s["name"]),
                                                        "".join(
                                                            list(
                                                                map(
                                                                    str,
                                                                    vid["vimeo"]
                                                                ))),
                                                    ),
                                                    octothorpe=True,
                                                )
                                                with tag(
                                                        "a",
                                                    ("role", "button"),
                                                    ("href", list_hash_id),
                                                    ("aria-expanded", "false"),
                                                    ("data-toggle",
                                                     "collapse"),
                                                ):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            "./images/vimeo_icon.png",
                                                        ),
                                                        (
                                                            "alt",
                                                            "{} (Vimeo)".
                                                            format(s["name"]),
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )
                                            else:
                                                # single video
                                                with tag(
                                                        "a",
                                                        href=join_urls(
                                                            "https://vimeo.com",
                                                            vid["vimeo"],
                                                        ),
                                                ):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            "./images/vimeo_icon.png",
                                                        ),
                                                        (
                                                            "alt",
                                                            "{} (Vimeo)".
                                                            format(s["name"]),
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )
                                        elif "crunchyroll" in vid:
                                            with tag(
                                                    "a",
                                                    href=join_urls(
                                                        "http://www.crunchyroll.com",
                                                        vid["crunchyroll"],
                                                    ),
                                            ):
                                                doc.stag(
                                                    "img",
                                                    (
                                                        "src",
                                                        "./images/cr_icon.png",
                                                    ),
                                                    (
                                                        "alt",
                                                        "{} (Crunchyroll)".
                                                        format(s["name"]),
                                                    ),
                                                    ("class",
                                                     "rounded-circle"),
                                                )
                                        elif "netflix" in vid:
                                            with tag(
                                                    "a",
                                                    href=join_urls(
                                                        "https://www.netflix.com",
                                                        "title",
                                                        vid["netflix"],
                                                    ),
                                            ):
                                                doc.stag(
                                                    "img",
                                                    (
                                                        "src",
                                                        "./images/netflix_icon.png",
                                                    ),
                                                    (
                                                        "alt",
                                                        "{} (Netflix)".format(
                                                            s["name"]),
                                                    ),
                                                    ("class",
                                                     "rounded-circle"),
                                                )
                                        elif "funimation" in vid:
                                            with tag(
                                                    "a",
                                                    href=join_urls(
                                                        "https://www.funimation.com",
                                                        "shows",
                                                        vid["funimation"],
                                                    ),
                                            ):
                                                doc.stag(
                                                    "img",
                                                    (
                                                        "src",
                                                        "./images/fn_icon.png",
                                                    ),
                                                    (
                                                        "alt",
                                                        "{} (Funimation)".
                                                        format(s["name"]),
                                                    ),
                                                    ("class",
                                                     "rounded-circle"),
                                                )
                                        elif "hidive" in vid:
                                            with tag(
                                                    "a",
                                                    href=join_urls(
                                                        "https://www.hidive.com",
                                                        "tv",
                                                        str(vid["hidive"]),
                                                    ),
                                            ):
                                                doc.stag(
                                                    "img",
                                                    (
                                                        "src",
                                                        "./images/hidive_icon.png",
                                                    ),
                                                    (
                                                        "alt",
                                                        "{} (Hidive)".format(
                                                            s["name"]),
                                                    ),
                                                    ("class",
                                                     "rounded-circle"),
                                                )

                                        elif "twitter" in vid:
                                            with tag(
                                                    "a",
                                                    href=join_urls(
                                                        vid["twitter"]),
                                            ):
                                                doc.stag(
                                                    "img",
                                                    (
                                                        "src",
                                                        "./images/twitter.svg",
                                                    ),
                                                    (
                                                        "alt",
                                                        "{} (Twitter)".format(
                                                            s["name"]),
                                                    ),
                                                    ("class",
                                                     "rounded-circle"),
                                                )
                                        elif "website" in vid:
                                            if "attraction-lemanga" in vid[
                                                    "website"]:
                                                with tag("a",
                                                         href=vid["website"]):
                                                    doc.stag(
                                                        "img",
                                                        (
                                                            "src",
                                                            "./images/attraction_icon.png",
                                                        ),
                                                        (
                                                            "alt",
                                                            "attraction-lemanga website",
                                                        ),
                                                        ("class",
                                                         "rounded-circle"),
                                                    )
                                            else:
                                                print(
                                                    "Warning, unfound 'source' in streaming:",
                                                    vid,
                                                )
                                        else:
                                            print(
                                                "Warning, unfound 'source' in streaming:",
                                                vid,
                                            )

                        # HIDDEN ROWS
                        # insert hidden row for extra info if ⓘ exists
                        if s["extra_info"] is not None:
                            with tag(
                                    "div",
                                    klass=
                                    "collapse border rounded-bottom border-top-0 mb-1",
                                    id=create_id(
                                        name="{}-extra-info".format(s["name"]),
                                        octothorpe=False,
                                    ),
                            ):
                                with tag("p", klass="pl-2 mb-0"):
                                    text(str(s["extra_info"]))

                        # insert hidden row for databases
                        if s["database"] is not None:
                            for db in s["database"]:
                                if "mal" in db and isinstance(db["mal"], list):
                                    list_hash_id = create_id(
                                        name="{}{}".format(
                                            str(s["name"]),
                                            "".join(list(map(str, db["mal"]))),
                                        ),
                                        octothorpe=False,
                                    )
                                    with tag(
                                            "div",
                                            klass="collapse rounded mb-2",
                                            id=list_hash_id,
                                    ):
                                        with tag("div", klass="list-group"):
                                            for entry in db["mal"]:
                                                with tag(
                                                        "a",
                                                        klass=
                                                        "list-group-item list-group-item-action",
                                                        href=join_urls(
                                                            "https://myanimelist.net",
                                                            "anime",
                                                            entry,
                                                        ),
                                                ):
                                                    if download_names:
                                                        text(
                                                            mal_cache.get(
                                                                entry))
                                                    else:
                                                        text(entry)
                            # insert hidden rows for youtube/vimeo
                        if s["streaming"] is not None:
                            for vid in s["streaming"]:
                                # multiple youtube videos
                                if "youtube" in vid and isinstance(
                                        vid["youtube"], list):
                                    list_hash_id = create_id(
                                        name="{}{}".format(
                                            str(s["name"]),
                                            "".join(
                                                list(map(str,
                                                         vid["youtube"]))),
                                        ),
                                        octothorpe=False,
                                    )
                                    with tag(
                                            "div",
                                            klass="collapse rounded mb-2",
                                            id=list_hash_id,
                                    ):
                                        with tag("div", klass="list-group"):
                                            # check if episodes have names [
                                            # correlates to MAL entries 1-1 ]
                                            for db in s["database"]:
                                                if "mal" in db and isinstance(
                                                        db["mal"], list):
                                                    for mal_id, v in zip(
                                                            db["mal"],
                                                            vid["youtube"]):
                                                        with tag(
                                                                "a",
                                                                klass=
                                                                "list-group-item list-group-item-action",
                                                                href=join_urls(
                                                                    "https://youtu.be",
                                                                    v),
                                                        ):
                                                            text(
                                                                mal_cache.get(
                                                                    mal_id))
                                                else:  # else use 'episode 1,2,3' as link text
                                                    for i, v in enumerate(
                                                            vid["youtube"], 1):
                                                        with tag(
                                                                "a",
                                                                klass=
                                                                "list-group-item list-group-item-action",
                                                                href=join_urls(
                                                                    "https://youtu.be",
                                                                    v),
                                                        ):
                                                            text("Episode {}".
                                                                 format(i))
                                # multiple vimeo videos
                                elif "vimeo" in vid and isinstance(
                                        vid["vimeo"], list):
                                    list_hash_id = create_id(
                                        name="{}{}".format(
                                            str(s["name"]),
                                            "".join(
                                                list(map(str, vid["vimeo"]))),
                                        ),
                                        octothorpe=False,
                                    )
                                    with tag(
                                            "div",
                                            klass="collapse rounded mb-2",
                                            id=list_hash_id,
                                    ):
                                        with tag("div", klass="list-group"):
                                            for i, v in enumerate(
                                                    vid["vimeo"], 1):
                                                with tag(
                                                        "a",
                                                        klass=
                                                        "list-group-item list-group-item-action",
                                                        href=join_urls(
                                                            "https://vimeo.com",
                                                            v),
                                                ):
                                                    text(
                                                        "Episode {}".format(i))
            # footer
            doc.asis("<!-- footer -->")
            with tag("footer", ("class", "bg-dark footer")):
                with tag("div", klass="container center"):
                    with tag("div", klass="row justify-content-center py-2"):
                        with tag("p", klass="mb-0"):
                            text("© PurplePinapples")
                with tag("a", klass="d-none", href=constants.user_link):
                    pass
            doc.asis("<!-- javascript/popper.js -->")
            doc.asis(
                """<script src="https://code.jquery.com/jquery-3.4.1.slim.min.js" integrity="sha384-J6qa4849blE2+poT4WnyKhv5vZF5SrPo0iEjwBvKU7imGFAV0wwj1yYfoRSJoZ+n" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js" integrity="sha384-Q6E9RHvbIyZFJoft+2mJbHaEWldlvI9IOYy5n3zV9zzTtmI3UksdQRVvoxMfooAo" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js" integrity="sha384-wfSDF2E50Y2D1uUdj0O3uMBJnjuUD4Ih7YwaYd1iqfktj0Uod8GCExl3Og8ifwB6" crossorigin="anonymous"></script>"""
            )
            with tag("script"):
                doc.asis("""
// function to filter the list page to include only particular badges
function filterBadge(badgeSlug, clickedTooltip) {
    document.querySelectorAll(".anime-row-container").forEach((anime) => {
        // set display property accordingly if the tag the user clicked on is included in this entry
        anime.style.display = (anime.querySelector(`span.badge.${badgeSlug}`) === null) ? 'none': '';
    });
    // disable/re-enable tooltip to fix visual display bug
    if (typeof clickedTooltip !== null) {
        $(clickedTooltip).tooltip("dispose")
        $(clickedTooltip).tooltip({
            placement: "top"
        });
    }
    window.location.hash = badgeSlug
}

// runs when document is loaded:
document.addEventListener('DOMContentLoaded', function() {
  // activate CC tooltips
  $('span.cc').tooltip({
    placement: "top"
  });

  //activate ? tooltip
  $('span.ordernote').tooltip({
    placement: "bottom"
  });

  // activate tooltip for badge link filters
  $('.badge-link').tooltip({
    placement: "top"
  })

  // sort by rec order/date added
  $('#orderchoice button').click(function() {
    $('#sort').val($(this).text().trim());
    $('#choiceform').submit();
  });

  // footer onclick
  let footer = document.querySelector("footer.footer");
  footer.onmouseup = function(a) { // when mouse is released
    if (a.ctrlKey || a.metaKey || a.which == 2) {
      a.preventDefault(); // prevent middle click from opening tab, so it doesnt open twice.
      window.open($(footer).find('a').attr("href"));
    } else {
      window.location = $(footer).find('a').attr("href");
    }
  }

  // check url to filter by tag onload
  if (window.location.hash.slice(1)) {
    filterBadge(window.location.hash.slice(1))
  }
}, false);

""")
    return indent(doc.getvalue(), indent_text=True)


def main(opt):
    global download_names
    download_names = opt
    # Read in YAML Sources
    with open(constants.LIST_SOURCES) as yaml_src:
        sources = yaml.load(yaml_src, Loader=yaml.FullLoader)
    # write out html file - ordered by reccomendation
    with open(f"{constants.OUTPUT_DIR}/index.html", "w") as write_html_file:
        print("Generated index.html")
        write_html_file.write(create_page(sources, constants.order.REC))
    # write out html file - ordered by date
    with open(f"{constants.OUTPUT_DIR}/newest.html", "w") as write_newest_html:
        print("Generated newest.html")
        write_newest_html.write(create_page(sources, constants.order.DATE))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d",
                        "--download-names",
                        action="store_true",
                        default=False)
    args = parser.parse_args()
    main(args.download_names)
    mal_cache.update_json_file()
