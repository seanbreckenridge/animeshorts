import time

import requests
import jikanpy


class crawl:
    """Keep track of time between scrape requests.
    args:
        wait: time between requests
        retry_max: number of times to retry
    """

    def __init__(self, wait, retry_max):
        self.wait = wait
        self.jikan = jikanpy.Jikan()
        self.retry_max = retry_max
        self.last_scrape = time.time() - (self.wait * 0.5)
        # can let user scrape faster the first time.

    def since_scrape(self):
        return (time.time() - self.last_scrape) > self.wait

    def wait_till(self):
        while not self.since_scrape():
            time.sleep(1)

    def get_anime(self, mal_id: int):
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
