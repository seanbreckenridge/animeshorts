import os
from enum import Enum

# Filenames
LIST_REC_LINK = "index_rec.html"
LIST_DATE_LINK = "index_newest.html"
PEOPLE_LINK = "people.html"
SOURCES_DIR = "sources"
OUTPUT_DIR = "../output"
LIST_SOURCES = os.path.join(SOURCES_DIR, "list_sources.yaml")
PEOPLE_SOURCES = os.path.join(SOURCES_DIR, "people_sources.yaml")
LIST_CSS = "list.css"
PEOPLE_CSS = "people.css"

# Strings
FULL_NAME = "Anime Shorts"
SHORT_NAME = "AnimeShorts"
LIST_TAB = "List"
PEOPLE_TAB = "People"


class Order(Enum):
    REC = 1
    DATE = 2


user_link = "https://myanimelist.net/profile/purplepinapples"
