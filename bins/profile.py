from flask import Blueprint, render_template, redirect, session, flash, request
from connection.sql import main

profile_bp = Blueprint("profile", __name__)
conn = main()

web_title = "台股ETF推薦管理平台"
navbar_after_login = [
    {"name": "首頁", "url": "/home"},
    {"name": "股票管理", "url": "/stocks"},
    {"name": "會員個資", "url": "/profile"},
    {"name": "登出", "url": "/logout"},
]
web_footer = web_title + " © 2025 OCU專題"

def is_logged_in():
    return 'user' in session and 'name' in session

@profile_bp.route("/profile")
def profile():
    if not is_logged_in():
        return redirect("/")
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (session['user'],))
        user = cursor.fetchone()
    return render_template("userprofile.html", title=web_title, navbar=navbar_after_login, footer=web_footer, user=user)

@profile_bp.route("/profileEdit", methods=["GET"])
def profileEdit():
    if not is_logged_in():
        return redirect("/")
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE username = %s", (session['user'],))
        user = cursor.fetchone()
    return render_template("userprofileEdit.html", title=web_title, navbar=navbar_after_login, footer=web_footer, user=user)

@profile_bp.route("/profileEdit", methods=["POST"])
def profileEditPost():
    if not is_logged_in():
        return redirect("/")
    idcard = request.form.get("idcard")
    name = request.form.get("name")
    email = request.form.get("email")
    birthday = request.form.get("birthday")
    tel = request.form.get("tel")
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE users 
            SET idcard=%s, name=%s, email=%s, birthday=%s, tel=%s
            WHERE username=%s
        """, (idcard, name, email, birthday, tel, session['user']))
        conn.commit()
    flash("個資更新成功！", "success")
    return redirect("/profile")
