# app.py
from flask import Flask, render_template, request, jsonify
import pyodbc
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(_name_)  

# 🔧 Conectare la Azure SQL
def get_db_connection():
    try:
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_NAME")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        driver = '{ODBC Driver 17 for SQL Server}'
        conn_str = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}'
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"❌ DB Connection error: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    temp = request.form.get('temperature')
    flood = request.form.get('flood')

    print(f"📥 Primit: temperature={temp}, flood={flood}")  

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "DB connection failed"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO telemetry (temperature, humidity, EventEnqueuedUtcTime)
            VALUES (?, ?, GETDATE())
        """, (temp, flood))
        connection.commit()
        cursor.close()

        # 🔁 Trimite stare LED înapoi
        return jsonify({"led": 1 if float(temp) > 25 else 0})

    except Exception as e:
        print(f"❌ Insert error: {e}")
        return jsonify({"error": "Insert error"}), 500
    finally:
        connection.close()

@app.route('/alert', methods=['POST'])
def alert():
    try:
        send_email("🌊 ALERTĂ INUNDAȚIE", "S-a detectat o inundație în sistem!")
        return jsonify({"status": "Email trimis"})
    exce
