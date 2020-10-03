import logging
import time
from scheduler.scraper import ScraperThread
from threading import Thread


class ProgressThread(Thread):
    def __init__(self) -> None:
        self.progress = 0
        super().__init__()

    def run(self) -> None:
        try:
            scraper = ScraperThread()
            scraper.start()

            progress = scraper.progress
            print(progress)
            while scraper.is_alive():
                time.sleep(1)
                if progress != scraper.progress:
                    progress = scraper.progress
                    print(progress)
        except Exception as e:
            print(e)

    def stop(self) -> None:
        self._stop()


progress = ProgressThread()
progress.run()
