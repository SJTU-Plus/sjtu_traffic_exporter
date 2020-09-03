import json
from functools import reduce
from typing import List

from requests import Session

from sjtu_traffic_exporter.models import Canteen, Library, SubCanteen

translation_table = {
    "闵行": "Minhang",
    "徐汇": "Xuhui",
    "第一": "1st",
    "第二": "2nd",
    "第三": "3rd",
    "第四": "4th",
    "第五": "5th",
    "第六": "6th",
    "第七": "7th",
    "餐厅": "Canteen",
    "李政道": "Li Zhengdao",
    "包玉刚": "Bao Yugang",
    "图书馆": "Library",
    "主馆": "Main",
    "研究生": "Postgraduate",
    "西": "Western",
    "清真": "Halal",
    "学生": "Student",
    "社科馆": "Social Science Library",
    "绿园": "Garden",
    "大众": "Public",
    "教工": "Teacher",
    "新疆": "Xinjiang",
    "外婆桥": "Grandma Bridge",
    "东湖面馆": "Eastern Lake Noodles",
    "哈乐": "Hello",
    "统禾": "Tonghe",
    "玉兰苑": "Yulanyuan",
    " ": "_"
}


def translate(src: str) -> str:
    for k, v in translation_table.items():
        src = src.replace(k, v)
    return src


class CanteenTraffic:
    def __init__(self):
        self.session = Session()

    def get(self) -> List[Canteen]:
        def process_main_places(place: dict) -> Canteen:
            return Canteen(int(place["Id"]), translate(place["Name"]), place["Seat_u"], place["Seat_s"])

        def process_sub_places(parent: Canteen, place: dict) -> SubCanteen:
            return SubCanteen(int(place["Id"]), translate(f'{parent.name}_{place["Name"]}'), place["Seat_u"],
                              place["Seat_s"],
                              parent)

        def fetch_sub_canteens(parent: Canteen) -> List[SubCanteen]:
            sub_places = self.session.get(f"https://canteen.sjtu.edu.cn/CARD/Ajax/PlaceDetails/{parent.id}").json()
            return [process_sub_places(parent, place) for place in sub_places]

        places = self.session.get("https://canteen.sjtu.edu.cn/CARD/Ajax/Place").json()
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
            return Library(translate(place["areaName"]), place["inCounter"], place["max"])

        raw_places = self.session.get("https://libsjtu.seanchao.workers.dev/").text
        places = json.loads(raw_places.replace("CountPerson(", "").replace(");", ""))["numbers"]
        return [process_place(place) for place in places]

    def fields(self) -> List[str]:
        return [library.name for library in self.get()]
