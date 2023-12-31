import datetime
import json
from time import sleep

import numpy as np
import pandas as pd
import requests

from vook_db_v7.config import MAX_PAGE, REQ_URL, WANT_ITEMS, req_params


brand = "リーバイス levis"
item = "501 66後期"

platform_id = 1
item_id = 1
knowledge_id = 10

df_prev = pd.read_csv("./data/output/products_raw_prev.csv")
PREV_ID_MAX = df_prev["id"].max()


# ページループ
# logger.info("loop start!")
def output(
    brand: str, item: str, platform_id: int, item_id: int, knowledge_id: int
) -> pd.DataFrame:
    cnt = 1
    keyword = f"{brand} {item} 中古"

    req_params["page"] = cnt
    req_params["keyword"] = keyword
    df = pd.DataFrame(columns=WANT_ITEMS)
    while True:
        req_params["page"] = cnt
        res = requests.get(REQ_URL, req_params)
        res_code = res.status_code
        res = json.loads(res.text)
        if res_code != 200:
            print(
                f"""
            ErrorCode -> {res_code}\n
            Error -> {res['error']}\n
            Page -> {cnt}"""
            )
        else:
            if res["hits"] == 0:
                print("返ってきた商品数の数が0なので、ループ終了")
                break
            tmp_df = pd.DataFrame(res["Items"])[WANT_ITEMS]
            df = pd.concat([df, tmp_df], ignore_index=True)
        if cnt == MAX_PAGE:
            print("MAX PAGEに到達したので、ループ終了")
            break
        # logger.info(f"{cnt} end!")
        cnt += 1
        # リクエスト制限回避
        sleep(1)

        print("Finished!!")

    df["platform_id"] = platform_id
    df["knowledge_id"] = knowledge_id
    df["size_id"] = 999
    df["id"] = np.arange(PREV_ID_MAX, PREV_ID_MAX + len(df)) + 1

    df_main = df.rename(
        columns={"itemName": "name", "itemPrice": "price", "itemUrl": "url"}
    )
    df_main = df_main.reindex(
        columns=["id", "name", "url", "price", "knowledge_id", "platform_id", "size_id"]
    )

    df_main["price"] = df_main["price"].astype(int)

    run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    df_main["created_at"] = run_time
    df_main["updated_at"] = run_time
    return df_main


def save(df_main: pd.DataFrame) -> None:
    file_name = "products_raw"
    df_main.to_csv("./data/output/" + file_name + ".csv", index=False)


def main():
    df_main = output(
        brand=brand,
        item=item,
        platform_id=platform_id,
        item_id=item_id,
        knowledge_id=knowledge_id,
    )
    save(df_main)


if __name__ == "__main__":
    main()
