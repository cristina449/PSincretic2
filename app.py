# app.py (Flask complet)
from flask import Flask, render_template, request, jsonify
import pyodbc
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Configurare Azure SQL DB
def get_db_connection():
    try:
        server = 'proiects2.database.windows.net'
        database = 'proiects2'
        username = 'floare'
        password = 'trandafir'
        driver = '{ODBC Driver 17 for SQL Server}'
        connection = pyodbc.connect(f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password}')
        return connection
    except Exception as e:
        print(f"❌ Eroare la conexiune: {e}")
        return None

# Ruta principală - interfața web
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint pentru date trimise de ESP32
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
        return jsonify({"led": 1 if float(temp) > 25 else 0})  # Ex: aprinde LED dacă temp > 25
    except Exception as e:
        print(e)
        return jsonify({"error": "Insert error"}), 500
    finally:
        connection.close()

# Endpoint pentru trimitere alertă prin email
@app.route('/alert', methods=['POST'])
def alert():
    try:
        send_email("ALERTĂ INUNDAȚIE", "S-a detectat o inundație în sistem!")
        return jsonify({"status": "Email trimis"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Trimite email prin SMTP
def send_email(subject, content):
    sender = "mihaescucristina17@gmail.com"
    receiver = "faminee@yahoo.com"
    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender, "mzdh kjsh tgxk zrok")
        server.sendmail(sender, receiver, msg.as_string())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
