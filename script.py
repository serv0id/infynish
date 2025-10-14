from typing import Any
import requests
from requests.cookies import cookiejar_from_dict
from loguru import logger

from config import COMPLETE_LECTURE_URL, ACCESS_TOKEN, HEADERS, COURSE_URL

MAX_RETRIES = 2  # retries for failed lecture completion


class Infynish(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = HEADERS
        self.session.cookies = cookiejar_from_dict({
            "access_token": ACCESS_TOKEN
        })

    def get_lectures_data(self) -> dict:
        resp = self.session.get(url=COURSE_URL, params={
            "caching_intent": True,
            "curriculum_types": "chapter,lecture,practice,quiz,role-play",
            "fields[asset]": "title,filename,asset_type,status,time_estimation,is_external",
            "fields[chapter]": "title,object_index,is_published,sort_order",
            "fields[lecture]": "title,object_index,is_published,sort_order,created,asset,supplementary_assets,is_free",
            "fields[practice]": "title,object_index,is_published,sort_order",
            "fields[quiz]": "title,object_index,is_published,sort_order,type",
            "page": 1,
            "page_size": 9999
        })

        if resp.status_code == 200:
            return resp.json()

        logger.error("Please check your credentials! Shutting down.")
        raise SystemExit

    def get_lecture_count(self, data: dict) -> int:
        count = 0
        for obj in data["results"]:
            if obj["_class"] == "lecture":
                count += 1
        return count

    def get_lecture_ids(self, data: dict) -> list:
        lecture_ids = []
        for obj in data["results"]:
            if obj["_class"] == "lecture":
                lecture_ids.append(obj["id"])
        return lecture_ids

    def complete_lectures(self, lecture_ids: list, attempt: int = 1):
        HEADERS["content-type"] = "application/json"
        try_again = []
        completed = []
        if attempt > MAX_RETRIES:
            print(f"[+] Retries exceeded {MAX_RETRIES}")
            print(f"[+] IDs left to try {lecture_ids}")
            print(f"[+] Left to try {len(lecture_ids)}")
            return
        for id in lecture_ids:
            try:
                data = {"lecture_id": id, "downloaded": False}
                resp = requests.post(url=COMPLETE_LECTURE_URL, headers=HEADERS, cookies=COOKIE, json=data)
                if resp.status_code == 201:
                    completed.append(id)
                    print(f"[+] Completed lecture {id}")
                else:
                    try_again.append(id)
                    print(f"[-] ERROR {id}")
                    print(f"[-] ERROR {resp.text}")
            except Exception as e:
                try_again.append(id)
                print(f"[-] ERROR {e}")

        if try_again:
            print(f"[+] Trying again for {len(try_again)} lectures")
            attempt += 1
            self.complete_lectures(try_again, attempt)
        else:
            print(f"[+] Completed {len(completed)}/{len(lecture_ids)} lectures")


def main() -> None:
    lecture_count_in_page = get_lecture_count(data)
    print(f"[+] Total lectures {lecture_count_in_page}")

    lecture_ids = get_lecture_ids(data)
    complete_lectures(lecture_ids)  # complete lectures


if __name__ == "__main__":
    main()
