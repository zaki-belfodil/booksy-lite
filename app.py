import os
from functools import wraps
from sqlite3 import DatabaseError,IntegrityError
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session,url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)



app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
db = SQL("sqlite:///mydb.db")




@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=['GET','POST'])
def register():
    if request.method == 'POST':
        if not request.form.get("email"):
            return render_template("register.html",error="You must enter a email address.")
        elif not request.form.get("password"):
            return render_template("register.html",error="You must enter a password.")
        elif not request.form.get("confirm"):
            return render_template("register.html",error="You must enter a confirm.")
        if request.form.get("password") != request.form.get("confirm"):
            return render_template("register.html",error="The passwords do not match.")
        
        email = request.form.get("email")
        hash = generate_password_hash(request.form.get("password"))
        username = request.form.get("username")
        
        try:
            db.execute("INSERT INTO users (email,hash,username) VALUES(?,?,?)",email,hash,username)
        except ValueError:
            return render_template("register.html",error="This account already exists")
        id = db.execute("SELECT userid FROM users WHERE email = ?",request.form.get("email"))
        session["user_id"] = id[0]["userid"]
        return redirect("/role")
            
    else:
        return render_template("register.html")


@app.route("/role",methods=['GET','POST'])
def role():
    if request.method == "POST":
        session["role"] = []
        choice = request.form.get("account_type")
        if choice == "user":
            db.execute("INSERT INTO customer (id) VALUES (?)", session["user_id"])
            session["role"].append("customer")
            return redirect("/")
        elif choice == "work":
            return redirect("/type")
    else:
        return render_template("role.html")


@app.route("/type",methods=['GET','POST'])
def account_type():
    if request.method == 'POST':
        choice = request.form.get("account_type")
        print(request.form.get("account_type"))
        if choice == "owner":
            return redirect("/set_owner")
        elif choice == "provider":
            db.execute("INSERT INTO provider (id) VALUES (?)", session["user_id"])
            session["role"].append("provider")
            return redirect("/pr_time")
    else:
        return render_template("type_of_work.html")

@app.route("/pr_time",methods=['GET','POST'])
def pr_time():
    if request.method == "POST":
        if not request.form.get("start_time") or not request.form.get("end_time"):
            return render_template("provider_time.html", error="Set working hours")
        start = request.form.get("start_time")
        hour, minute = start.split(":")
        start_of_work_per_min = int(hour) * 60 + int(minute)
        end = request.form.get("end_time")
        hour, minute = end.split(":")
        end_of_work_per_min = int(hour) * 60 + int(minute)
        db.execute("UPDATE provider SET start_of_work_per_min = ?, end_of_work_per_min = ? WHERE id = ? ",start_of_work_per_min,end_of_work_per_min,session["user_id"])
        return redirect("/")
    else:
        return render_template("provider_time.html")

    
@app.route("/set_owner",methods=['GET','POST']) 
def owner():
    if request.method == "POST":
        if not request.form.get("business_name"):
            return render_template("create.html",error="set business name")
        if not request.form.get("start_time") or not request.form.get("end_time"):
            return render_template("create.html", error="Set working hours")
        start = request.form.get("start_time")
        hour, minute = start.split(":")
        start_of_work_per_min = int(hour) * 60 + int(minute)
        end = request.form.get("end_time")
        hour, minute = end.split(":")
        end_of_work_per_min = int(hour) * 60 + int(minute)
        db.execute("INSERT INTO business (name,owner_id) VALUES (?,?)",request.form.get("business_name"),session["user_id"])
        business_id = db.execute("SELECT id FROM business WHERE owner_id = ?",session["user_id"])
        db.execute("INSERT INTO owners (id) VALUES (?)", session["user_id"])
        db.execute("INSERT INTO provider (id,business_id,start_of_work_per_min,end_of_work_per_min) VALUES (?,?,?,?)", session["user_id"],business_id[0]["id"],start_of_work_per_min,end_of_work_per_min)
        return redirect("/service")
        
    else:
        return render_template("create.html")


@app.route("/service",methods=['GET','POST'])
def service():
    if request.method == "POST":
        if not request.form.get("service_name") or not request.form.get("time"):
            return render_template("service.html",error="Please fill in the information.")
        business_id = db.execute("SELECT id FROM business WHERE owner_id = ? ",session["user_id"])
        id = business_id[0]["id"]
        session["business_id"] = id
        db.execute("INSERT INTO service (name,duration_min,business_id) VALUES (?,?,?)",request.form.get("service_name"),request.form.get("time"),id)
        service_id = db.execute("""
        SELECT id FROM service
        WHERE business_id = ?
        ORDER BY id DESC
        LIMIT 1
        """, id)[0]["id"]
        db.execute("""
        INSERT INTO service_providing(service_id, provider_id)
        VALUES (?,?)
        """,
        service_id,
        session["user_id"]
        )
        session["role"] = ["owner", "provider"]
        return redirect("/")
    else:
        return render_template("service.html")


@app.route("/available_services",methods=['GET','POST'])
def services():
    if request.method == "POST":
        return redirect("/edit")
    else:
        services = db.execute("SELECT * FROM service WHERE business_id = ?",session["business_id"])
        return render_template("available_services.html",services=services)

