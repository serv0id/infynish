import os
import requests
from config import COMPLETE_LECTURE_URL, ACCESS_TOKEN


PAGE_NUMBER = 1  # page indexing starts with 1
PAGE_SIZE = 9999  # did not want to implement page handling, this is workaround
COURSE_URL = "https://springboard.udemy.com/api-2.0/courses/4242194/subscriber-curriculum-items/?caching_intent=True&curriculum_types=chapter%2Clecture%2Cpractice%2Cquiz%2Crole-play&fields%5Basset%5D=title%2Cfilename%2Casset_type%2Cstatus%2Ctime_estimation%2Cis_external&fields%5Bchapter%5D=title%2Cobject_index%2Cis_published%2Csort_order&fields%5Blecture%5D=title%2Cobject_index%2Cis_published%2Csort_order%2Ccreated%2Casset%2Csupplementary_assets%2Cis_free&fields%5Bpractice%5D=title%2Cobject_index%2Cis_published%2Csort_order&fields%5Bquiz%5D=title%2Cobject_index%2Cis_published%2Csort_order%2Ctype&page={PAGE_NUMBER}&page_size={PAGE_SIZE}".format(
    PAGE_NUMBER=PAGE_NUMBER, PAGE_SIZE=PAGE_SIZE)
HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "x-requested-with": "XMLHttpRequest"
}
COOKIE = {
    "access_token": ACCESS_TOKEN
}
MAX_RETRIES = 2  # retries for failed lecture completion


def get_json_data(url: str) -> dict:
    try:
        resp = requests.get(url=url, headers=HEADERS, cookies=COOKIE)
        data = resp.json()
        return data
    except Exception as e:
        print(f"[-] ERROR, {resp.text}")
        print(f"[-] ERROR for {url} : {e}")


def get_lecture_count(data: dict) -> int:
    count = 0
    for obj in data["results"]:
        if obj["_class"] == "lecture":
            count += 1
    return count


def get_lecture_ids(data: dict) -> list:
    lecture_ids = []
    for obj in data["results"]:
        if obj["_class"] == "lecture":
            lecture_ids.append(obj["id"])
    return lecture_ids


def complete_lectures(lecture_ids: list, attempt: int = 1):
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
        complete_lectures(try_again, attempt)
    else:
        print(f"[+] Completed {len(completed)}/{len(lecture_ids)} lectures")


# ---

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
