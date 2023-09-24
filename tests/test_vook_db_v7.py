"""仕様書: https://docs.google.com/spreadsheets/d/1KK8aWAntbFzdJ-_642IKRACOqINbjdgnj68Ijwkry-U/edit#gid=0"""

from vook_db_v7 import __version__


def test_version():
    assert __version__ == "0.1.0"


columns_correct = [
    "id",
    "name",
    "url",
    "price",
    "knowledge_id",
    "pltaform_id",
    "size_id",
    "created_at",
    "updated_at",
]


def test_columns_names_checker(file):
    if all(file.columns == columns_correct):
        print("columns ok!")
    else:
        print("incorrect columns!")


def test_id_checker(file):
    if file[columns_correct[0]].notnull().all():
        if file[columns_correct[0]].dtypes == "int64":
            print("id ok!")
        else:
            print("incorrect id values")
    else:
        print("there are null ids")


def test_name_checker(file):
    if file[columns_correct[1]].notnull().all():
        if file[columns_correct[1]].dtypes == "O":
            print("name ok!")
        else:
            print("incorrect name values")
    else:
        print("there are null names")


def test_url_checker(file):
    if file[columns_correct[2]].notnull().all():
        if file[columns_correct[2]].dtypes == "O":
            print("url ok!")
        else:
            print("incorrect url values")
    else:
        print("there are null urls")


def test_price_checker(file):
    if file[columns_correct[3]].notnull().all():
        if file[columns_correct[3]].dtypes == "int64":
            print("price ok!")
        else:
            print("incorrect price value")
    else:
        print("there are null prices")


def test_knowledge_id_checker(file):
    if file[columns_correct[4]].notnull().all():
        if file[columns_correct[4]].dtypes == "int64":
            print("knowledge_id ok!")
        else:
            print("incorrect knowledge_id value")
    else:
        print("there are null knowledge_ids")


def test_pltaform_id_checker(file):
    if file[columns_correct[5]].notnull().all():
        if file[columns_correct[5]].dtypes == "int64":
            print("pltaform_id ok!")
        else:
            print("incorrect pltaform_id value")
    else:
        print("there are null pltaform_ids")


def test_size_id_checker(file):
    if file[columns_correct[6]].notnull().all():
        if file[columns_correct[6]].dtypes == "int64":
            print("size_id ok!")
        else:
            print("incorrect size_id value")
    else:
        print("there are null size_ids")


def test_created_at_checker(file):
    if file[columns_correct[7]].notnull().all():
        if file[columns_correct[7]].dtypes == "O":
            print("created_at ok!")
        else:
            print("incorrect created_at values")
    else:
        print("there are null created_at")


def test_updated_at_checker(file):
    if file[columns_correct[8]].notnull().all():
        if file[columns_correct[8]].dtypes == "O":
            print("updated_at ok!")
        else:
            print("incorrect updated_at values")
    else:
        print("there are null updated_at")