@app.route("/edit",methods=['GET','POST'])
def edit():
    if request.method == "POST":
        db.execute("UPDATE service SET name = ? ,duration_min = ? WHERE business_id = ?",request.form.get("service_name"),request.form.get("time"),session["business_id"])
        return redirect("/")
    else:
        return render_template("edit_service.html")


@app.context_processor
def roles():
    return {
        "roles": session.get("role", [])
    }

@app.route("/b_appointments",methods=['GET','POST'])
def b_appointments():
    if request.method == "POST":
        pass
    elif request.method == "GET":
        appointments = db.execute("""
            SELECT appointment.id ,users.username,provider_user.username as provider,service.name,appointment.date,appointment.start_time,appointment.status,hour,min
            FROM appointment
            JOIN users ON appointment.customer_id = users.userid
            JOIN service ON appointment.service_id = service.id
            JOIN provider ON appointment.provider_id = provider.id
            JOIN users AS provider_user ON provider.id = provider_user.userid
            JOIN business ON provider.business_id  = business.id
            WHERE business.owner_id = ?
        """,session["user_id"])
 
        return render_template("b_appointments.html",appointments=appointments)

@app.route("/businesses",methods=['GET','POST'])
def appointment():
    if request.method == 'POST':
        if not request.form.get("business_id"):
            return render_template("create.html",error="set business name")
        business_id= request.form.get("business_id")
        return redirect(f"/business_appointments?business_id={business_id}")
    else:
        businesses = db.execute("""SELECT name,username,id FROM business 
                                JOIN users ON business.owner_id = users.userid
                                    WHERE business.name= ?
                                """,request.args.get("business_name"))
        if not businesses:
            return render_template("not_found.html"),404
        return render_template("businesses.html",businesses=businesses)

@app.route("/business_appointments",methods=['GET','POST'])
def business_appointments():
    if request.method == "POST":
        service_id = request.form.get("service_id")
        return redirect(f"/book?service_id={service_id}")
    else:
        services = db.execute("""
            SELECT service.name, service.duration_min,service.id FROM service 
            JOIN business ON service.business_id = business.id
            WHERE business.id = ?
            """, request.args.get("business_id"))
        return render_template("appointment.html",services=services)

@app.route("/book",methods=['GET','POST'])
def book():
    if request.method == "POST":
        services = db.execute("SELECT * FROM service WHERE id = ?",request.form.get("service_id"))
        service = services[0]
        if not request.form.get("date"):
            return render_template("book.html",error="Enter a date",service=service)
        duration_min = service["duration_min"]
        date = request.form.get("date")

        return redirect(f"/provider?date={date}&service_id={request.form.get("service_id")}")
    else:
        services = db.execute("SELECT * FROM service WHERE id = ?",request.args.get("service_id"))
        service = services[0]
        return render_template("book.html",service=service)
    
@app.route("/provider",methods=['GET','POST'])
def choose_privider():
    if request.method == 'POST':
        service_id = request.form.get("service_id")
        date = request.form.get("date")
        provider_id = request.form.get("provider_id")


        return redirect(f"/date?date={date}&service_id={service_id}&provider_id={provider_id}")
    else:
        date = request.args.get("date")
        service_id = request.args.get("service_id")
        services = db.execute("SELECT * FROM service WHERE id = ?",request.args.get("service_id"))[0]
        business = services["business_id"]
        providers = db.execute("""
            SELECT users.username, provider.id 
            FROM service_providing
            JOIN provider ON service_providing.provider_id = provider.id
            JOIN users ON provider.id = users.userid
            WHERE service_providing.service_id = ?
        """, service_id)
        return render_template("provider.html",providers=providers,business=business,date=date,services=services)
 


