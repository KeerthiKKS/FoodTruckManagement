drop database food_truck;
create database food_truck;
use food_truck;

CREATE TABLE food_truck (
    food_truck_id INT AUTO_INCREMENT PRIMARY KEY,
    food_truck_title VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    verification_status VARCHAR(255) DEFAULT 'not verified'
);

CREATE TABLE delivery_boy (
    delivery_boy_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    address_proof VARCHAR(255) NOT NULL,
    verification_status VARCHAR(255) DEFAULT 'not verified'
);

CREATE TABLE customers (
    customer_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    gender VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    verification_status VARCHAR(255) DEFAULT 'not verified'
);
CREATE TABLE truck_timings (
    truck_timing_id INT AUTO_INCREMENT PRIMARY KEY,
    from_time VARCHAR(255) NOT NULL,
    to_time VARCHAR(255) NOT NULL,
    date VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    food_truck_id INT NOT NULL,
    FOREIGN KEY (food_truck_id)
        REFERENCES food_truck (food_truck_id)
);
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    food_truck_id INT NOT NULL,
    FOREIGN KEY (food_truck_id)
        REFERENCES food_truck (food_truck_id)
);
CREATE TABLE food_items (
    food_item_id INT AUTO_INCREMENT PRIMARY KEY,
    food_item_name VARCHAR(255) NOT NULL,
    price VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    units VARCHAR(255) NOT NULL,
    category_id INT NOT NULL,
    picture VARCHAR(255) NOT NULL,
    status VARCHAR(255) NOT NULL default 'Available',
    description VARCHAR(255) NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES categories (category_id)
);
alter table food_items modify status VARCHAR(255) NOT NULL default 'Available';
CREATE TABLE customer_orders (
    customer_order_id INT AUTO_INCREMENT PRIMARY KEY,
    status VARCHAR(255) NOT NULL,
    customer_id INT NOT NULL,
    date DATETIME DEFAULT CURRENT_TIMESTAMP,
    delivery_boy_id INT,
    food_truck_id INT NOT NULL,
    truck_timing_id INT NOT NULL,
    FOREIGN KEY (delivery_boy_id)
        REFERENCES delivery_boy (delivery_boy_id),
    FOREIGN KEY (customer_id)
        REFERENCES customers (customer_id),
    FOREIGN KEY (food_truck_id)
        REFERENCES food_truck (food_truck_id),
    FOREIGN KEY (truck_timing_id)
        REFERENCES truck_timings (truck_timing_id)
);

CREATE TABLE customer_order_items (
    customer_order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_order_id INT NOT NULL,
    food_item_id INT NOT NULL,
    quantity INT NOT NULL,
    FOREIGN KEY (customer_order_id)
        REFERENCES customer_orders (customer_order_id),
    FOREIGN KEY (food_item_id)
        REFERENCES food_items (food_item_id)
);

CREATE TABLE review (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_order_item_id INT NOT NULL,
    review VARCHAR(255) NOT NULL,
    rating VARCHAR(255) NOT NULL,
    FOREIGN KEY (customer_order_item_id)
        REFERENCES customer_order_items (customer_order_item_id)
);