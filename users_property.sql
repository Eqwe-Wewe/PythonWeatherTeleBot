-- таблица для кеширования запросов пользователей

CREATE TABLE IF NOT EXISTS users_property
                           (
                           chat_id INT UNIQUE,
                           url VARCHAR(254),
                           url_region VARCHAR(254),
                           PRIMARY KEY (chat_id)
                           );
