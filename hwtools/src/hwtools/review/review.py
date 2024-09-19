import pandas as pd
from more_itertools import flatten
from pydantic_settings import BaseSettings
from requests import Session


class Settings(BaseSettings):
    TOKEN: str = ""
    CID: int = 0
    UID: int = 0


settings = Settings()

token = settings.TOKEN
uid = settings.UID
cid = settings.CID

session = Session()


def get_user():
    res = session.get(f"https://teaching.applysquare.com/Api/Public/getUser/token/{token}", params={"uid": uid})
    msg = res.json()["message"]
    print(f"欢迎！{msg['realname']}")


def get_homework_list():
    params = {
        "p": 1,
        "sort_order": "publish_at",
        "sort": "DESC",
        "plan_id": -1,
        "uid": uid,
        "cid": cid,
    }
    res = session.get(f"https://teaching.applysquare.com/Api/Work/getPublishList/token/{token}", params=params)
    rows = res.json()["message"]["rows"]
    print("作业列表")
    for row in rows:
        print(f"{row['homework_id']}: {row['title']}")


def get_homework_question(homework_id: str):
    params = {
        "homework_id": homework_id,
        "uid": uid,
        "cid": cid,
    }
    res = session.get(f"https://teaching.applysquare.com/Api/Work/item/token/{token}", params=params)
    a = res.json()
    ql = a["message"]["question_list"]
    return ql[0]


def main():
    get_user()
    get_homework_list()
    homework_id = input("请选择作业：")
    question = get_homework_question(homework_id)

    not_review_list = list(
        flatten(
            session.get(
                f"https://teaching.applysquare.com/Api/Work/getTeacherNotReviewList/token/{token}",
                params={
                    "homework_id": homework_id,
                    "cid": cid,
                    "page": i,
                    "search_key": "",
                    "uid": uid,
                },
            ).json()["message"]["not_review_list"]
            for i in range(1, 5)
        )
    )
    print(f"未评阅 ({len(not_review_list)})：", ", ".join(t["realname"] for t in not_review_list))

    file_name = input("请选择评分文件：")
    result = pd.read_excel(file_name, dtype={"学号": str, "一卡通号": str})
    if "分数" not in result.columns:
        result["分数"] = result["基础分"]
    result_dict = dict(
        flatten([(row["学号"], row["分数"]), (row["一卡通号"], row["分数"])] for _, row in result.iterrows())
    )

    for item in not_review_list:
        score = result_dict[item["student_id"]]
        if not item["is_delay"]:
            res = session.post(
                f"https://teaching.applysquare.com/Api/Work/mark/token/{token}",
                data={
                    "homework_id": homework_id,
                    "be_uid": item["uid"],
                    "score": score,
                    "review_data[0][question_id]": question["id"],
                    "review_data[0][score]": score,
                    "review_data[0][mark_score]": question["homework_score"],
                    "review_data[0][content]": "",
                    "uid": question["uid"],
                    "cid": question["cid"],
                },
            )
        else:
            res = session.post(
                f"https://teaching.applysquare.com/Api/Work/fillDelaySubmitScore/token/{token}",
                data={
                    "hid": homework_id,
                    "be_uid": item["uid"],
                    "score": score,
                    "cid": question["cid"],
                    "change_reason": "",
                },
            )
        print(item, res.json()["message"])


if __name__ == "__main__":
    main()
