from db import UseDataBase
from config_db import config


with UseDataBase(config) as cursor:
    cursor.execute("""CREATE TABLE users_property(
                    chat_id INT UNIQUE,
                    url VARCHAR(254),
                    url_regions VARCHAR(254),
                    url_region VARCHAR(254),
                    PRIMARY KEY (chat_id)
                    );""")
