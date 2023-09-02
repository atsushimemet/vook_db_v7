#!/usr/bin/env python
# coding: utf-8

# Import
from vook_db_v5.config import (
    max_products,
    step,
    params,
    start_num,
    COL_NAMES,
    REQ_URL_CATE,
    KNOWLEDGE_ID,
    PLATFORM_ID,
    run_time,
)
import json
import pandas as pd
import requests


def main():
    l_df = []
    for inc in range(0, max_products, step):
        params["start"] = start_num + inc
        df = pd.DataFrame(columns=COL_NAMES)
        res = requests.get(url=REQ_URL_CATE, params=params)
        res_cd = res.status_code
        if res_cd != 200:
            print("Bad request")
            break
        else:
            res = json.loads(res.text)
            if len(res["hits"]) == 0:
                print("If the number of returned items is 0, the loop ends.")
            print("Get Data")
            l_hit = []
            for h in res["hits"]:
                l_hit.append(
                    (
                        h["index"],
                        h["name"],
                        h["url"],
                        h["price"],
                        KNOWLEDGE_ID,
                        PLATFORM_ID,
                        "",
                        # 現在の日付と時刻を取得 & フォーマットを指定して文字列に変換
                        run_time,
                        # 現在の日付と時刻を取得 & フォーマットを指定して文字列に変換
                        run_time,
                    )
                )
            df = pd.DataFrame(l_hit, columns=COL_NAMES)
            l_df.append(df)

    products_raw = pd.concat(l_df, axis=0, ignore_index=True)
    products_raw.to_csv("./data/output/products_raw.csv", index=False)
    print("fin")


if __name__ == "__main__":
    main()