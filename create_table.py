from db import UseDataBase
from config_db import config


def main():
    with UseDataBase(config) as cursor:
        cursor.execute(
            """
                CREATE TABLE users_property
                             (
                             chat_id INT UNIQUE,
                             url VARCHAR(254),
                             url_region VARCHAR(254),
                             PRIMARY KEY (chat_id)
                             );
            """
        )


if __name__ == '__main__':
    main()
