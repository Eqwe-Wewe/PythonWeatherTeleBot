-- таблица для кеширования запросов пользователей

CREATE TABLE users_property(
chat_id INT UNIQUE,
url VARCHAR(200),
url_regions VARCHAR(200),
url_region VARCHAR(200),
PRIMARY KEY (chat_id)
)ENGINE=InnoDB;