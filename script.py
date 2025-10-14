import click
import requests
from requests.cookies import cookiejar_from_dict
from loguru import logger
from config import COMPLETE_LECTURE_URL, ACCESS_TOKEN, HEADERS, COURSE_URL


class Infynish(object):
    def __init__(self, course_id: int):
        self.session = requests.Session()
        self.session.headers = HEADERS
        self.session.cookies = cookiejar_from_dict({
            "access_token": ACCESS_TOKEN
        })

        self.course_id = course_id

    def get_lectures_data(self) -> dict:
        resp = self.session.get(url=COURSE_URL.format(self.course_id), params={
            "caching_intent": True,
            "curriculum_types": "chapter,lecture,practice,quiz,role-play",
            "fields[asset]": "title,filename,asset_type,status,time_estimation,is_external",
            "fields[chapter]": "title,object_index,is_published,sort_order",
            "fields[lecture]": "title,object_index,is_published,sort_order,created,asset,supplementary_assets,is_free",
            "fields[practice]": "title,object_index,is_published,sort_order",
            "fields[quiz]": "title,object_index,is_published,sort_order,type",
            "page": 1,
            "page_size": 9999  # absurd number to fetch max results
        })

        if resp.status_code == 200:
            return resp.json()

        logger.error("Please check your credentials! Shutting down.")
        raise SystemExit

    def process_lectures(self, lectures_data: dict) -> None:
        for element in lectures_data["results"]:
            if element["_class"] == "lecture":
                self.complete_lecture(element["id"])

    def complete_lecture(self, lecture_id: int) -> None:
        resp = self.session.post(url=COMPLETE_LECTURE_URL.format(self.course_id), json={
            "downloaded": False,
            "lecture_id": lecture_id
        })

        if resp.status_code == 201:
            logger.info(f"Watched lecture {lecture_id}!")
        else:
            logger.error(f"Some error occured while watching {lecture_id}!")


@logger.catch
@click.command()
@click.option('--course', required=True, help="The course ID")
def main(course: int) -> None:
    infynish = Infynish(course)

    lectures = infynish.get_lectures_data()
    infynish.process_lectures(lectures)


if __name__ == "__main__":
    main()
