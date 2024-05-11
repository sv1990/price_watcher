#!/usr/bin/env python

import json
from abc import abstractmethod
from datetime import datetime
from pathlib import Path

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


class PriceWatcherBase:
    def __init__(self, url: str, description: str) -> None:
        self.url = url
        self.description = description

    @abstractmethod
    def get_price_impl(self, driver: Chrome) -> float | str:
        pass

    def get_price(self, driver: Chrome) -> float | str:
        driver.get(self.url)
        return self.get_price_impl(driver)


class Otto(PriceWatcherBase):
    def get_price_impl(self, driver: Chrome) -> float | str:
        element = driver.find_element(
            By.CLASS_NAME, "js_pdp_price__retail-price__value"
        )
        return element.text


def main() -> None:
    watchers: list[PriceWatcherBase] = [
        Otto(
            "https://www.otto.de/p/belkin-belkin-drahtloses-3-in-1-magsafe-ladepad-smartphone-ladegeraet-inkl-netzteil-kompatibel-fuer-iphone-der-serie-15-14-13-12-fuer-iphone-apple-watch-und-airpods-wireless-ladegeraet-ladestation-C1614884204/#variationId=1614884205",
            "Belkin drahtloses 3-in-1 MagSafe Ladepad",
        ),
        Otto(
            "https://www.otto.de/p/apple-iphone-15-128gb-smartphone-15-5-cm-6-1-zoll-128-gb-speicherplatz-48-mp-kamera-1786938266/#variationId=1786938267",
            "iPhone 15 Black",
        ),
        Otto(
            "https://www.otto.de/p/apple-iphone-14-128gb-smartphone-15-4-cm-6-1-zoll-128-gb-speicherplatz-12-mp-kamera-1676826909/#variationId=1676023634",
            "iPhone 14 Black",
        ),
        Otto(
            "https://www.otto.de/p/apple-iphone-13-smartphone-15-4-cm-6-1-zoll-128-gb-speicherplatz-12-mp-kamera-1503513747/#variationId=1503513780",
            "iPhone 13 Midnight",
        ),
    ]

    options = Options()
    options.headless = True
    driver = Chrome(options=options)
    driver.maximize_window()
    driver.implicitly_wait(10)

    output_folder = Path("data/raw")
    output_folder.mkdir(exist_ok=True, parents=True)
    output = []
    for watcher in watchers:
        try:
            price = watcher.get_price(driver)
            output.append(
                {"description": watcher.description, "url": watcher.url, "price": price}
            )
        except Exception as e:
            print(f"{e!r}")
    with open(
        output_folder / f"{datetime.now().isoformat()}.json", "w", encoding="utf-8"
    ) as f:
        json.dump(output, f)


if __name__ == "__main__":
    main()
