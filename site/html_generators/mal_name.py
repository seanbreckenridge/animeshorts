import json
import time
from os import path
from pathlib import Path
from typing import Dict, Iterator, Optional, Any

import requests
import jikanpy

from . import constants


class Crawl:
    """Keep track of time between scrape requests.
    args:
        wait: time between requests
        retry_max: number of times to retry
    """

    def __init__(self, wait: int = 5, retry_max: int = 3):
        self.wait = wait
        self.jikan = jikanpy.Jikan()
        self.retry_max = retry_max
        self.last_scrape = time.time() - (self.wait * 0.5)
        # can let user scrape faster the first time.

    def since_scrape(self) -> float:
        return (time.time() - self.last_scrape) > self.wait

    def wait_till(self) -> None:
        while not self.since_scrape():
            time.sleep(1)

    def get_anime(self, mal_id: int) -> Dict[str, Any]:
        count = 0
        while count < self.retry_max:
            # sleep for successively longer times
            time.sleep(self.wait * count)
            try:
                self.wait_till()
                response = self.jikan.anime(mal_id)
                self.last_scrape = time.time()
                return response
            except requests.exceptions.RequestException:
                pass
            count += 1
        raise NotImplementedError(f"Couldn't cache {mal_id}")


class Cache:
    """class to manage caching API requests for MAL names"""

    def __init__(self, crawler: Optional[Crawl] = None):
        self.jsonpath = Path(constants.this_dir).parent / "mal_name_cache.json"
        self.write_to_cache_const = 5
        self.write_to_cache_periodically = self.write_to_cache_const
        self.crawler = crawler or Crawl()
        self.items: Dict[str, str] = {}
        if not path.exists(self.jsonpath):
            open(self.jsonpath, "a").close()
        with open(self.jsonpath, "r") as js_f:
            try:
                self.items = json.load(js_f)
            except json.JSONDecodeError:  # file is empty or broken
                pass
        self.update_json_file()

    def update_json_file(self) -> None:
        with open(self.jsonpath, "w") as f:
            json.dump(self.items, f, indent=4)

    def _mal_crawl_name(self, mal_id: int) -> str:
        """Downloads the name of the MAL id"""
        print(f"[Cache][Crawler] Downloading name for MAL ID {mal_id}")
        return str(self.crawler.get_anime(mal_id)["title"])

    def download_name(self, id: int) -> str:
        self.write_to_cache_periodically -= 1
        if self.write_to_cache_periodically < 0:
            self.write_to_cache_periodically = self.write_to_cache_const
            self.update_json_file()
        return self._mal_crawl_name(id)

    def __contains__(self, id: int) -> bool:
        """defines the 'in' keyword on cache."""
        return str(id) in self.items

    def get(self, id: int) -> str:
        if self.__contains__(id):
            # print("[Cache] Found name for id {} in cache".format(id))
            return self.items[str(id)]
        else:
            self.items[str(id)] = self.download_name(id)
            return self.items[str(id)]

    def __iter__(self) -> Iterator[str]:
        return self.items.__iter__()
