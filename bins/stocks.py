from flask import Blueprint, render_template, redirect, session, flash, request
from connection.sql import main
import datetime

stock_bp = Blueprint("stock", __name__)
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


# === 股票列表 ===
@stock_bp.route("/stocks")
def stock_list():
    if not is_logged_in():
        return redirect("/")
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM stocks ORDER BY id DESC")
        stocks = cursor.fetchall()
    return render_template(
        "stock.html",
        title=web_title,
        navbar=navbar_after_login,
        footer=web_footer,
        stocks=stocks
    )


# === 股票新增（GET/POST 合併）===
@stock_bp.route("/stockAdd", methods=["GET", "POST"])
def stock_add():
    if not is_logged_in():
        return redirect("/")

    if request.method == "POST":
        # 取得表單資料（支援多筆）
        names = request.form.getlist("Name[]")
        symbols = request.form.getlist("Symbol[]")
        quantities = request.form.getlist("Quantity[]")
        purchase_prices = request.form.getlist("Purchase_price[]")
        current_prices = request.form.getlist("Current_price[]")

        # created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with conn.cursor() as cursor:
            for i in range(len(names)):
                cursor.execute("""
                    INSERT INTO stocks (name, symbol, quantity, purchase_price, current_price)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    names[i],
                    symbols[i],
                    int(quantities[i]),
                    float(purchase_prices[i]),
                    float(current_prices[i])
                ))
            conn.commit()

        flash("股票新增成功！", "success")
        return redirect("/stocks")

    # GET：顯示新增頁面
    return render_template("stockAdd.html", title=web_title, navbar=navbar_after_login, footer=web_footer)


# === 股票編輯（GET/POST 合併）===
@stock_bp.route("/stockEdit/<int:id>", methods=["GET", "POST"])
def stock_edit(id):
    if not is_logged_in():
        return redirect("/")

    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM stocks WHERE id = %s", (id,))
        stock = cursor.fetchone()

    if not stock:
        flash("找不到該股票資料！", "error")
        return redirect("/stocks")

    if request.method == "POST":
        name = request.form.get("Name")
        symbol = request.form.get("Symbol")
        quantity = request.form.get("Quantity")
        purchase_price = request.form.get("Purchase_price")
        current_price = request.form.get("Current_price")

        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE stocks
                SET name=%s, symbol=%s, quantity=%s, purchase_price=%s, current_price=%s
                WHERE id=%s
            """, (name, symbol, quantity, purchase_price, current_price, id))
            conn.commit()

        flash("股票資料已更新！", "success")
        return redirect("/stocks")

    # GET：顯示編輯頁面
    return render_template("stockEdit.html", title=web_title, navbar=navbar_after_login, footer=web_footer, stock=stock)


# === 股票刪除 ===
@stock_bp.route("/stockDelete/<int:id>")
def stock_delete(id):
    if not is_logged_in():
        return redirect("/")

    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM stocks WHERE id = %s", (id,))
        conn.commit()

    flash("股票已刪除！", "success")
    return redirect("/stocks")
