# Student Data Management System

A fully containerized web application for managing university students, courses,
and enrollments — built with Flask, MySQL 8, Nginx, and Docker Compose.

## Overview

This system provides a browser-based CRUD interface to:
- **Manage Students** — add, search, edit, delete student records
- **Manage Courses** — create and update course information
- **Manage Enrollments** — enroll students in courses and record grades

## Architecture

```
Browser
  │
  │ HTTP :80
  ▼
┌─────────────────────┐
│   nginx:1.25-alpine  │  (frontend network)
│   Reverse Proxy      │
└──────────┬──────────┘
           │ proxy_pass http://app:8000
           ▼
┌─────────────────────┐
│   app (Flask 3)      │  (frontend + backend networks)
│   Python 3.12-slim   │
└──────────┬──────────┘
           │ PyMySQL :3306
           ▼
┌─────────────────────┐
│   db (MySQL 8.0)     │  (backend network only)
│   mysql_data volume  │
└─────────────────────┘
```

Two Docker networks enforce security:
- **backend** — only `db` and `app` can communicate
- **frontend** — only `app` and `nginx` can communicate
- Nginx can **never** reach MySQL directly

## Prerequisites

- Docker Engine 24+
- Docker Compose v2 (`docker compose` command)
- No local MySQL or Python installation needed

## Run Locally (from source)

```bash
# 1. Clone the repository
git clone https://github.com/KhaledNaimi/student-docker-22035111.git
cd student-docker-22035111

# 2. Set up environment variables
cp env.example .env
# Edit .env — change all passwords before running!

# 3. Build and start all containers
docker compose up --build

# 4. Open in browser
open http://localhost        # macOS
xdg-open http://localhost    # Linux
# or just visit http://localhost in any browser
```

The app will be ready when you see `* Running on all addresses (0.0.0.0)` in the logs.
Seed data (10 students, 5 courses, 15 enrollments) loads automatically on first run.

## Stop & Restart (data is preserved)

```bash
# Stop containers (data is safe in the mysql_data volume)
docker compose down

# Restart
docker compose up

# Full reset (WARNING: deletes all data)
docker compose down -v
```

## Run from Docker Hub

```bash
# Pull the application image
docker pull khalednaimi/student-app:latest

# Then run the full stack using docker-compose.yml
# (edit docker-compose.yml to use the pulled image instead of build)
cp env.example .env   # fill in .env first
docker compose up
```

## Environment Variables

Copy `env.example` to `.env` and set these before running:

| Variable          | Description                        | Example              |
|-------------------|------------------------------------|----------------------|
| `DB_NAME`         | MySQL database name                | `studentdb`          |
| `DB_USER`         | MySQL application user             | `smsuser`            |
| `DB_PASSWORD`     | MySQL application user password    | `strong_password`    |
| `DB_ROOT_PASSWORD`| MySQL root password                | `root_strong_pass`   |
| `SECRET_KEY`      | Flask session secret key           | `random_secret_key`  |

## Project Structure

```
student-docker-YOURID/
├── app/
│   ├── Dockerfile          # Flask app image
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── app.py              # All Flask routes
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── students/
│       │   ├── list.html
│       │   ├── form.html
│       │   └── enrollments.html
│       ├── courses/
│       │   ├── list.html
│       │   └── form.html
│       └── enrollments/
│           ├── list.html
│           └── form.html
├── db/
│   └── init.sql            # Schema + seed data
├── nginx/
│   └── nginx.conf          # Reverse proxy config
├── docker-compose.yml
├── env.example
├── .gitignore
└── README.md
```

## Technology Stack

| Layer           | Technology       | Version  |
|-----------------|------------------|----------|
| Database        | MySQL            | 8.0      |
| Web Server      | Nginx            | 1.25     |
| Application     | Python / Flask   | 3.12 / 3 |
| Containerization| Docker Engine    | 24+      |
| Orchestration   | Docker Compose   | v2       |

## Course

Cloud Computing / DevOps Fundamentals — Dr. Mossab Al Hunaity  
Future Scientists Academy

<!-- Docker setup complete -->