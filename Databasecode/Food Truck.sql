create database food_truck;
use food_truck;

create table food_truck(
food_truck_id int auto_increment primary key,
name varchar(255) not null,
email varchar(255) not null unique,
password varchar(255) not null,
phone varchar(255) not null,
verification_status varchar(255) default 'not verified'
);
alter table food_truck add food_truck_title varchar(255) not null;
create table delivery_boy(
delivery_boy_id int auto_increment primary key,
name varchar(255) not null,
email varchar(255) not null unique,
password varchar(255) not null,
phone varchar(255) not null,
verification_status varchar(255) default 'not verified'
);
alter table delivery_boy add address_proof varchar(255) not null;
create table customers(
customer_id int auto_increment primary key,
name varchar(255) not null,
email varchar(255) not null unique,
password varchar(255) not null,
phone varchar(255) not null,
gender varchar(255) not null,
address varchar(255) not null,
verification_status varchar(255) default 'not verified'
);
create table truck_timings(
truck_timing_id int auto_increment primary key,
from_time varchar(255) not null,
to_time varchar(255) not null,
date varchar(255) not null,
location varchar(255) not null,
food_truck_id int not null,
foreign key(food_truck_id) references food_truck(food_truck_id)
);
create table categories(
category_id int auto_increment primary key,
category_name varchar(255) not null,
food_truck_id int not null,
foreign key(food_truck_id) references food_truck(food_truck_id)
);
create table food_items(
food_item_id int auto_increment primary key,
food_item_name varchar(255) not null,
price          varchar(255) not null,
quantity       int not null,
units          varchar(255) not null,
category_id    int not null,
picture        varchar(255) not null,
status         varchar(255) not null,
description    varchar(255) not null,
foreign key(category_id) references categories(category_id)
);
alter table food_items modify status varchar(255) default 'Available';
create table customer_orders(
customer_order_id int auto_increment primary key,
status varchar(255) not null,
customer_id int not null,
date datetime default current_timestamp,
delivery_boy_id int ,
food_truck_id int not null,
truck_timing_id int not null,
foreign key(delivery_boy_id) references delivery_boy(delivery_boy_id),
foreign key(customer_id) references customers(customer_id),
foreign key(food_truck_id) references food_truck(food_truck_id),
foreign key(truck_timing_id) references truck_timings(truck_timing_id)
);

create table customer_order_items(
customer_order_item_id int auto_increment primary key,
customer_order_id int not null,
food_item_id int not null,
quantity int not null,
foreign key(customer_order_id) references customer_orders(customer_order_id),
foreign key(food_item_id) references food_items(food_item_id)
);

create table review(
review_id int auto_increment primary key,
customer_order_item_id int not null,
review varchar(255) not null,
rating varchar(255) not null,
foreign key(customer_order_item_id) references customer_order_items(customer_order_item_id)
);