from flask import Flask, request, jsonify, render_template, redirect, session, flash
import base64

# === mysql連線 ===
from connection.sql import main
conn = main()


# === Flask應用程式初始化 ===
app = Flask(__name__) 
app.secret_key = "etf_taiwan_2025_unversity_ocu_project"

# === 網站標題 ===
web_title = "台股ETF推薦管理平台"
# === 網站footer 標題 ===
web_footer = web_title+" © 2025 OCU專題"

# === navbar選單 登入前 ===
navbar_before_login = [
    {"name": "登入", "url": "/"},
    {"name": "註冊", "url": "/register"},
]

# === navbar選單 登入後 ===
navbar_after_login = [
    {"name": "首頁", "url": "/home"},
    {"name": "登出", "url": "/logout"},
    {"name": "會員個資", "url": "/profile"},
]

# === session管理 ===
def is_logged_in():
    return 'user' in session and 'name' in session 

# === 登入首頁 ===
@app.route("/", methods=["GET"])
def login():
    # 檢查使用者是否已經登入
    islogged_in = is_logged_in()
    if islogged_in:
        return redirect("/home")
    
    return render_template("login.html", title=web_title, navbar=navbar_before_login, footer=web_footer)

# === 登入處理 ===
@app.route("/login", methods=["POST"])
def do_login():
    username = request.form.get("username")
    password = request.form.get("password")
    
    # 從資料庫驗證使用者
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

    password = base64.b64encode(password.encode()).decode() if password else None
    if user and user[6] == username and user[7] == password:
        session['user'] = user[6]  # 使用者名稱
        session['name'] = user[1]  # 使用者姓名
        return redirect("/home")
    else:
        if not user:
            # 使用Flask的flash功能來顯示錯誤訊息
            flash("帳號錯誤~請重新輸入!","error")
            return redirect('/')
        elif user[2] != password:
            # 使用Flask的flash功能來顯示錯誤訊息
            flash("密碼錯誤~請重新輸入!","error")
            return redirect('/')
        else:
            # 使用Flask的flash功能來顯示錯誤訊息
            flash("登入失敗~請稍後再試!","error")
            return redirect('/')

# === 登出 ===
@app.route("/logout", methods=["GET"])
def logout():
    session['user'] = None
    session['name'] = None
    session.clear()
    return redirect("/")


# === 登入後首頁 ===
@app.route("/home", methods=["GET"])
def home():
    # 檢查使用者是否已經登入
    islogged_in = is_logged_in()
    if not islogged_in:
        return redirect("/")
    
    return render_template("home.html", title=web_title, navbar=navbar_after_login, footer=web_footer)


# === 會員個資頁面 ===
@app.route("/profile", methods=["GET"])
def profile():
    # 檢查使用者是否已經登入
    islogged_in = is_logged_in()
    if not islogged_in:
        return redirect("/")
    
    # 取得使用者資料
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (session['user'],))
        user = cursor.fetchone()

    if user:
        return render_template("userprofile.html", title=web_title, navbar=navbar_after_login, footer=web_footer, user=user)
    else:
        flash("無法找到使用者資料！", "error")
        return redirect("/home")

# === 會員個資編輯頁面 ===
@app.route("/profileEdit", methods=["GET"])
def profileEdit():
    # 檢查使用者是否已經登入
    islogged_in = is_logged_in()
    if not islogged_in:
        return redirect("/")
    
    # 取得使用者資料
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (session['user'],))
        user = cursor.fetchone()

    if user:
        return render_template("userprofileEdit.html", title=web_title, navbar=navbar_after_login, footer=web_footer, user=user)
    else:
        flash("無法找到使用者資料！", "error")
        return redirect("/home")

# === 會員個資編輯處理 ===
@app.route("/profileEdit", methods=["POST"])
def profileEditPost():
    # 檢查使用者是否已經登入
    islogged_in = is_logged_in()
    if not islogged_in:
        return redirect("/")

    # 取得表單資料
    idcard = request.form.get("idcard")
    name = request.form.get("name")
    email = request.form.get("email")
    birthday = request.form.get("birthday")
    tel = request.form.get("tel")

    # 更新使用者資料
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE users 
            SET idcard = %s, name= %s, email = %s, birthday = %s, tel = %s 
            WHERE username = %s
        """, (idcard, name, email, birthday, tel, session['user']))
        conn.commit()

    flash("個資更新成功！", "success")
    return redirect("/profile")

# ======
app.run(debug=True)
