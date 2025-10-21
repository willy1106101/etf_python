from flask import Blueprint, render_template, redirect, session
from connection.sql import main

home_bp = Blueprint("home", __name__)
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

@home_bp.route("/home")
def home():
    # 檢查使用者是否已經登入
    islogged_in = is_logged_in()
    if not islogged_in:
        return redirect("/")
    
    # 1. 查詢隨機三檔股票基本資料
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM etf_tickers ORDER BY rand() LIMIT 3")
        tickers = cursor.fetchall()

    # 2. 查詢這三檔股票的最新價格、前一日價格、開盤價，計算漲跌幅等
    info_stock = []
    with conn.cursor(dictionary=True) as cursor:
        for symbol in tickers:
            ticker_code = symbol[2]
            # 查詢最新兩日的收盤價與開盤價
            cursor.execute("""
                SELECT date, closing_price, open_price
                FROM stock_prices
                WHERE ticker = %s
                ORDER BY date DESC LIMIT 2
            """, (ticker_code,))
            price_rows = cursor.fetchall()

            def safe_val(val, digits=2):
                if val is None:
                    return '-'
                if isinstance(val, str):
                    if val.strip() == '' or val.strip().lower() == 'none':
                        return '-'
                    try:
                        fval = float(val)
                        return f"{fval:.{digits}f}"
                    except Exception:
                        return val
                if isinstance(val, (int, float)):
                    return f"{val:.{digits}f}"
                return '-'

            if not price_rows:
                info_stock.append({
                    'name': symbol[1],
                    'code': ticker_code,
                    'price': '-',
                    'open': '-',
                    'previous_close': '-',
                    'change': '-',
                    'sign': '-',
                    'color': ''
                })
                continue
            latest = price_rows[0]
            previous = price_rows[1] if len(price_rows) > 1 else None
            # 計算漲跌幅
            latest_close = latest['closing_price'] if latest['closing_price'] is not None else None
            previous_close = previous['closing_price'] if previous and previous['closing_price'] is not None else None
            try:
                if previous_close is not None and latest_close is not None:
                    change = float(latest_close) - float(previous_close)
                    percent = (change / float(previous_close)) * 100 if float(previous_close) else 0
                else:
                    change = None
                    percent = None
            except Exception:
                change = None
                percent = None
            # 漲跌符號與顏色
            if percent is None:
                sign, color, percent_str = '-', '', '-'
            elif percent > 0:
                sign, color, percent_str = "▲", "text-success", f"{abs(percent):.2f}"
            elif percent < 0:
                sign, color, percent_str = "▼", "text-danger", f"{abs(percent):.2f}"
            else:
                sign, color, percent_str = "■", "text-secondary", f"{abs(percent):.2f}"
            info_stock.append({
                'name': symbol[1],
                'code': ticker_code,
                'price': safe_val(latest.get('closing_price')),
                'open': safe_val(latest.get('open_price')),
                'previous_close': safe_val(previous['closing_price']) if previous else '-',
                'change': percent_str if percent_str != '0.00' else '-',
                'sign': sign,
                'color': color
            })

    # 3. 熱門ETF與新聞維持原本流程
    # symbols = []
    # names = []
    # with conn.cursor() as cursor:
    #     cursor.execute("SELECT * FROM etf_tickers ORDER BY rand() LIMIT 5")
    #     for row in cursor.fetchall():
    #         symbols.append(row[2])
    #         names.append(row[1])
    # hot_etf = get_hot_etf(symbols, names)

    return render_template(
        "home.html",
        title=web_title,
        navbar=navbar_after_login,
        footer=web_footer,
        tickers=tickers,
        info_stock=info_stock
    )