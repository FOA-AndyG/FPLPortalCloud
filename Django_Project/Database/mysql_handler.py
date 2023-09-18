from Database.database_interface import *
import MySQLdb
from sqlalchemy import create_engine
import pandas as pd


class MysqlHandler(DatabaseInterface):
    def __init__(self, **kwargs):
        super().__init__()
        self.ip_address = kwargs.get("ip_address", "localhost")
        self.database_name = kwargs.get("database_name", "itweb")
        self.user = kwargs.get("user", "prog")
        self.password = kwargs.get("password", "prog123")
        self._conn = None
        self._cursor = None

    def __enter__(self):
        super().__enter__()
        print('Connecting to mysql....')
        self._conn = MySQLdb.connect(self.ip_address, self.user, self.password, self.database_name)
        self._cursor = self._conn.cursor()
        return self

    @property
    def get_connection(self):
        return self._conn

    @property
    def get_cursor(self):
        return self._cursor

    def __exit__(self, exception_type, exception_val, exception_trace):
        super().__exit__(exception_type, exception_val, exception_trace)
        try:
            self._cursor.close()
            print('Close cursor')
            self._conn.close()
            print('Close conn.')
        except AttributeError:  # isn't closable
            print('Not closable.')
            return True  # exception handled successfully

    def read_sql_to_dataframe(self, sql: str) -> pd.DataFrame:
        super().read_sql_to_dataframe(sql)
        df = pd.read_sql(sql, self._conn)
        return df


class SQLAlchemyHandler(DatabaseInterface):
    def __init__(self, **kwargs):
        super().__init__()
        self.ip_address = kwargs.get("ip_address", "localhost")
        self.database_name = kwargs.get("database_name", "itweb")
        self.user = kwargs.get("user", "prog")
        self.password = kwargs.get("password", "prog123")
        self.engine = kwargs.get("engine", "mysql+pymysql")
        self._conn = None

    def __enter__(self):
        super().__enter__()
        print('Connecting to mysql SQLAlchemy....')
        self._conn = create_engine(f'{self.engine}://{self.user}:{self.password}@{self.ip_address}/{self.database_name}')
        return self

    @property
    def get_connection(self):
        return self._conn

    def __exit__(self, exception_type, exception_val, exception_trace):
        super().__exit__(exception_type, exception_val, exception_trace)
        try:
            self._conn.dispose()
            print('Close _conn')
        except AttributeError:  # isn't closable
            print('Not closable.')
            return True  # exception handled successfully

    def read_sql_to_dataframe(self, sql: str) -> pd.DataFrame:
        super().read_sql_to_dataframe(sql)
        df = pd.read_sql_query(sql, self._conn)
        return df


class FPLMySQLConnection(DatabaseInterface):
    def __init__(self, **kwargs):
        super().__init__()
        self.ip_address = "192.168.167.88"
        self.database_name = "itweb"
        self.user = "prog"
        self.password = "prog123"
        self.engine = "mysql+pymysql"
        self._conn = None

    def __enter__(self):
        super().__enter__()
        print('Connecting to mysql SQLAlchemy....')
        self._conn = create_engine(f'{self.engine}://{self.user}:{self.password}@{self.ip_address}/{self.database_name}')
        return self

    @property
    def get_connection(self):
        return self._conn

    def __exit__(self, exception_type, exception_val, exception_trace):
        super().__exit__(exception_type, exception_val, exception_trace)
        try:
            # self._cursor.close()
            # print('Close cursor')
            self._conn.dispose()
            print('Close _conn')
        except AttributeError:  # isn't closable
            print('Not closable.')
            return True  # exception handled successfully

    def read_sql_to_dataframe(self, sql: str) -> pd.DataFrame:
        super().read_sql_to_dataframe(sql)
        df = pd.read_sql_query(sql, self._conn)
        return df


class ECANGMySQLConnection(DatabaseInterface):
    def __init__(self):
        super().__init__()
        self.ip_address = "34.96.174.105"
        self.database_name = "wms"
        self.user = "edi"
        self.password = "A!05FOA2021edi"
        self.engine = "mysql+pymysql"
        self._conn = None

    def __enter__(self):
        super().__enter__()
        self._conn = create_engine(f'{self.engine}://{self.user}:{self.password}@{self.ip_address}/{self.database_name}')
        print('ECANGMySQLConnection is connected')
        return self

    @property
    def get_connection(self):
        return self._conn

    def __exit__(self, exception_type, exception_val, exception_trace):
        super().__exit__(exception_type, exception_val, exception_trace)
        try:
            self._conn.dispose()
            print('ECANGMySQLConnection Closed')
        except AttributeError:  # isn't closable
            print('Not closable.')
            return True  # exception handled successfully

    def read_sql_to_dataframe(self, sql: str) -> pd.DataFrame:
        # super().read_sql_to_dataframe(sql)
        df = pd.read_sql_query(sql, self._conn)
        return df
