# app.py (cu variabile de mediu)
from flask import Flask, render_template, request, jsonify
import pyodbc
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# Configurare Azure SQL DB din variabile de mediu
def get_db_connection():
    try:
        server = os.getenv("DB_SERVER")
        database = os.getenv("DB_NAME")
        username = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        driver = '{ODBC Driver 17 for SQL Server}'
        connection = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        return connection
    except Exception as e:
        print(f"❌ Eroare la conexiune: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    temp = request.form.get('temperature')
    flood = request.form.get('flood')

    connection = get_db_connection()
    if not connection:
        return jsonify({"error": "DB error"}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO telemetry (temperature, humidity, EventEnqueuedUtcTime) VALUES (?, ?, GETDATE())", (temp, flood))
        connection.commit()
        cursor.close()
        return jsonify({"led": 1 if float(temp) > 25 else 0})
    except Exception as e:
        print(e)
        return jsonify({"error": "Insert error"}), 500
    finally:
        connection.close()

@app.route('/alert', methods=['POST'])
def alert():
    try:
        send_email("ALERTĂ INUNDAȚIE", "S-a detectat o inundație în sistem!")
        return jsonify({"status": "Email trimis"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def send_email(subject, content):
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL_RECEIVER")

    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
