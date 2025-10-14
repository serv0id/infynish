from typing import Any
import requests
from requests.cookies import cookiejar_from_dict
from config import COMPLETE_LECTURE_URL, ACCESS_TOKEN, HEADERS, COURSE_URL

MAX_RETRIES = 2  # retries for failed lecture completion


class Infynish(object):
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = HEADERS
        self.session.cookies = cookiejar_from_dict({
            "access_token": ACCESS_TOKEN
        })

    def get_json_data(self, url: str) -> Any | None:
        try:
            resp = self.session.get(url)
            data = resp.json()
            return data
        except Exception as e:
            print(f"[-] ERROR, {resp.text}")
            print(f"[-] ERROR for {url} : {e}")

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


if __name__ == "__main__":
    data = get_json_data(COURSE_URL)
    if data:
        print(f"[+] Got data")
        try:
            if data["next"]:
                print(f"[+] Next: {data["next"]} (Run again with updated page value)")
        except:
            try:
                if "You do not have permission" in data["detail"]:
                    print(f"[+] HINT, verify that your access_token is correct and not expired")
            except:
                pass
            finally:
                print(f"[-] ERROR, {data}")
                exit()
    else:
        print("[-] Unable to get data")
        print("[x] Exiting")
        exit()
    lecture_count_in_page = get_lecture_count(data)
    print(f"[+] Total lectures {lecture_count_in_page}")

    lecture_ids = get_lecture_ids(data)
    complete_lectures(lecture_ids)  # complete lectures
