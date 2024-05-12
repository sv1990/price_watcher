#!/usr/bin/env python

import json
from abc import abstractmethod
from datetime import datetime
from pathlib import Path
from time import sleep

import pandas as pd
import requests
from bs4 import BeautifulSoup


class PriceWatcherBase:
    def __init__(self, url: str, description: str) -> None:
        self.url = url
        self.description = description

    @abstractmethod
    def get_price_impl(self) -> pd.DataFrame:
        pass

    def get_price(self, now: datetime) -> float | str:
        df = self.get_price_impl()
        df["url"] = self.url
        df["description"] = self.description
        df["timestamp"] = now
        return df


class Otto(PriceWatcherBase):
    def get_price_impl(self) -> pd.DataFrame:
        response = requests.get(self.url)
        if response.status_code != 200:
            raise ValueError(f"Response {response.status_code}")
        soup = BeautifulSoup(response.text, "html.parser")
        data = json.loads(soup.find_all(id="js_pdp_variationTrackingData")[0].string)
        df = pd.json_normalize(data)
        df = df.loc[
            df["labels.hd_Price"].notna(),
            [
                "labels.hd_Discount",
                "labels.hd_Availability",
                "labels.hd_Price",
                "labels.hd_Stock",
                "labels.hd_Color",
                "labels.hd_Retailer",
            ],
        ]
        df.columns = df.columns.str.removeprefix("labels.hd_")
        return df


def main() -> None:
    watchers: list[PriceWatcherBase] = [
        Otto(
            "https://www.otto.de/p/belkin-belkin-drahtloses-3-in-1-magsafe-ladepad-smartphone-ladegeraet-inkl-netzteil-kompatibel-fuer-iphone-der-serie-15-14-13-12-fuer-iphone-apple-watch-und-airpods-wireless-ladegeraet-ladestation-C1614884204/#variationId=1614884205",
            "Belkin drahtloses 3-in-1 MagSafe Ladepad",
        ),
        Otto(
            "https://www.otto.de/p/apple-iphone-15-128gb-smartphone-15-5-cm-6-1-zoll-128-gb-speicherplatz-48-mp-kamera-1786938266/#variationId=1786938267",
            "iPhone 15",
        ),
        Otto(
            "https://www.otto.de/p/apple-iphone-14-128gb-smartphone-15-4-cm-6-1-zoll-128-gb-speicherplatz-12-mp-kamera-1676826909/#variationId=1676023634",
            "iPhone 14",
        ),
        Otto(
            "https://www.otto.de/p/apple-iphone-13-smartphone-15-4-cm-6-1-zoll-128-gb-speicherplatz-12-mp-kamera-1503513747/#variationId=1503513780",
            "iPhone 13",
        ),
        Otto(
            "https://www.otto.de/p/apple-watch-series-9-gps-aluminium-45mm-m-l-smartwatch-4-5-cm-1-77-zoll-watch-os-10-sport-band-1786971288/#variationId=1786971565",
            "Apple Watch 9 45mm M/L GPS",
        ),
        Otto(
            "https://www.otto.de/p/apple-watch-series-9-gps-aluminium-41mm-s-m-smartwatch-4-1-cm-1-69-zoll-watch-os-10-sport-band-1786966413/#variationId=1786966782",
            "Apple Watch 9 41mm S/M GPS",
        ),
        Otto(
            "https://www.otto.de/p/apple-watch-series-9-gps-plus-cellular-45mm-aluminium-s-m-smartwatch-4-5-cm-1-77-zoll-watch-os-10-sport-band-1786966196/#variationId=1786966578",
            "Apple Watch 9 45mm M/L GPS+LTE",
        ),
        Otto(
            "https://www.otto.de/p/apple-watch-series-9-gps-plus-cellular-41mm-aluminium-s-m-smartwatch-4-1-cm-1-61-zoll-watch-os-10-sport-band-1786965023/#variationId=1786965434",
            "Apple Watch 9 41mm S/M GPS+LTE",
        ),
        Otto(
            "https://www.otto.de/p/apple-watch-se-gps-40-mm-aluminium-s-m-smartwatch-4-cm-1-57-zoll-watch-os-10-sport-band-1786965324/#variationId=1786965487",
            "Apple Watch SE 2 40mm S/M GPS",
        ),
    ]

    output_folder = Path("data/raw")
    output_folder.mkdir(exist_ok=True, parents=True)
    output: list[pd.DataFrame] = []
    now = datetime.now()

    for watcher in watchers:
        sleep(1)
        try:
            output.append(watcher.get_price(now))
        except Exception as e:
            print(f"{watcher.description}: {e!r}")
    pd.concat(output, ignore_index=True).to_csv(
        output_folder / f"{now.isoformat()}.csv", index=False
    )


if __name__ == "__main__":
    main()
