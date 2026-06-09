from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "ecommerce"

# Database Setup
def init_db():
    conn = sqlite3.connect("ecommerce.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        product TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect("ecommerce.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM products")
    products = cur.fetchall()
    conn.close()
    return render_template("home.html", products=products)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("ecommerce.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users(username,password,role) VALUES(?,?,?)",
                (username, password, "User")
            )
            conn.commit()
        except:
            pass

        conn.close()
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("ecommerce.db")
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            session["role"] = user[3]
            return redirect("/")

    return render_template("login.html")

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(id)
    session.modified = True

    return redirect("/cart")

@app.route("/cart")
def cart():
    items = []

    if "cart" in session:
        conn = sqlite3.connect("ecommerce.db")
        cur = conn.cursor()

        for pid in session["cart"]:
            cur.execute("SELECT * FROM products WHERE id=?", (pid,))
            product = cur.fetchone()

            if product:
                items.append(product)

        conn.close()

    return render_template("cart.html", items=items)

@app.route("/checkout")
def checkout():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("ecommerce.db")
    cur = conn.cursor()

    if "cart" in session:
        for pid in session["cart"]:
            cur.execute(
                "SELECT name FROM products WHERE id=?",
                (pid,)
            )

            product = cur.fetchone()

            if product:
                cur.execute(
                    "INSERT INTO orders(username,product,status) VALUES(?,?,?)",
                    (session["user"], product[0], "Processing")
                )

    conn.commit()
    conn.close()

    session["cart"] = []

    return "Order Placed Successfully!"

@app.route("/orders")
def orders():

    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("ecommerce.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM orders WHERE username=?",
        (session["user"],)
    )

    data = cur.fetchall()
    conn.close()

    return jsonify(data)

@app.route("/admin")
def admin():

    if session.get("role") != "Admin":
        return "Access Denied"

    conn = sqlite3.connect("ecommerce.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM products")
    products = cur.fetchall()

    conn.close()

    return render_template("admin.html", products=products)

@app.route("/add_product", methods=["POST"])
def add_product():

    if session.get("role") != "Admin":
        return "Access Denied"

    name = request.form["name"]
    price = request.form["price"]

    conn = sqlite3.connect("ecommerce.db")
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO products(name,price) VALUES(?,?)",
        (name, price)
    )

    conn.commit()
    conn.close()

    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True)