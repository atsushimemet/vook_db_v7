"""仕様書: https://docs.google.com/spreadsheets/d/1KK8aWAntbFzdJ-_642IKRACOqINbjdgnj68Ijwkry-U/edit#gid=0"""
from vook_db_v7.rakuten_api_call import output


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


def test_columns_names_checker():
    file = output(
        brand="リーバイス levis", item="501 66前期", platform_id=1, item_id=1, knowledge_id=1
    )
    if all(file.columns == columns_correct):
        print("columns ok!")
    else:
        print("incorrect columns!")


class TestColumnTypeChecker:
    file = output(
        brand="リーバイス levis",
        item="501 66前期",
        platform_id=1,
        item_id=1,
        knowledge_id=1,
    )

    def test_id_checker(self):
        if self.file[columns_correct[0]].notnull().all():
            assert self.file[columns_correct[0]].dtypes == "int64"

    def test_name_checker(self):
        if self.file[columns_correct[1]].notnull().all():
            assert self.file[columns_correct[1]].dtypes == "O"

    def test_url_checker(self):
        if self.file[columns_correct[2]].notnull().all():
            assert self.file[columns_correct[2]].dtypes == "O"

    def test_price_checker(self):
        if self.file[columns_correct[3]].notnull().all():
            assert self.file[columns_correct[3]].dtypes == "int64"

    def test_knowledge_id_checker(self):
        if self.file[columns_correct[4]].notnull().all():
            assert self.file[columns_correct[4]].dtypes == "int64"

    def test_platform_id_checker(self):
        if self.file[columns_correct[5]].notnull().all():
            assert self.file[columns_correct[5]].dtypes == "int64"

    def test_size_id_checker(self):
        """Tolerate defects. When size_id is not null, O2int64"""
        if self.file[columns_correct[6]].notnull().all():
            assert self.file[columns_correct[6]].dtypes == "O"

    def test_created_at_checker(self):
        if self.file[columns_correct[7]].notnull().all():
            assert self.file[columns_correct[7]].dtypes == "O"

    def test_updated_at_checker(self):
        if self.file[columns_correct[8]].notnull().all():
            assert self.file[columns_correct[8]].dtypes == "O"
