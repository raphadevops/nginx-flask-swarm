# 🐝 Nginx + Flask + PostgreSQL with Docker Swarm

A demonstration project of a distributed multi-container architecture using **Docker Swarm** for orchestration, **Nginx** as a load balancer and reverse proxy, **Flask/Gunicorn** as the backend with **2 replicas**, and **PostgreSQL** for data persistence.

---

## 🏗️ Architecture

```
                   ┌─────────────┐
     HTTP :80      │             │    HTTP :5000     ┌─────────────────────┐
 ──────────────►   │    Nginx    │ ────────────────► │  Flask replica 1    │
                   │  (Proxy +   │                   └─────────────────────┘
                   │  Balancer)  │                   ┌─────────────────────┐
                   │             │ ────────────────► │  Flask replica 2    │
                   └─────────────┘                   └──────────┬──────────┘
                                                                │
                                                                ▼
                                                    ┌─────────────────────┐
                                                    │   PostgreSQL :5432  │
                                                    │  (persistent data)  │
                                                    └─────────────────────┘
```

| Component | Role | Replicas |
|---|---|---|
| **Nginx** | Load balancer + reverse proxy | 1 |
| **Flask + Gunicorn** | Python backend with 2 Gunicorn workers | 2 |
| **PostgreSQL** | Relational database with persistent volume | 1 |

---

## 🆚 How this project differs from nginx-flask-docker

| Feature | nginx-flask-docker | nginx-flask-swarm |
|---|---|---|
| Orchestration | Docker Compose | Docker Swarm |
| Network | bridge | overlay (multi-node) |
| Flask replicas | 1 | 2 (load balanced) |
| Database | — | PostgreSQL |
| Dockerfile | Standard | Multi-stage build |
| Rolling update | — | ✓ zero downtime |

---

## 🚀 Getting Started

### Prerequisites

- Docker >= 24.x with Swarm mode enabled
- Docker Compose >= 2.x (for local build)

### 1. Initialize Docker Swarm

```bash
docker swarm init
```

### 2. Build the backend image

```bash
# Standard build
docker build -t nginx-flask-swarm-backend:latest ./backend

# Or using multi-stage build (smaller image)
docker build -f backend/Dockerfile.multistage -t nginx-flask-swarm-backend:latest ./backend
```

### 3. Deploy the stack

```bash
docker stack deploy -c docker-stack.yml nginx-flask-swarm
```

### 4. Check running services

```bash
# List all services and replicas
docker service ls

# Check replica status
docker service ps nginx-flask-swarm_backend
```

---

## 🔗 Available Endpoints

| Endpoint | Description |
|---|---|
| `GET /` | Returns app status, container hostname and environment |
| `GET /health` | Application health check — returns `{ "status": "healthy" }` |
| `GET /db-test` | Tests PostgreSQL connection and returns server version |
| `GET /visitas` | Inserts a visit record and returns total count + serving hostname |
| `GET /nginx-health` | Nginx health check — responds without hitting Flask |

### Testing

```bash
# Main endpoint
curl http://localhost/

# Application health check
curl http://localhost/health

# Test database connection
curl http://localhost/db-test

# Register a visit (run multiple times to see load balancing in action)
curl http://localhost/visitas

# Nginx health check
curl http://localhost/nginx-health
```

> 💡 **Tip:** Call `/visitas` multiple times and watch the `registrado_por` field alternate between different hostnames — proof that Swarm is distributing requests across both Flask replicas.

---

## 📋 Useful Commands

```bash
# View logs from all replicas of a service
docker service logs -f nginx-flask-swarm_backend

# Scale replicas up or down
docker service scale nginx-flask-swarm_backend=3

# Remove the entire stack
docker stack rm nginx-flask-swarm

# List volumes (persistent data)
docker volume ls

# Leave Swarm mode
docker swarm leave --force
```

---

## 📁 Project Structure

```
nginx-flask-swarm/
├── backend/
│   ├── app.py                  # Flask app with PostgreSQL integration
│   ├── requirements.txt        # Flask + Gunicorn + psycopg2-binary
│   ├── dockerfile              # Standard Dockerfile
│   └── Dockerfile.multistage   # Multi-stage build (optimized image)
├── nginx/
│   └── nginx.conf              # Reverse proxy + load balancer config
├── docker-stack.yml            # Swarm stack definition
└── README.md
```

---

## 🔍 Key Concepts Demonstrated

- **Docker Swarm orchestration** — deploying and managing services across a cluster
- **Load balancing** — Nginx distributes traffic between 2 Flask replicas
- **Overlay network** — enables container communication across multiple Swarm nodes
- **Multi-stage build** — separate build and runtime stages for a smaller, cleaner final image
- **Rolling update** — `parallelism: 1, delay: 10s` updates one replica at a time with zero downtime
- **Persistent volume** — PostgreSQL data survives container restarts via `postgres_data` named volume
- **Environment variables** — all credentials and config injected via Compose/Stack, never hardcoded
- **Non-root user** — Flask runs as `appuser` inside the container (security best practice)
- **Replica-aware logging** — `/visitas` records which hostname served each request, making load balancing observable

---

## 🛠️ Tech Stack

| Technology | Version | Role |
|---|---|---|
| Nginx | 1.25 Alpine | Reverse Proxy + Load Balancer |
| Python | 3.12 Slim | Runtime |
| Flask | 3.0.3 | Web Framework |
| Gunicorn | 22.0.0 | WSGI Server |
| PostgreSQL | 16 Alpine | Relational Database |
| psycopg2-binary | 2.9.9 | PostgreSQL driver for Python |
| Docker Swarm | — | Container Orchestration |

---

## 👤 Author

**Raphael** — [raphadevops](https://github.com/raphadevops)
