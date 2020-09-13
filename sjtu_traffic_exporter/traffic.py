import json
import os

from functools import reduce
from typing import List

from requests import Session

from sjtu_traffic_exporter.models import Canteen, Library, SubCanteen

PLUS_HOST = os.environ.get("PLUS_HOST", "sjtu-plus.internal")

class CanteenTraffic:
    def __init__(self):
        self.session = Session()

    def get(self) -> List[Canteen]:
        def process_main_places(place: dict) -> Canteen:
            return Canteen(int(place["Id"]), place["Name"], place["Seat_u"], place["Seat_s"])

        def process_sub_places(parent: Canteen, place: dict) -> SubCanteen:
            return SubCanteen(int(place["Id"]), place["Name"], place["Seat_u"], place["Seat_s"], parent)

        def fetch_sub_canteens(parent: Canteen) -> List[SubCanteen]:
            sub_places = self.session.get(f"http://{PLUS_HOST}/api/sjtu/canteen/{parent.id}").json()
            return [process_sub_places(parent, place) for place in sub_places]
        places = self.session.get("http://{PLUS_HOST}/api/sjtu/canteen").json()
        main_canteens = [process_main_places(place) for place in places]
        sub_canteens = reduce(lambda x, y: (x if x else []) + y, map(fetch_sub_canteens, main_canteens))
        return main_canteens + sub_canteens

    def fields(self) -> List[str]:
        return [canteen.name for canteen in self.get()]


class LibraryTraffic:
    def __init__(self):
        self.session = Session()

    def get(self) -> List[Library]:
        def process_place(place: dict) -> Library:
            return Library(place["areaName"], place["inCounter"], place["max"])

        raw_places = self.session.get("http://{PLUS_HOST}/api/sjtu/library").json()
        places = raw_places["numbers"]
        return [process_place(place) for place in places]

    def fields(self) -> List[str]:
        return [library.name for library in self.get()]
