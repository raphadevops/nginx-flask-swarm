from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "API rodando com sucesso!",
        "hostname": socket.gethostname(),
        "replica": os.getenv("HOSTNAME", "unknown"),
        "environment": os.getenv("ENVIRONMENT", "development")
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/info")
def info():
    return jsonify({
        "app": "nginx-flask-swarm",
        "version": "1.0.0",
        "stack": ["Nginx", "Python", "Flask", "Docker Swarm"]
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)