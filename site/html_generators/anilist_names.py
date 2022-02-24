import sys
import json
from pathlib import Path
from typing import Dict, Optional

import time
import requests

from . import constants


class AniListNames(object):
    def __init__(self) -> None:
        self.jsonpath = Path(constants.this_dir).parent / "anilist_cache.json"
        self.data: Dict[str, Optional[str]] = {}
        if self.jsonpath.exists():
            self.data = json.loads(self.jsonpath.read_text())

    def write(self) -> None:
        self.jsonpath.write_text(json.dumps(self.data, indent=4, sort_keys=True))

    def fetch(self, mal_id: int) -> Optional[str]:
        query = """query($id: Int, $type: MediaType){Media(idMal: $id, type: $type){siteUrl}}"""
        variables = {"id": mal_id, "type": "ANIME"}
        url = "https://graphql.anilist.co"
        time.sleep(1)
        print(f"Requesting Anilist ID for {mal_id}", file=sys.stderr)
        response = requests.post(url, json={"query": query, "variables": variables})
        if response.status_code > 400:
            return None
        data = response.json()
        return str(data["data"]["Media"]["siteUrl"])

    def get(self, mal_id: int) -> Optional[str]:
        sm = str(mal_id)
        if sm in self.data:
            return self.data[sm]
        else:
            self.data[sm] = self.fetch(mal_id)
            self.write()
            return self.data[sm]
