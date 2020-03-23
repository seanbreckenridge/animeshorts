from yattag import Doc, indent
import constants

# generates the navbar, and forms for the top of the page.


def navbar(active, **kwargs):
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
        with tag("a", klass="navbar-brand text-nowrap mr-3 my-2", href="/"):
            text(constants.FULL_NAME)
        # collapsable page links
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
                        ("href", "/"),
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
                        ("href", "/people"),
                    ):
                        text(constants.PEOPLE_TAB)
            if active == constants.LIST_TAB:
                with tag("ul", klass="navbar-nav"):
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
                            ("id", "orderchoice"),
                        ):
                            with tag(
                                "button",
                                (
                                    "class",
                                    "btn btn-secondary{}".format(
                                        " active"
                                        if sorttab == constants.order.REC
                                        else ""
                                    ),
                                ),
                            ):
                                text("Recommendation")
                            with tag(
                                "button",
                                (
                                    "class",
                                    "btn btn-secondary{}".format(
                                        " active"
                                        if sorttab == constants.order.DATE
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
                                ("class", "mx-2 badge ordernote"),
                                ("data-toggle", "tooltip"),
                                (
                                    "data-original-title",
                                    "Recommendation lists better entries near the top. Date Added lists entries I added to the list recently at the top.",
                                ),
                            ):
                                text("?")
                            with tag(
                                "a",
                                (
                                    "href",
                                    "https://github.com/seanbreckenridge/animeshorts",
                                ),
                                ("class", "ml-1"),
                            ):
                                doc.stag(
                                    "img",
                                    (
                                        "src",
                                        """{{url_for('static', filename='images/GitHub-Mark-Light-64px.png')}}""",
                                    ),
                                    ("alt", "Source on Github"),
                                    ("style", "max-height: 32px; width: auto;"),
                                )
        with tag(
            "form",
            ("style", "display: none;"),
            ("id", "choiceform"),
            ("method", "get"),
            ("action", "/"),
        ):
            doc.stag("input", ("type", "hidden"), ("id", "sort"), ("name", "sort"))

    return indent(doc.getvalue(), indent_text=True)
