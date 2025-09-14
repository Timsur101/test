CREATE DATABASE IF NOT EXISTS app;

USE app;
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) UNIQUE
);

CREATE TABLE IF NOT EXISTS buy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_user INT,
    product VARCHAR(255),
    price FLOAT,
    comment TEXT,
    category_id INT,
    date DATE,
    FOREIGN KEY (category_id) REFERENCES categories(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

INSERT IGNORE INTO categories (name) VALUES
    ('Продукты'),
    ('Транспорт'),
    ('Жилье'),
    ('Развлечения'),
    ('Другое');

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255)
)
