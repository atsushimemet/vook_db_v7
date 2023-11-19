#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import json
import re
from time import sleep
import sys

from sshtunnel import SSHTunnelForwarder
import pymysql

import numpy as np
import pandas as pd
import requests

from vook_db_v7.config import MAX_PAGE, REQ_URL, WANT_ITEMS, req_params
from vook_db_v7.local_config import get_ec2_config, get_rds_config  # noqa


class DualLogger:
    def __init__(self, file_path, terminal):
        self.terminal = terminal
        self.log = open(file_path, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        # このメソッドはダミーで、必要ない場合があります。
        pass


def main():
    """DBからテーブル取得"""

    config_ec2 = get_ec2_config()
    query = """
    SELECT
        a.id as knowledge_id,
        a.name as knowledge_name,
        b.name as brand_name,
        c.name as line_name
    FROM
        knowledges a
    LEFT JOIN
        brands b
    ON
        a.brand_id = b.id
    LEFT JOIN
        `lines` c
    ON
        a.line_id = c.id
    """
    df_from_db = pd.DataFrame()

    # SSHトンネルの設定
    with SSHTunnelForwarder(
        (config_ec2["host_name"], config_ec2["ec2_port"]),
        ssh_username=config_ec2["ssh_username"],
        ssh_pkey=config_ec2["ssh_pkey"],
        remote_bind_address=(
            config_ec2["rds_end_point"],
            config_ec2["rds_port"],
        ),
    ) as server:
        print(f"Local bind port: {server.local_bind_port}")
        conn = None

        try:
            conn = pymysql.connect(
                **get_rds_config(server.local_bind_port), connect_timeout=10
            )
            cursor = conn.cursor()
            # SQLクエリの実行
            cursor.execute(query)
            for row in cursor:  # column1, column2, ...は取得したいカラム名に合わせて変更してください
                # print(row)

                df_from_db = pd.concat(
                    [df_from_db, pd.DataFrame([row])], ignore_index=True
                )

        except pymysql.MySQLError as e:
            print(f"Error connecting to MySQL: {e}")
        finally:
            if conn is not None:
                conn.close()

    # apiコールした結果からdataframeを出力する関数を定義
    def DataFrame_maker(keyword, platform_id, knowledge_id, size_id):
        cnt = 1
        df = pd.DataFrame(columns=WANT_ITEMS)
        req_params["page"] = cnt
        req_params["keyword"] = keyword
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
        df["size_id"] = size_id
        df_main = df.rename(
            columns={"itemName": "name", "itemPrice": "price", "itemUrl": "url"}  # noqa
        )
        df_main = df_main.reindex(
            columns=[
                "id",
                "name",
                "url",
                "price",
                "knowledge_id",
                "platform_id",
                "size_id",
            ]
        )
        print("price type before:", df_main["price"].dtype)
        df_main["price"] = df_main["price"].astype(int)
        print("price type after:", df_main["price"].dtype)
        run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        df_main["created_at"] = run_time
        df_main["updated_at"] = run_time
        return df_main

    # 対応表を読み出し
    errata_table = pd.read_csv("./data/input/query_ng_ok.csv")

    # エラーワードに対して対応表をもとにレスポンスする関数
    def convertor(input_string, errata_table):
        # 特定のワードが DataFrame に含まれているかどうかを確認し、行番号を表示
        row_indices = errata_table.index[
            errata_table.apply(lambda row: input_string in row.values, axis=1)
        ].tolist()
        if row_indices:
            output = errata_table["corrected"][row_indices[0]]
            print(f"{input_string}を{output}に変換します")
            return output

        else:
            print(f"{input_string}は対応表に存在しません。")
            return input_string

    def validate_input(input_string):
        """
        連続する2文字以上で構成されたワードのみをOKとし、単体1文字またはスペースの前後に単体1文字が含まれるワードをNGとするバリデータ関数
        """
        # 正規表現パターン: 単体1文字またはスペースの前後に単体1文字が含まれるワードを検出
        pattern_ng = re.compile(r"^[!-~]$|\s[!-~]$|^[!-~]\s")

        # 入力文字列がOKパターンに一致するか確認
        # 入力文字列がNGパターンに一致するか確認
        if not pattern_ng.search(input_string):
            return input_string

        else:
            # エラーワードがあればメッセージを吐き、convertor関数によって対応する
            print(f"エラーワード　{input_string}が存在しました:")
            return convertor(input_string, errata_table)

    # 対象のワードリスト作成
    words_brand_name = df_from_db["brand_name"].values
    words_knowledge_name = df_from_db["knowledge_name"].values
    words_line_name = df_from_db["line_name"].values

    for row in np.arange(len(words_brand_name)):
        word = words_brand_name[row]
        words_brand_name[row] = validate_input(word)

    for row in np.arange(len(words_knowledge_name)):
        word = words_knowledge_name[row]
        words_knowledge_name[row] = validate_input(word)

    for row in np.arange(len(words_line_name)):
        word = words_line_name[row]
        words_line_name[row] = validate_input(word)

    # 修正版のテーブルを作成
    df_from_db_corrected = pd.DataFrame(columns=df_from_db.columns)
    df_from_db_corrected["knowledge_id"] = df_from_db["knowledge_id"].values
    df_from_db_corrected["knowledge_name"] = words_knowledge_name
    df_from_db_corrected["brand_name"] = words_brand_name
    df_from_db_corrected["line_name"] = words_line_name

    platform_id = 1  # 楽天
    size_id = 999
    sleep_second = 1

    data = df_from_db_corrected

    n_bulk = len(data)
    df_bulk = pd.DataFrame()

    for n in np.arange(n_bulk):
        brand_name = data.brand_name[n]
        line_name = data.line_name[n]
        knowledge_name = data.knowledge_name[n]
        query = f"{brand_name} {line_name} {knowledge_name} 中古"
        # query validatorが欲しい　半角1文字をなくす

        knowledge_id = data.knowledge_id[n]
        print("検索キーワード:[" + query + "]", "knowledge_id:", knowledge_id)
        output = DataFrame_maker(query, platform_id, knowledge_id, size_id)
        df_bulk = pd.concat([df_bulk, output], ignore_index=True)
        sleep(sleep_second)
        # 429エラー防止のためのタイムストップ

    df_prev = pd.read_csv("./data/output/products_raw_prev.csv")
    PREV_ID_MAX = df_prev["id"].max()
    df_bulk["id"] = np.arange(PREV_ID_MAX, PREV_ID_MAX + len(df_bulk)) + 1

    columns_correct = [
        "id",
        "name",
        "url",
        "price",
        "knowledge_id",
        "platform_id",
        "size_id",
        "created_at",
        "updated_at",
    ]

    def columns_checker(file):
        if all(file.columns == columns_correct):
            print("columns ok!")
        else:
            print("incorrect columns!")

    def id_checker(file):
        if file[columns_correct[0]].notnull().all():
            if file[columns_correct[0]].dtypes == "int64":
                print("id ok!")
            else:
                print("incorrect id values")
        else:
            print("there are null ids")

    def name_checker(file):
        if file[columns_correct[1]].notnull().all():
            if file[columns_correct[1]].dtypes == "O":
                print("name ok!")
            else:
                print("incorrect name values")
        else:
            print("there are null names")

    def url_checker(file):
        if file[columns_correct[2]].notnull().all():
            if file[columns_correct[2]].dtypes == "O":
                print("url ok!")
            else:
                print("incorrect url values")
        else:
            print("there are null urls")

    def price_checker(file):
        if file[columns_correct[3]].notnull().all():
            if file[columns_correct[3]].dtypes == "int64":
                print("price ok!")
            else:
                print("incorrect price value")
        else:
            print("there are null prices")

    def knowledge_id_checker(file):
        if file[columns_correct[4]].notnull().all():
            if file[columns_correct[4]].dtypes == "int64":
                print("knowledge_id ok!")
            else:
                print("incorrect knowledge_id value")
        else:
            print("there are null knowledge_ids")

    def platform_id_checker(file):
        if file[columns_correct[5]].notnull().all():
            if file[columns_correct[5]].dtypes == "int64":
                print("pltaform_id ok!")
            else:
                print("incorrect pltaform_id value")
        else:
            print("there are null pltaform_ids")

    def size_id_checker(file):
        if file[columns_correct[6]].notnull().all():
            if file[columns_correct[6]].dtypes == "int64":
                print("size_id ok!")
            else:
                print("incorrect size_id value")
        else:
            print("there are null size_ids")

    def created_at_checker(file):
        if file[columns_correct[7]].notnull().all():
            if file[columns_correct[7]].dtypes == "O":
                print("created_at ok!")
            else:
                print("incorrect created_at values")
        else:
            print("there are null created_at")

    def updated_at_checker(file):
        if file[columns_correct[8]].notnull().all():
            if file[columns_correct[8]].dtypes == "O":
                print("updated_at ok!")
            else:
                print("incorrect updated_at values")
        else:
            print("there are null updated_at")

    columns_checker(df_bulk)
    id_checker(df_bulk)
    name_checker(df_bulk)
    knowledge_id_checker(df_bulk)
    platform_id_checker(df_bulk)
    url_checker(df_bulk)
    price_checker(df_bulk)
    size_id_checker(df_bulk)
    updated_at_checker(df_bulk)
    created_at_checker(df_bulk)
    print(df_bulk.dtypes)

    file_name = "products_raw_test"
    df_bulk.to_csv("./data/output/" + file_name + ".csv", index=False)


if __name__ == "__main__":
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")

    # ログディレクトリと日付サブディレクトリのパスを作成
    log_directory = os.path.join("log", date_str)

    # ディレクトリが存在しない場合は作成
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    # ログファイルのパスを作成
    log_file_path = os.path.join(log_directory, f"log_{date_str}{time_str}.txt")  # noqa

    # DualLogger を設定
    sys.stdout = DualLogger(log_file_path, sys.stdout)

    # main 関数を実行
    main()

    # ログファイルを閉じる
    sys.stdout.log.close()
