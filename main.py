import datetime

from flask import Flask, request, render_template, session, redirect
import os
import pymysql
import random
from Mail import send_email
from pyasn1_modules.rfc2459 import id_ce_subjectAltName

app = Flask(__name__)
app.secret_key = "lucky"
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = APP_ROOT + "/static/"
conn = pymysql.connect(host="localhost", user="root", password="Keerthi123", db="food_truck")
cursor = conn.cursor()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/food_truck_registration")
def food_truck_registration():
    return render_template("food_truck_registration.html")


@app.route("/food_truck_registration_action", methods=['post'])
def food_truck_registration_action():
    food_truck_title = request.form.get("food_truck_title")
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    count = cursor.execute("select * from food_truck where email='" + str(email) + "'")
    if count > 0:
        return render_template("msg.html", message="duplicate email address")
    count = cursor.execute("select * from food_truck where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("msg.html", message="duplicate phone number")
    try:
        cursor.execute("insert into food_truck(food_truck_title,name,email,password,phone)values('"+str(food_truck_title)+"','"+str(name)+"','"+str(email)+"','"+str(password)+"','"+str(phone)+"')")
        conn.commit()
        food_truck_id = cursor.lastrowid
        otp = random.randrange(1000, 100000)
        subject = "Food truck email verification"
        message = "use this OTP "+str(otp)+" to verify your account"
        send_email(subject, message, email)
        return render_template("food_truck_verification.html", food_truck_id=food_truck_id, otp=otp)
    except Exception as e:
        print(e)
        return render_template("msg.html", message="something went wrong")


@app.route("/food_truck_verification", methods=['post'])
def food_truck_verification():
    food_truck_id = request.form.get("food_truck_id")
    cursor.execute("update food_truck set verification_status='verified' where food_truck_id='"+str(food_truck_id)+"'")
    conn.commit()
    return render_template("msg.html", message="food registered successfully")


@app.route("/food_truck_login")
def food_truck_login():
    return render_template("food_truck_login.html")


@app.route("/food_truck_login_action", methods=['post'])
def food_truck_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from food_truck where email='"+str(email)+"'and password='"+str(password)+"'")
    if count > 0:
        trucks = cursor.fetchall()
        session['food_truck_id'] = trucks[0][0]
        session['role'] = 'food_truck'
        return redirect("/food_truck_home")
    else:
        return render_template("notification.html", notification="Invalid login Details")


@app.route("/food_truck_home")
def food_truck_home():
    food_truck_id = session['food_truck_id']
    cursor.execute("select * from food_truck where food_truck_id='"+str(food_truck_id)+"'")
    trucks = cursor.fetchall()
    return render_template("food_truck_home.html", truck=trucks[0])


@app.route("/add_truck_timings")
def add_truck_timings():
    cursor.execute("select * from food_truck")
    trucks = cursor.fetchall()
    return render_template("add_truck_timings.html", trucks=trucks)


@app.route("/add_truck_timings_action", methods=['post'])
def add_truck_timings_action():
    from_time = request.form.get("from_time")
    to_time = request.form.get("to_time")
    date = request.form.get("date")
    location = request.form.get("location")
    food_truck_id = session['food_truck_id']
    from_time = date+" "+from_time
    to_time = date+" "+to_time
    count = cursor.execute("select * from truck_timings where food_truck_id='"+str(food_truck_id)+"' and ('"+str(from_time)+"'>=from_time and '"+str(from_time)+"'<=to_time and '"+str(to_time)+"'>=from_time and '"+str(to_time)+"'>=to_time)or('"+str(from_time)+"'<=from_time and '"+str(from_time)+"'<=to_time and '"+str(to_time)+"'>=from_time and '"+str(to_time)+"'<=to_time)or('"+str(from_time)+"'<=from_time and '"+str(from_time)+"'<=to_time and '"+str(to_time)+"'>=from_time and '"+str(to_time)+"'>=to_time)or('"+str(from_time)+"'>=from_time and '"+str(from_time)+"'<=to_time and '"+str(to_time)+"'>=from_time and '"+str(to_time)+"'<=to_time)")
    if count > 0:
        return {"message": "Time Collision"}
    else:
        cursor.execute("insert into truck_timings(from_time,to_time,date,location,food_truck_id)values('"+str(from_time)+"','"+str(to_time)+"','"+str(date)+"','"+str(location)+"','"+str(food_truck_id)+"')")
        conn.commit()
        return {"message": "Timings Added Successfully"}


@app.route("/get_timings")
def get_timings():
    food_truck_id = session['food_truck_id']
    date = request.args.get("date")
    cursor.execute("select * from truck_timings where food_truck_id='"+str(food_truck_id)+"'and date='"+str(date)+"'")
    timings = cursor.fetchall()
    return render_template("view_truck_timings.html", timings=timings)


@app.route("/add_categories")
def add_categories():
    cursor.execute("select * from food_truck")
    trucks = cursor.fetchall()
    return render_template("add_categories.html", trucks=trucks)


@app.route("/add_categories_action", methods=['post'])
def add_categories_action():
    category_name = request.form.get("category_name")
    food_truck_id = session['food_truck_id']
    count =cursor.execute("select * from categories where category_name='"+str(category_name)+"'")
    if count > 0:
        return {"message": "Duplicate category name "}
    else:
        cursor.execute("insert into categories(category_name,food_truck_id)values('"+str(category_name)+"','"+str(food_truck_id)+"')")
        conn.commit()
        return {"message": "Category added successfully"}


@app.route("/get_categories")
def get_categories():
    food_truck_id = session['food_truck_id']
    cursor.execute("select * from categories where food_truck_id='" + str(food_truck_id) + "'")
    categories = cursor.fetchall()
    return render_template("view_categories.html", categories=categories)


@app.route("/add_food_items")
def add_food_items():
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    return render_template("add_food_items.html", categories=categories)


@app.route("/add_food_items_action", methods=['post'])
def add_food_items_action():
    food_item_name = request.form.get("food_item_name")
    price = request.form.get("price")
    quantity = request.form.get("quantity")
    units = request.form.get("units")
    category_id = request.form.get("category_id")
    picture = request.files.get("picture")
    description = request.form.get("description")
    count = cursor.execute("select * from food_items where food_item_name='"+str(food_item_name)+"'")
    if count > 0:
        return render_template("fmsg.html", message="Food Item Name Is Already Exist")
    try:
        path = APP_ROOT +"/food_items/"+ picture.filename
        picture.save(path)
        print(path)
        cursor.execute("insert into food_items (food_item_name,price,quantity,units,category_id,picture,description)values('"+str(food_item_name)+"','"+str(price)+"','"+str(quantity)+"','"+str(units)+"','"+str(category_id)+"','"+str(picture.filename)+"','"+str(description)+"')")
        conn.commit()
        return render_template("fmsg.html", message="Food Item Added Successfully")
    except Exception as e:
        return render_template("fmsg.html", message="invalid Food Item Name")


@app.route("/search_by_food")
def search_by_food():
    return render_template("search_by_food.html")


@app.route("/get_food", methods=['get'])
def get_food():
    keyword = request.args.get("keyword")
    cursor.execute("select * from food_items where food_item_name like '%"+str(keyword)+"%' or category_id in(select category_id from categories where category_name like '%"+str(keyword)+"%')")
    food_items = cursor.fetchall()
    print(food_items)
    return render_template("view_food_items.html", food_items=food_items, get_categories_by_category_id=get_categories_by_category_id,get_food_truck_id_by_category_id=get_food_truck_id_by_category_id, get_food_trucks_by_food_truck_id=get_food_trucks_by_food_truck_id, get_truck_timings_by_food_truck_id=get_truck_timings_by_food_truck_id,get_rating_by_customer_order_item_id=get_rating_by_customer_order_item_id,get_customer_by_review_id=get_customer_by_review_id)


@app.route("/search_by_truck")
def search_by_truck():
    cursor.execute("select * from categories")
    categories = cursor.fetchall()
    cursor.execute("select * from food_truck")
    food_trucks = cursor.fetchall()
    return render_template("search_by_truck.html", categories=categories, food_trucks=food_trucks)


@app.route("/get_food_by_truck_category_food_name", methods=['get'])
def get_food_by_truck_category_food_name():
    category_id = request.args.get("category_id")
    food_item_name = request.args.get("food_item_name")
    cursor.execute("select * from food_items where food_item_name like '%"+str(food_item_name)+"%' and category_id ='"+str(category_id)+"' ")
    food_items = cursor.fetchall()
    return render_template("view_food_items.html", food_items=food_items, get_categories_by_category_id=get_categories_by_category_id,get_food_truck_id_by_category_id=get_food_truck_id_by_category_id, get_food_trucks_by_food_truck_id=get_food_trucks_by_food_truck_id, get_truck_timings_by_food_truck_id=get_truck_timings_by_food_truck_id,get_rating_by_customer_order_item_id=get_rating_by_customer_order_item_id,get_customer_by_review_id=get_customer_by_review_id)


@app.route("/get_categories_by_food_truck_id")
def get_categories_by_food_truck_id():
    food_truck_id = request.args.get("food_truck_id")
    cursor.execute("select * from categories where food_truck_id='"+str(food_truck_id)+"'")
    categories = cursor.fetchall()
    return render_template("get_categories_by_food_truck_id.html", categories=categories)


@app.route("/get_food_by_location")
def get_food_by_location():
    cursor.execute("select Distinct(location) from truck_timings where from_time>now()")
    locations = cursor.fetchall()
    return render_template("get_food_by_location_datetime_food_name_category.html", locations=locations)


@app.route("/get_food_by_location_datetime_food_name_category")
def get_food_by_location_datetime_food_name_category():
    food_item_name = request.args.get("food_item_name")
    location = request.args.get("location")
    from_time = request.args.get("from_time")
    if location is None and from_time is None:
        query = "select * from food_items where food_item_name like '%"+str(food_item_name)+"%'  or category_id in(select category_id from categories where category_name like '%"+str(food_item_name)+"%') "
    elif location is None and from_time is not None:
        query = "select * from food_items where food_item_name like '%"+str(food_item_name)+"%'  or category_id in(select category_id from categories where category_name like '%"+str(food_item_name)+"%') and category_id in (select category_id from categories where food_truck_id in(select food_truck_id from food_truck where truck_timings where from_time>='"+str(from_time)+"' )) "
    elif location is not None and from_time is None:
        query = "select * from food_items where food_item_name like '%"+str(food_item_name)+"%'  or category_id in(select category_id from categories where category_name like '%"+str(food_item_name)+"%') and category_id in (select category_id from categories where food_truck_id in(select food_truck_id from food_truck where truck_timings where location=='"+str(location)+"' )) "
    elif location is not None and from_time is not None:
        query = "select * from food_items where food_item_name like '%"+str(food_item_name)+"%'  or category_id in(select category_id from categories where category_name like '%"+str(food_item_name)+"%') and category_id in (select category_id from categories where food_truck_id in(select food_truck_id from food_truck where truck_timings where location=='"+str(location)+"' and from_time>='"+str(from_time)+"')) "
    cursor.execute(query)
    food_items = cursor.fetchall()
    return render_template("view_food_items.html", food_items=food_items, get_categories_by_category_id=get_categories_by_category_id,get_food_truck_id_by_category_id=get_food_truck_id_by_category_id,get_food_trucks_by_food_truck_id=get_food_trucks_by_food_truck_id,get_truck_timings_by_food_truck_id=get_truck_timings_by_food_truck_id,get_rating_by_customer_order_item_id=get_rating_by_customer_order_item_id,get_customer_by_review_id=get_customer_by_review_id)


def get_categories_by_category_id(category_id):
    cursor.execute("select * from categories where category_id='"+str(category_id)+"'")
    categories = cursor.fetchall()
    return categories[0]


def get_food_truck_id_by_category_id(category_id):
    cursor.execute("select * from categories where category_id='"+str(category_id)+"'")
    categories = cursor.fetchall()
    return categories[0]


def get_food_trucks_by_food_truck_id(food_truck_id):
    cursor.execute("select * from food_truck where food_truck_id='"+str(food_truck_id)+"'")
    food_trucks = cursor.fetchall()
    return food_trucks[0]


def get_truck_timings_by_food_truck_id(food_truck_id):
    cursor.execute("select * from truck_timings where food_truck_id='"+str(food_truck_id)+"' and to_time>now()")
    truck_timings = cursor.fetchall()
    return truck_timings


@app.route("/delivery_boy_registration")
def delivery_boy_registration():
    return render_template("delivery_boy_registration.html")


@app.route("/delivery_boy_registration_action", methods=['post'])
def delivery_boy_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    address_proof = request.files.get("address_proof")
    count = cursor.execute("select * from delivery_boy where email='" + str(email) + "'")
    if count > 0:
        return render_template("msg.html", message="duplicate email address")
    count = cursor.execute("select * from delivery_boy where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("msg.html", message="duplicate phone number")
    try:
        path = APP_ROOT + "/delivery_boy/" + address_proof.filename
        address_proof.save(path)
        cursor.execute("insert into delivery_boy(name,email,password,phone,address_proof)values('" + str(name) + "','" + str(email) + "','" + str(password) + "','" + str(phone) + "','"+str(address_proof.filename)+"')")
        conn.commit()
        delivery_boy_id = cursor.lastrowid
        otp = random.randrange(1000, 100000)
        subject = "Delivery Boy email verification"
        message = "use this OTP " + str(otp) + " to verify your account"
        send_email(subject, message, email)
        return render_template("deliveryboy_verification.html", delivery_boy_id=delivery_boy_id, otp=otp)
    except Exception as e:
        print(e)
        return render_template("msg.html", message="something went wrong")


@app.route("/deliveryboy_verification", methods=['post'])
def deliveryboy_verification():
    delivery_boy_id = request.form.get("delivery_boy_id")
    cursor.execute("update delivery_boy set verification_status='verified' where delivery_boy_id='"+str(delivery_boy_id)+"'")
    conn.commit()
    return render_template("msg.html", message="Delivery Boy registered successfully")


@app.route("/delivery_boy_login")
def delivery_boy_login():
    return render_template("delivery_boy_login.html")


@app.route("/delivery_boy_login_action", methods=['post'])
def delivery_boy_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from delivery_boy where email='"+str(email)+"'and password='"+str(password)+"'")
    if count > 0:
        deliveryboy = cursor.fetchall()
        session['delivery_boy_id'] = deliveryboy[0][0]
        session['role'] = 'delivery_boy'
        return redirect("/delivery_boy_home")
    else:
        return render_template("notification.html", notification="Invalid login Details")


@app.route("/delivery_boy_home")
def delivery_boy_home():
    delivery_boy_id = session['delivery_boy_id']
    cursor.execute("select * from delivery_boy where  delivery_boy_id ='"+str(delivery_boy_id)+"'")
    deliveryboy = cursor.fetchall()
    return render_template("delivery_boy_home.html", deliveryboy=deliveryboy[0])


@app.route("/customer_registration")
def customer_registration():
    return render_template("customer_registration.html")


@app.route("/customer_registration_action", methods=['post'])
def customer_registration_action():
    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    gender = request.form.get("gender")
    address = request.form.get("address")
    count = cursor.execute("select * from customers where email='" + str(email) + "'")
    if count > 0:
        return render_template("msg.html", message="Duplicate email address")
    count = cursor.execute("select * from customers where phone='" + str(phone) + "'")
    if count > 0:
        return render_template("msg.html", message="Duplicate phone number")
    try:
        cursor.execute("insert into customers(name,email,password,phone,gender,address)values('" + str(name) + "','" + str(email) + "','" + str(password) + "','" + str(phone) + "','" + str(gender) + "','" + str(address) + "')")
        conn.commit()
        customer_id = cursor.lastrowid
        otp = random.randrange(1000, 100000)
        subject = "customer email verification"
        message = "use this OTP " + str(otp) + " to verify your account"
        send_email(subject, message, email)
        return render_template("customer_verification.html", customer_id=customer_id, otp=otp)
    except Exception as e:
        return render_template("msg.html", message="Invalid login details")


@app.route("/customer_verification", methods=['post'])
def customer_verification():
    customer_id = request.form.get("customer_id")
    cursor.execute("update customers set verification_status='verified' where customer_id='"+str(customer_id)+"'")
    return render_template("msg.html", message="Customer Registered successfully")


@app.route("/customer_login")
def customer_login():
    return render_template("customer_login.html")


@app.route("/customer_login_action", methods=['post'])
def customer_login_action():
    email = request.form.get("email")
    password = request.form.get("password")
    count = cursor.execute("select * from customers where email='" + str(email) + "'and password='" + str(password) + "'")
    if count > 0:
        customers = cursor.fetchall()
        session['customer_id'] = customers[0][0]
        session['role'] = 'customer'
        return redirect("/customer_home")
    else:
        return render_template("notification.html", notification="Invalid login Details")


@app.route("/customer_home")
def customer_home():
    customer_id = session['customer_id']
    cursor.execute("select * from customers where  customer_id ='" + str(customer_id) + "'")
    customers = cursor.fetchall()
    return render_template("customer_home.html", customer=customers[0])


@app.route("/add_to_cart")
def add_to_cart():
    food_item_id = request.args.get("food_item_id")
    quantity = request.args.get("quantity")
    customer_id = session['customer_id']
    cursor.execute("select * from categories where category_id in(select category_id from food_items where food_item_id='"+str(food_item_id)+"')")
    categories = cursor.fetchall()
    food_truck_id = categories[0][2]
    cursor.execute("select * from truck_timings where food_truck_id='"+str(food_truck_id)+"'")
    truck_timings = cursor.fetchall()
    truck_timing_id = truck_timings[0][0]
    count = cursor.execute("select * from customer_orders where customer_id='" + str(customer_id) + "'and food_truck_id='" + str(food_truck_id) + "'and truck_timing_id='" + str(truck_timing_id) + "' and status='cart'")
    if count > 0:
        customer_orders = cursor.fetchall()
        customer_order_id = customer_orders[0][0]
    else:
        cursor.execute("insert into customer_orders(customer_id,food_truck_id,truck_timing_id,status)values('" + str(customer_id) + "','" + str(food_truck_id) + "','" + str(truck_timing_id) + "','cart')")
        conn.commit()
        customer_order_id = cursor.lastrowid
    count = cursor.execute("select * from customer_order_items where food_item_id='"+str(food_item_id)+"' and customer_order_id='"+str(customer_order_id)+"'")
    if count > 0:
        cursor.execute("update customer_order_items set quantity=quantity +'"+str(quantity)+"' where food_item_id='"+(food_item_id)+"' and customer_order_id='"+str(customer_order_id)+"'")
        conn.commit()
        return render_template("cmsg.html", message="food Item Updated successfully")
    else:
        cursor.execute("insert into customer_order_items(food_item_id,customer_order_id,quantity)values('"+str(food_item_id)+"','"+str(customer_order_id)+"','"+str(quantity)+"')")
        conn.commit()
        return render_template("cmsg.html", message="food Item Add to Cart")


@app.route("/view_cart")
def view_cart():
    role = session['role']
    type = request.args.get("type")
    query = ""
    if role == 'customer':
         customer_id = session['customer_id']
         if type == 'cart':
             query = "select * from customer_orders where customer_id='" + str(customer_id) + "' and status='cart'"
         elif type == 'processing':
             query = "select * from customer_orders where customer_id='" + str(customer_id) + "' and (status='ordered' or status='cooking' or status='cooked' or status='accepted for delivery' or status='delivery boy picked up' or status='Hand over to customer')"
         elif type == 'history':
             query = "select * from customer_orders where customer_id='" + str(customer_id) + "' and (status='cancelled' or status='delivered')"
    elif role == 'food_truck':
        food_truck_id = session['food_truck_id']
        if type == 'ordered':
            query = "select * from customer_orders where food_truck_id='" + str(food_truck_id) + "' and status='ordered'"
        elif type == 'processing':
            query = "select * from customer_orders where food_truck_id='" + str(food_truck_id) + "' and (status='cooking' or status='cooked' or status='accepted for delivery' or status='delivery boy picked up' or status='Hand over to customer')"
        elif type == 'history':
            query = "select * from customer_orders where food_truck_id='" + str(food_truck_id) + "' and (status='cancelled' or status='delivered')"
    elif role == 'delivery_boy':
        delivery_boy_id = session['delivery_boy_id']
        if type == 'orders':
            query = "select * from customer_orders where  status='cooked'"
        elif type == 'my_orders':
            query = "select * from customer_orders where delivery_boy_id='"+str(delivery_boy_id)+"' and (status='accepted for delivery' or status='delivery boy picked up' or status='Hand over to customer')"
        elif type == 'history':
            query = "select * from customer_orders where delivery_boy_id='"+str(delivery_boy_id)+"' and status='delivered'"
    cursor.execute(query)
    customer_orders = cursor.fetchall()
    customer_orders = list(customer_orders)
    customer_orders.reverse()
    return render_template("view_cart.html", customer_orders=customer_orders, get_customer_by_customer_id=get_customer_by_customer_id,get_customer_order_items_by_customer_order_id=get_customer_order_items_by_customer_order_id, get_food_trucks_by_food_truck_id=get_food_trucks_by_food_truck_id,get_truck_timings_by_food_truck_id=get_truck_timings_by_food_truck_id, get_food_items_by_food_item_id=get_food_items_by_food_item_id, get_categories_by_category_id=get_categories_by_category_id, int=int, get_delivery_boy_by_delivery_boy_id=get_delivery_boy_by_delivery_boy_id,get_truck_timing_by_truck_timing_id=get_truck_timing_by_truck_timing_id,can_cook_the_order=can_cook_the_order,is_customer_is_not_reviews=is_customer_is_not_reviews)


def get_customer_by_customer_id(customer_id):
    cursor.execute("select * from customers where customer_id='"+str(customer_id)+"'")
    customers = cursor.fetchall()
    return customers[0]


def get_customer_order_items_by_customer_order_id(customer_order_id):
    cursor.execute("select * from customer_order_items where customer_order_id='"+str(customer_order_id)+"'")
    customer_order_items = cursor.fetchall()
    return customer_order_items


def get_food_items_by_food_item_id(food_item_id):
    cursor.execute("select * from food_items where food_item_id='"+str(food_item_id)+"' ")
    food_items = cursor.fetchall()
    return food_items[0]


def get_delivery_boy_by_delivery_boy_id(delivery_boy_id):
    cursor.execute("select * from delivery_boy where delivery_boy_id='"+str(delivery_boy_id)+"'")
    delivery_boys = cursor.fetchall()
    return delivery_boys[0]


def get_truck_timing_by_truck_timing_id(truck_timing_id):
    cursor.execute("select * from truck_timings where truck_timing_id='"+str(truck_timing_id)+"'")
    truck_timings = cursor.fetchall()
    return truck_timings[0]


def can_cook_the_order(truck_timing_id):
    cursor.execute("select * from truck_timings where truck_timing_id='"+str(truck_timing_id)+"'")
    truck_timings = cursor.fetchall()
    from_time = truck_timings[0][1]
    to_time = truck_timings[0][2]
    from_time = datetime.datetime.strptime(from_time, '%Y-%m-%d %H:%M')
    to_time = datetime.datetime.strptime(to_time, '%Y-%m-%d %H:%M')
    today = datetime.datetime.now()
    if today>=from_time and today<=to_time:
        return True
    return False


@app.route("/order_now")
def order_now():
    customer_order_id = request.args.get("customer_order_id")
    totalPrice = request.args.get("totalPrice")
    truck_timing_id = request.args.get("truck_timing_id")
    cursor.execute("select * from customer_order_items where customer_order_id='"+str(customer_order_id)+"'")
    return render_template("order_now.html", customer_order_id=customer_order_id, totalPrice=totalPrice, truck_timing_id=truck_timing_id)


@app.route("/payment", methods=['post'])
def payment():
    customer_order_id = request.form.get("customer_order_id")
    truck_timing_id = request.form.get("truck_timing_id")
    cursor.execute("update customer_orders set status='ordered',truck_timing_id='"+str(truck_timing_id)+"' where customer_order_id='"+str(customer_order_id)+"'")
    conn.commit()
    return render_template("cmsg.html", message="payment successfully")


@app.route("/set_status", methods=['post'])
def set_status():
    customer_order_id = request.form.get("customer_order_id")
    status = request.form.get("status")
    cursor.execute("update customer_orders set status='"+str(status)+"' where customer_order_id='"+str(customer_order_id)+"'")
    conn.commit()
    return render_template("message.html", message="Order " +status+ " successfully ")


@app.route("/set_status2", methods=['post'])
def set_status2():
    customer_order_id = request.form.get("customer_order_id")
    status = request.form.get("status")
    delivery_boy_id = session['delivery_boy_id']
    cursor.execute("update customer_orders set status='"+str(status)+"', delivery_boy_id='"+str(delivery_boy_id)+"' where customer_order_id='"+str(customer_order_id)+"'")
    conn.commit()
    return render_template("message.html", message="order " +status+ " successfully")


@app.route("/remove_from_cart")
def remove_from_cart():
    customer_order_item_id = request.args.get("customer_order_item_id")
    cursor.execute("select * from customer_order_items where customer_order_item_id='"+str(customer_order_item_id)+"'")
    customer_order_items = cursor.fetchall()
    customer_order_id = customer_order_items[0][1]
    cursor.execute("delete from customer_order_items where customer_order_item_id='"+str(customer_order_item_id)+"'")
    conn.commit()
    count = cursor.execute("select * from customer_order_items where customer_order_id='"+str(customer_order_id)+"'")
    if count > 0:
        return redirect("/view_cart?type=cart")
    else:
        cursor.execute("delete from customer_orders where customer_order_id='" + str(customer_order_id) + "'")
        conn.commit()
        return render_template("cmsg.html", message="Item Removed successfully")


@app.route("/give_review")
def give_review():
    customer_order_item_id = request.args.get("customer_order_item_id")
    cursor.execute("select * from customer_order_items where customer_order_item_id='"+str(customer_order_item_id)+"'")
    customer_order_items = cursor.fetchall()
    return render_template("give_review.html", customer_order_items=customer_order_items, customer_order_item_id=customer_order_item_id)


@app.route("/give_review_action")
def give_review_action():
    customer_order_item_id = request.args.get("customer_order_item_id")
    review = request.args.get("review")
    rating = request.args.get("rating")
    cursor.execute("insert into review(customer_order_item_id,review,rating)values('"+str(customer_order_item_id)+"','"+str(review)+"','"+str(rating)+"')")
    conn.commit()
    return render_template("cmsg.html", message="Thank You For Your Review")


def get_rating_by_customer_order_item_id(food_item_id):
    cursor.execute("select avg(rating) from review where customer_order_item_id in(select customer_order_item_id from customer_order_items where food_item_id='"+str(food_item_id)+"')")
    ratings = cursor.fetchall()
    return ratings[0][0]


@app.route("/view_reviews")
def view_reviews():
    food_item_id = request.args.get("food_item_id")
    cursor.execute("select * from review where customer_order_item_id in(select customer_order_item_id from customer_order_items where food_item_id='"+str(food_item_id)+"')")
    reviews = cursor.fetchall()
    return render_template("view_reviews.html", reviews=reviews, get_customer_by_review_id=get_customer_by_review_id,is_customer_is_not_reviews=is_customer_is_not_reviews)


def get_customer_by_review_id(review_id):
    cursor.execute("select * from customers where customer_id in (select customer_id from customer_orders where customer_order_id in(select customer_order_id from customer_order_items where customer_order_item_id in (select customer_order_item_id from review where review_id='"+str(review_id)+"')))")
    customers = cursor.fetchall()
    return customers[0]


def is_customer_is_not_reviews(customer_order_item_id):
    count = cursor.execute("select * from review where customer_order_item_id='"+str(customer_order_item_id)+"'")
    if count == 0:
        return True
    return False


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


app.run(debug=True)
