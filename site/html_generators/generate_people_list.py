import sys
from os import path
from pathlib import Path
from typing import TypeVar, List, Iterator, Optional


import yaml
from pydantic import BaseModel
from yattag import Doc, indent  # type: ignore[import]
from PIL import Image  # type: ignore[import]

from . import constants
from . import generate_navbar
from .generate_list import join_urls


class Person(BaseModel):
    name: str
    image: str
    mal: Optional[int]
    website: Optional[str]
    youtube: Optional[str]


def image_path(filename: str) -> str:
    return path.join("./images/people", filename)


def get_ratio_image_from_relative_path(filename: str) -> str:
    """from the html_generators directory, gets the ratio of height/width for an image in the people directory"""
    p = Path(__file__).parent.parent / "static/images/people" / filename
    assert p.exists(), str(p)
    with Image.open(p) as img:
        width, height = img.size
        return "{}%".format(height / width * 100)


T = TypeVar("T")


def chunk_list(lst: List[T], chunk_size: int) -> Iterator[List[T]]:
    """Return chunk_size'd lists from the large list."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i : i + chunk_size]


def create_people_page(sources: List[Person]) -> str:
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
            doc.asis("""<link rel="stylesheet" href="./css/people.css">""")
            doc.asis("<!-- Fonts -->")
            doc.asis(
                '<link href="https://fonts.googleapis.com/css?family=Lato" rel="stylesheet">'
            )
        with tag("body"):
            doc.asis("<!-- navbar -->")
            doc.asis(generate_navbar.navbar(active=constants.PEOPLE_TAB))
            doc.asis("<!-- note -->")
            with tag(
                "div", ("class", "container rounded-bottom py-3 mb-2"), ("id", "note")
            ):
                with tag("p", ("class", "text-center mb-0")):
                    text(
                        "People I feel are worth checking out. For more, check out the "
                    )
                    with tag("a", href="https://myanimelist.net/clubs.php?cid=76651"):
                        text("Short Directors Project")
                    text(" on MAL")
            doc.asis("<!-- list -->")
            with tag("main", klass="container"):
                with tag("div", klass="card-columns"):
                    for c in sources:
                        with tag("div", klass="card"):
                            with tag(
                                "div",
                                ("class", "image-container"),
                                (
                                    "style",
                                    (
                                        f"padding-bottom:{get_ratio_image_from_relative_path(c.image)};"
                                    ),
                                ),
                            ):
                                doc.stag(
                                    "img",
                                    ("class", "card-img-top img-fluid"),
                                    ("src", image_path(c.image)),
                                    alt=c.name,
                                )
                            with tag("div", klass="card-block"):
                                with tag("h4", klass="card-title"):
                                    text(c.name)
                                with tag("div", klass="card-text"):
                                    for other_link in sorted(
                                        list(
                                            {
                                                k: getattr(c, k)
                                                for k, v in c.dict().items()
                                                if k not in ["name", "image"]
                                                and v is not None
                                            }
                                        )
                                    ):
                                        o_link = getattr(c, other_link)
                                        assert o_link is not None, (
                                            str(c) + f"using {other_link}"
                                        )
                                        if other_link == "mal":
                                            with tag(
                                                "a",
                                                ("target", "_blank"),
                                                ("rel", "norefferer"),
                                                klass="badge badge-pill person-link badge-secondary",
                                                href=join_urls(
                                                    "https://myanimelist.net",
                                                    "people",
                                                    o_link,
                                                ),
                                            ):
                                                with tag("span", klass="moveup"):
                                                    text("mal")
                                        elif other_link == "website":
                                            with tag(
                                                "a",
                                                ("target", "_blank"),
                                                ("rel", "norefferer"),
                                                klass="badge badge-pill person-link badge-secondary movetext",
                                                href=o_link,
                                            ):
                                                with tag("span", klass="moveup"):
                                                    text("website")
                                        elif other_link == "vimeo":
                                            with tag(
                                                "a",
                                                ("target", "_blank"),
                                                ("rel", "norefferer"),
                                                klass="badge badge-pill person-link badge-secondary movetext",
                                                href=join_urls(
                                                    "https://vimeo.com",
                                                    o_link,
                                                ),
                                            ):
                                                with tag("span", klass="moveup"):
                                                    text("vimeo")
                                        elif other_link == "youtube":
                                            with tag(
                                                "a",
                                                ("target", "_blank"),
                                                ("rel", "norefferer"),
                                                klass="badge badge-pill person-link badge-secondary movetext",
                                                href=join_urls(
                                                    "https://www.youtube.com",
                                                    "user",
                                                    o_link,
                                                ),
                                            ):
                                                with tag("span", klass="moveup"):
                                                    text("youtube")
                                        else:
                                            print(
                                                f"Unknown tag: {other_link}",
                                                file=sys.stderr,
                                            )
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
                doc.asis(
                    """
// runs when document is loaded:
document.addEventListener('DOMContentLoaded', function() {

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

  }, false);
"""
                )
    return str(indent(doc.getvalue(), indent_text=True))


def main() -> None:
    # Read in YAML Sources
    with open(constants.PEOPLE_SOURCES) as yaml_src:
        raw_sources = yaml.load(yaml_src, Loader=yaml.FullLoader)
    sources = [Person.parse_obj(p) for p in raw_sources]
    # write out html file
    with open(f"{constants.OUTPUT_DIR}/people.html", "w") as write_html_file:
        print("Generated people.html")
        write_html_file.write(str(create_people_page(sources)))


if __name__ == "__main__":
    main()
