# 🚀 Deployment Files

This directory contains deployment configurations for different platforms:

## 📁 Structure

```
deployment/
├── docker/                 # Docker Compose setup
│   ├── docker-compose.yml  # Full stack with PostgreSQL
│   ├── docker-entrypoint.sh # Docker initialization script
│   └── init-db.sql         # Database initialization
├── railway/                # Railway cloud deployment  
│   ├── railway-entrypoint.sh # Railway initialization script
│   └── railway-template.json # One-click deploy template
└── README.md              # This file
```

## 🐳 Docker Deployment

```bash
# From project root
make docker-up
```

Or manually:
```bash
cd deployment/docker
docker-compose up -d
```

## 🚂 Railway Deployment

1. **One-click deploy:** Use `railway-template.json`
2. **Manual deploy:** Connect GitHub repo to Railway
3. **CLI deploy:** `railway up` from project root

## ⚙️ Configuration

Both deployment methods:
- ✅ Auto-initialize database tables
- ✅ Handle environment variables
- ✅ Include health checks
- ✅ Support PostgreSQL
- ✅ Provide monitoring

## 📚 Documentation

See `/docs` folder for detailed deployment guides.
