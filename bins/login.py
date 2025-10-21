from flask import Blueprint, request, render_template, redirect, session, flash
import base64
from connection.sql import main

auth_bp = Blueprint("auth", __name__)
conn = main()

web_title = "台股ETF推薦管理平台"
web_footer = web_title + " © 2025 OCU專題"
navbar_before_login = [
    {"name": "登入", "url": "/"},
    {"name": "註冊", "url": "/register"},
]

def is_logged_in():
    return 'user' in session and 'name' in session

# 登入頁
@auth_bp.route("/", methods=["GET"])
def index():
    if is_logged_in():
        return redirect("/home")
    return render_template("login.html", title=web_title, navbar=navbar_before_login, footer=web_footer)

# 登入處理
@auth_bp.route("/login", methods=["POST"])
def do_login():
    username = request.form.get("username")
    password = request.form.get("password")

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

    password = base64.b64encode(password.encode()).decode() if password else None
    if user and user[6] == username and user[7] == password:
        session['user'] = user[6]
        session['name'] = user[1]
        return redirect("/home")
    else:
        flash("帳號或密碼錯誤！", "error")
        return redirect('/')

# 註冊頁
@auth_bp.route("/register", methods=["GET"])
def register():
    if is_logged_in():
        return redirect("/home")
    return render_template("register.html", title=web_title, navbar=navbar_before_login, footer=web_footer)

# 註冊處理
@auth_bp.route("/register", methods=["POST"])
def do_register():
    username = request.form.get("username")
    password = request.form.get("password")
    idcard = request.form.get("idcard")
    name = request.form.get("name")
    email = request.form.get("email")
    birthday = request.form.get("birthday")
    tel = request.form.get("tel")

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()

    if existing_user:
        flash("使用者名稱已存在！", "error")
        return redirect("/register")

    password = base64.b64encode(password.encode()).decode() if password else None
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO users (username, password, idcard, name, email, birthday, tel)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, (username, password, idcard, name, email, birthday, tel))
        conn.commit()

    flash("註冊成功！請登入。", "success")
    return redirect("/")

# 登出
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")