@app.route("/date",methods=['GET',"POST"])
def date():
    if request.method == 'POST':
        service_id = request.form.get("service_id")
        date = request.form.get("date")
        provider_id = request.form.get("provider_id")
        time = request.form.get("time")
        customer_id = session["user_id"]
        service = db.execute("SELECT duration_min FROM service WHERE id = ?",service_id)[0]
        hour, minute = map(int, time.split(":"))
        start_time = hour * 60 + minute
        end_time = start_time + service["duration_min"]
        time = start_time
        hour = int(time // 60)
        minn = int(time % 60)
        db.execute("""INSERT INTO appointment
        (customer_id, service_id, provider_id, date, status, start_time, end_time,hour,min)
        VALUES (?, ?, ?, ?, ?, ?, ?,?,?)
            """,customer_id,service_id,provider_id,date,"booked",start_time,end_time,hour,minn)
        return redirect("/")
    else:
        date = request.args.get("date")
        services = db.execute("SELECT * FROM service WHERE id = ?",request.args.get("service_id"))
        service = services[0]
        provider_id = request.args.get("provider_id")
        providers = db.execute("""
            SELECT username,start_of_work_per_min,end_of_work_per_min ,provider.id
            FROM users
            JOIN provider ON users.userid = provider.id
            WHERE provider.id = ?
        """, provider_id)
        provider = providers[0]
        start = provider["start_of_work_per_min"]
        end = provider["end_of_work_per_min"]
        duration = service["duration_min"]
        times = []
        appointments = db.execute("SELECT start_time,end_time FROM appointment WHERE provider_id = ? AND date = ?",provider["id"],date)
        while(start+duration <= end):
            slot = {
                "time": f"{start//60:02d}:{start%60:02d}",
                "available": True
            }
            appointment_end = start + duration
            for appointment in appointments:
                if start < appointment["end_time"] and appointment_end > appointment["start_time"]:
                    slot["available"] = False
                    break
            times.append(slot)
            start += duration
        
        return render_template("date.html",date=date,service=service,provider=provider,times=times)
@app.route("/user_app")
def user_app():
        appointments = db.execute("""
            SELECT appointment.id,provider_user.username as provider,service.name,appointment.date,appointment.start_time,hour,min
            FROM appointment
            JOIN users ON appointment.customer_id = users.userid
            JOIN service ON appointment.service_id = service.id
            JOIN provider ON appointment.provider_id = provider.id
            JOIN users AS provider_user ON provider.id = provider_user.userid
            WHERE users.userid = ?
        """,session["user_id"])
        return render_template("user_appointments.html",appointments=appointments)

@app.route("/add",methods=['GET','POST'])
def add():
    if request.method == "POST":
        service_id = request.form.get("service_id")
        db.execute("""
        INSERT INTO service_providing(service_id, provider_id)
        VALUES (?,?)
        """,
        service_id,
        session["user_id"]
        )
        return redirect("/")
    else:
        business_id = db.execute("SELECT business_id FROM provider WHERE id = ?",session["user_id"])
        services = db.execute("SELECT name,id FROM service WHERE business_id = ?",business_id[0]["business_id"])
        return render_template("add.html",services=services)
    
@app.route("/show_providers",methods=['GET','POST'])
def show_the_providers():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            return redirect("/add_providers")
        if action == "delete":
            provider_id = request.form.get("provider_id")

            db.execute("DELETE FROM service_providing WHERE provider_id = ?", provider_id)
            db.execute("DELETE FROM appointment WHERE provider_id = ?", provider_id)
            db.execute("DELETE FROM provider WHERE id = ?", provider_id)
            return render_template("show_p.html")
    else:
        providers = db.execute("""SELECT provider.is_owner,users.username,provider.id FROM users
        JOIN provider ON provider.id = users.userid
        WHERE provider.business_id = ?
        """,session["business_id"])
        business_ownerid = db.execute("SELECT owner_id FROM business WHERE id = ?",session["business_id"])[0]
        for provider in providers:
            if provider["id"] == business_ownerid["owner_id"]:

                db.execute("UPDATE provider SET is_owner = ? WHERE id = ?",1,provider["id"])
                break

        return render_template("show_p.html",providers=providers)

@app.route("/add_providers",methods=['GET','POST'])
def add_providers():
    if request.method == "POST":
        if not request.form.get("provider_id"):
            return render_template("add_p.html",error="Enter a provider_id")
        
        provider = db.execute("""SELECT users.username , provider.id FROM users
        JOIN provider ON provider.id = users.userid
        WHERE provider.id = ?
        """,request.form.get("provider_id"))
        if provider == []:
            return render_template("add_p.html",error="not found")
        else:
            provider_id = provider[0]["id"]
            db.execute("UPDATE provider SET business_id = ? WHERE id = ?",session["business_id"],provider_id)
            services = db.execute("SELECT id FROM service WHERE business_id = ?", session["business_id"])
            for s in services:
                db.execute("INSERT OR IGNORE INTO service_providing (service_id, provider_id) VALUES (?, ?)", s["id"], provider_id)
        return redirect("/")
        
    else:
        return render_template("add_p.html")
    



@app.route("/login",methods=['GET','POST'])
def login():
    session.clear()
    if request.method == 'POST':
        if not request.form.get("email"):
            return render_template("login.html",error="You must enter a email address.")
        elif not request.form.get("password"):
            return render_template("login.html",error="You must enter your password.")
        
    else:
        return render_template("login.html")
    rows = db.execute("SELECT * FROM users WHERE email= ? ",request.form.get("email"))
    if len(rows) != 1 or not check_password_hash(rows[0]["hash"],request.form.get("password")):
        return render_template("login.html",error="invalid username and/or password")
    session["user_id"] = rows[0]["userid"]
    roles = []
    if db.execute("SELECT id FROM owners WHERE id = ?", session["user_id"]):
        roles.append("owner")

    if db.execute("SELECT id FROM provider WHERE id = ?", session["user_id"]):
        roles.append("provider")

    if db.execute("SELECT id FROM customer WHERE id = ?", session["user_id"]):
        roles.append("customer")
    
    if "owner" in roles:
        business_id = db.execute("SELECT id FROM business WHERE owner_id = ? ",session["user_id"])
        id = business_id[0]["id"]
        session["business_id"] = id
        
    session["role"] = roles
    return redirect("/")
    

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)