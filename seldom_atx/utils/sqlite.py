import json
import os
import sqlite3
import threading

from seldom_atx.logging import log
from seldom_atx.running.config import DataBase, DB_DIR

DB_PATH = os.path.join(DB_DIR, DataBase.DB_NAME)

lock = threading.RLock()


class SQLiteDB:

    def __init__(self, db_path=DB_PATH):
        """
        Connect to the sqlite database
        """
        # check_same_thread=False
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def close(self):
        """
        Close the database connection
        """
        self.connection.close()

    def execute_sql(self, sql: str, *args, **kwargs):
        """
        Execute SQL
        """
        with lock:
            self.cursor.execute(sql, *args, **kwargs)
            self.connection.commit()

    def insert_data(self, table: str, data: dict):
        """
        Insert sql statement
        """
        # 创建占位符，如 (?, ?, ...)
        placeholders = ', '.join('?' for _ in data)
        # 列名，如 column1, column2, ...
        columns = ', '.join(data.keys())
        # 数据值转换为元组
        values = tuple(json.dumps(value) if isinstance(value, (list, dict)) else value
                       for value in data.values())

        # 构建 SQL 语句
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        # 使用参数化查询执行 SQL
        self.execute_sql(sql, values)

    def query_sql(self, sql: str, *args, **kwargs):
        """
        Query SQL
        return: query data
        """
        data_list = []
        with lock:
            rows = self.cursor.execute(sql, *args, **kwargs)
            for row in rows:
                data_list.append(row)
            return data_list

    def select_data(self, table: str, where: dict = None):
        """
        select sql statement
        """
        sql = """select * from {}""".format(table)
        if where is not None:
            sql += 'where {};'.format(self.dict_to_str_and(where))
        return self.query_sql(sql)

    def update_data(self, table: str, data: dict, where: dict):
        """
        update sql statement
        """
        sql = """update {} set """.format(table)
        sql += self.dict_to_str(data)
        if where:
            sql += ' where {};'.format(self.dict_to_str_and(where))
        self.execute_sql(sql)

    def delete_data(self, table: str, where: dict = None):
        """
        delete table data
        """
        sql = """delete from {}""".format(table)
        if where is not None:
            sql += ' where {};'.format(self.dict_to_str_and(where))
        self.execute_sql(sql)

    def init_table(self, table_data: dict):
        """
        init table data
        """
        for table, data_list in table_data.items():
            self.delete_data(table)
            for data in data_list:
                self.insert_data(table, data)
        self.close()

    @staticmethod
    def dict_to_str(data: dict) -> str:
        """
        dict to set str
        """
        tmp_list = []
        for key, value in data.items():
            if value is None:
                tmp = "{k}={v}".format(k=key, v='null')
            elif isinstance(value, int):
                tmp = "{k}={v}".format(k=key, v=str(value))
            else:
                tmp = "{k}='{v}'".format(k=key, v=value)
            tmp_list.append(tmp)
        return ','.join(tmp_list)

    @staticmethod
    def dict_to_str_and(conditions: dict) -> str:
        """
        dict to where and str
        """
        tmp_list = []
        for key, value in conditions.items():
            if value is None:
                tmp = "{k}={v}".format(k=key, v='null')
            elif isinstance(value, int):
                tmp = "{k}={v}".format(k=key, v=str(value))
            else:
                tmp = "{k}='{v}'".format(k=key, v=value)
            tmp_list.append(tmp)
        return ' and '.join(tmp_list)


class Config(SQLiteDB):
    def __init__(self):
        super(Config, self).__init__()
        self.table = DataBase.CONFIG_TABLE

    def set(self, key: str, value):
        sql = f"""insert into {self.table}(key,value) values (:key,:value)"""
        value = json.dumps(value)
        try:
            self.execute_sql(sql, (key, value))
        except sqlite3.IntegrityError as ie:
            log.debug(f"config全局配置已加载=====>key: {key}, value: {value}")
            self.connection.commit()
            sql = "update {} set value=? where key=?".format(self.table)
            self.execute_sql(sql, (value, key))

    def get(self, key: str):
        sql = f"""select value from {self.table} where key=:key"""
        query_res = self.query_sql(sql, (key,))
        try:
            res = query_res[0][0]
        except IndexError:
            return None
        res = json.loads(res)

        return res

    def get_all(self) -> dict:
        """
        获取config表所有数据
        :return: {key:value,...}
        """
        all_data = self.select_data(self.table)
        dic = {}
        for m in all_data:
            dic[m[0]] = json.loads(m[1])
        return dic

    def clear(self):
        """清空表"""
        sql = """delete from {}""".format(self.table)
        self.execute_sql(sql)

    def del_(self, where: dict = None):
        """根据条件删除"""
        sql = """delete from {}""".format(self.table)
        if where is not None:
            sql += ' where {};'.format(self.dict_to_str_and(where))
        self.execute_sql(sql)


# config = Config()
if __name__ == '__main__':
    db = SQLiteDB()
