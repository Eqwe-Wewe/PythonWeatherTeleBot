from psycopg2 import connect, Error
from config_db import config


class DataBaseError(Exception):
    pass


class UseDataBase:
    def __init__(self, config: dict):
        self.config = config

    def __enter__(self):
        try:
            self.conn = connect(**self.config)
            self.cursor = self.conn.cursor()
            return self.cursor
        except Error as err:
            self.conn.rollback()
            raise DataBaseError(err)

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        if exc_type:
            raise exc_type(exc_value)
