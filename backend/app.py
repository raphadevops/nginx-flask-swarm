from flask import Flask, jsonify
import os
import socket
import psycopg2

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "flaskdb"),
        user=os.getenv("DB_USER", "flask"),
        password=os.getenv("DB_PASSWORD", "flask123")
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
            CREATE TABLE IF NOT EXISTS visitas (
                id SERIAL PRIMARY KEY,
                hostname VARCHAR(100),
                data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        cur.execute("INSERT INTO visitas (hostname) VALUES (%s);", (socket.gethostname(),))
        cur.execute("SELECT COUNT(*) FROM visitas;")
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)