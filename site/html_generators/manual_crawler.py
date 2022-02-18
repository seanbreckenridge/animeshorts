import time

from typing import Any, Dict

import requests
import jikanpy


class Crawl:
    """Keep track of time between scrape requests.
    args:
        wait: time between requests
        retry_max: number of times to retry
    """

    def __init__(self, wait: int , retry_max: int):
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
        raise NotImplementedError(f"Couldnt cache {mal_id}")
