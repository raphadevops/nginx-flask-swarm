from flask import Flask, jsonify
import os
import socket
import psycopg2
import time

START_TIME = time.time()

app = Flask(__name__)

def get_db():
    secret_path = "/run/secrets/db_password"
    if os.path.exists(secret_path):
        with open(secret_path) as f:
            password = f.read().strip()
    else:
        password = os.getenv("DB_PASSWORD", "")

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "flaskdb"),
        user=os.getenv("DB_USER", "flask"),
        password=password
    )

@app.route("/")
def home():
    return jsonify({
        "message": "API is running successfully!",
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "author": "raphadevops"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/db-test")
def db_test():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({
            "status": "connected",
            "postgres": version[0]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/visits")
def visits():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS visits (
                id SERIAL PRIMARY KEY,
                hostname VARCHAR(100),
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("INSERT INTO visits (hostname) VALUES (%s);", (socket.gethostname(),))
        cur.execute("SELECT COUNT(*) FROM visits;")
        total = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({
            "total_visits": total,
            "served_by": socket.gethostname()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/metrics")
def metrics():
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    db_status = "unavailable"
    total_visits = None
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM visits;")
        total_visits = cur.fetchone()[0]
        cur.close()
        conn.close()
        db_status = "connected"
    except Exception:
        pass 
    return jsonify({
        "hostname": socket.gethostname(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "uptime": f"{hours}h {minutes}m {seconds}s",
        "uptime_seconds": uptime_seconds,
        "database": db_status,
        "total_visits": total_visits
        })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)