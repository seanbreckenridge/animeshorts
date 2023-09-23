from typing import Any

from yattag import Doc, indent  # type: ignore[import]
from . import constants

# generates the navbar, and forms for the top of the page.


def navbar(active: str, **kwargs: Any) -> str:
    """'active' determines which tab is highlighted"""
    if not kwargs:
        sorttab = None
    else:
        sorttab = kwargs["sorttab"]
    doc, tag, text = Doc().tagtext()
    with tag(
        "nav",
        klass="navbar navbar-expand-lg navbar-dark bg-dark navbar-static-top container",
    ):
        # hamburger menu
        with tag(
            "button",
            ("class", "navbar-toggler"),
            ("data-toggle", "collapse"),
            ("data-target", "#collapse_navbar_target"),
        ):
            with tag("span", klass="navbar-toggler-icon"):
                text()
        # navbar title
        with tag("a", klass="navbar-brand text-nowrap mr-3 my-2", href="./"):
            text(constants.FULL_NAME)
        # collapsible page links
        with tag("div", klass="collapse navbar-collapse", id="collapse_navbar_target"):
            with tag("ul", klass="navbar-nav nav-pills dark-blue"):
                with tag(
                    "li",
                    klass="nav-item{}".format(
                        " active" if active == constants.LIST_TAB else ""
                    ),
                ):
                    with tag(
                        "a",
                        ("class", "nav-link px-2"),
                        (
                            "style",
                            "{}".format(
                                "background-color: #385289;"
                                if active == constants.LIST_TAB
                                else ""
                            ),
                        ),
                        ("href", "./"),
                    ):
                        text(constants.LIST_TAB)
                with tag(
                    "li",
                    klass="nav-item{}".format(
                        " active" if active == constants.PEOPLE_TAB else ""
                    ),
                ):
                    with tag(
                        "a",
                        ("class", "nav-link px-2"),
                        (
                            "style",
                            "{}".format(
                                "background-color: #385289;"
                                if active == constants.PEOPLE_TAB
                                else ""
                            ),
                        ),
                        ("href", "./people"),
                    ):
                        text(constants.PEOPLE_TAB)
            if active == constants.LIST_TAB:
                with tag("ul", klass="navbar-nav pr-2"):
                    with tag("li", klass="nav-item"):
                        with tag(
                            "a",
                            klass="mx-2",
                            style="color: white; position: relative; top: 0.1rem;",
                        ):
                            text("Order By:")
                        with tag(
                            "div",
                            ("class", "btn-group ml-1"),
                            ("role", "group"),
                        ):
                            with tag("form", ("action", "./"), ("class", "btn-group")):
                                with tag(
                                    "button",
                                    (
                                        "class",
                                        "btn btn-secondary{}".format(
                                            " active"
                                            if sorttab == constants.Order.REC
                                            else ""
                                        ),
                                    ),
                                ):
                                    text("Recommendation")
                            with tag(
                                "form", ("action", "./newest"), ("class", "btn-group")
                            ):
                                with tag(
                                    "button",
                                    (
                                        "class",
                                        "btn btn-secondary{}".format(
                                            " active"
                                            if sorttab == constants.Order.DATE
                                            else ""
                                        ),
                                    ),
                                ):
                                    text("Date Added")
                            with tag(
                                "span",
                                (
                                    "style",
                                    "color: white; position: relative; top: 0.3rem;",
                                ),
                                ("class", "ml-2 badge ordernote"),
                                ("data-toggle", "tooltip"),
                                (
                                    "data-original-title",
                                    "Recommendation lists better entries near the top. Date Added lists entries I added to the list recently at the top.",
                                ),
                            ):
                                text("?")
            with tag("ul", klass="navbar-nav p-2"):
                with tag("li", klass="nav-item"):
                    with tag(
                        "a",
                        (
                            "href",
                            "https://github.com/seanbreckenridge/animeshorts",
                        ),
                        ("target", "_blank"),
                        ("rel", "norefferer"),
                    ):
                        doc.stag(
                            "img",
                            ("src", """./images/github.png"""),
                            ("alt", "Source on Github"),
                            ("style", "max-height: 40px; width: auto; invert(80);"),
                        )

    return str(indent(doc.getvalue(), indent_text=True))
