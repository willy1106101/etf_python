from flask import Flask
from connection.sql import main

# === Flask 初始化 ===
app = Flask(__name__)
app.secret_key = "etf_taiwan_2025_unversity_ocu_project"

# === 全域變數 ===
web_title = "台股ETF推薦管理平台"
web_footer = web_title + " © 2025 OCU專題"
conn = main()

# === 導入 Blueprint 模組 ===
from bins.login import auth_bp
from bins.profile import profile_bp
from bins.stocks import stock_bp
from bins.home import home_bp


# === 註冊 Blueprint ===
app.register_blueprint(auth_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(stock_bp)
app.register_blueprint(home_bp)


# === 啟動 Flask ===
if __name__ == "__main__":
    app.run(debug=False)
