# 🐳 Nginx + Flask + PostgreSQL com Docker Swarm

Projeto de demonstração de uma arquitetura com **Nginx como reverse proxy** para uma aplicação **Python/Flask** conectada a um banco de dados **PostgreSQL**, orquestrado via **Docker Swarm** com múltiplas réplicas, load balancing automático e persistência de dados via volumes.

## 🏗️ Arquitetura

```
                    ┌─────────────┐
      HTTP :80      │             │     HTTP :5000
  ───────────────►  │    Nginx    │  ───────────────►  Flask Réplica 1
                    │  (Proxy +   │  ───────────────►  Flask Réplica 2
                    │   LB)       │                         │
                    └─────────────┘                         │
                                                            ▼
                                                       PostgreSQL
                                                            │
                                                            ▼
                                                     Volume (dados
                                                     persistidos)
```

- **Nginx**: Recebe requisições externas e distribui entre réplicas via load balance
- **Flask + Gunicorn**: 2 réplicas rodando em paralelo gerenciadas pelo Swarm
- **PostgreSQL**: Banco de dados com volume para persistência dos dados
- **Docker Swarm**: Orquestra os serviços, garante disponibilidade e reinicia containers com falha
- **Overlay Network**: Rede interna isolada para comunicação entre os serviços

## 🔄 Diferença para o Docker Compose

| | Docker Compose | Docker Swarm |
|---|---|---|
| Uso | Desenvolvimento local | Produção / Multi-nó |
| Réplicas | Não | Sim |
| Load Balance | Não | Automático |
| Alta disponibilidade | Não | Sim |
| Orquestração | Básica | Avançada |

## 🚀 Como rodar

### Pré-requisitos
- Docker >= 24.x
- Docker Swarm ativo

### Clonando o repositório

```bash
git clone https://github.com/raphabdev/nginx-flask-swarm.git
cd nginx-flask-swarm
```

### Ativando o Swarm

```bash
docker swarm init
```

### Build da imagem

```bash
docker build -t nginx-flask-swarm-backend:latest ./backend
```

### Subindo o stack

```bash
docker stack deploy -c docker-stack.yml flask-swarm
```

### Verificando os serviços

```bash
docker stack services flask-swarm
```

Aguarde até aparecer `2/2` no backend, `1/1` no Nginx e `1/1` no PostgreSQL.

### Testando os endpoints

```bash
# Endpoint principal
curl http://localhost/

# Health check
curl http://localhost/health

# Informações da app
curl http://localhost/info

# Testa conexão com o banco
curl http://localhost/db-test

# Registra e conta visitas (persiste no banco)
curl http://localhost/visitas

# Health check do Nginx
curl http://localhost/nginx-health
```

### Visualizando o load balance

Execute o comando abaixo várias vezes e observe o campo `hostname` mudando entre as réplicas:

```bash
curl http://localhost/visitas
```

### Visualizando logs

```bash
# Backend
docker service logs -f flask-swarm_backend

# PostgreSQL
docker service logs -f flask-swarm_postgres

# Nginx
docker service logs -f flask-swarm_nginx
```

### Derrubando o stack

```bash
docker stack rm flask-swarm
```

### Verificando o volume após derrubar o stack

```bash
docker volume ls
```

O volume `flask-swarm_postgres_data` persiste mesmo após o stack ser removido. Ao subir novamente, os dados estarão intactos.

## 📁 Estrutura do projeto

```
.
├── backend/
│   ├── app.py            # Aplicação Flask
│   ├── requirements.txt  # Dependências Python
│   └── Dockerfile        # Imagem do backend
├── nginx/
│   └── nginx.conf        # Configuração do reverse proxy
├── docker-stack.yml      # Orquestração via Docker Swarm
└── README.md
```

## 🔍 Conceitos demonstrados

- **Docker Swarm** como orquestrador de containers
- **Réplicas** — múltiplas instâncias do mesmo serviço
- **Load Balancing** automático entre réplicas
- **Docker Volumes** — persistência de dados do PostgreSQL
- **Overlay Network** para comunicação entre serviços
- **Restart Policy** para alta disponibilidade
- **Update Config** para deploy sem downtime
- **Reverse Proxy** com Nginx
- **Variáveis de ambiente** para configuração por serviço

## 🛠️ Tecnologias

| Tecnologia | Versão | Papel |
|---|---|---|
| Nginx | 1.25 Alpine | Reverse Proxy + Load Balancer |
| Python | 3.12 Slim | Runtime |
| Flask | 3.0.3 | Web Framework |
| Gunicorn | 22.0.0 | WSGI Server |
| PostgreSQL | 16 Alpine | Banco de Dados |
| Docker Swarm | - | Orquestração |

---

**Autor:** raphabdev
