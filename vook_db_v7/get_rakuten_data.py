import json
import re
from time import sleep
import os
import pandas as pd
import requests
from vook_db_v5.config import req_params, WANT_ITEMS, REQ_URL, MAX_PAGE, path_output_dir
import datetime
import argparse
import numpy as np
# from logzero import logger

brand = 'リーバイス levis'
item = '501 66前期'

platform_id = 1
item_id = 1
knowledge_id = 1

file_name = 'products_raw'


cnt = 1
keyword = f"{brand} {item} 中古"

req_params["page"] = cnt
req_params["keyword"] = keyword
df = pd.DataFrame(columns=WANT_ITEMS)

# ページループ
# logger.info("loop start!")
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

df['pltaform_id'] = platform_id
df['knowledge_id'] = knowledge_id
df['size_id'] = ''
df['id'] = np.arange(len(df))+1

df_main = df.rename(columns={'itemName':'name', 'itemPrice':'price', 'itemUrl':'url'})
df_main = df_main.reindex(columns=[
    'id','name','url','price','knowledge_id','pltaform_id','size_id'])

run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
df_main['created_at'] = run_time
df_main['updated_at'] = run_time

df_main.to_csv('./data/output/'+file_name+'.csv', index=False)