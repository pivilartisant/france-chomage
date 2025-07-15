# 🚀 Deployment Options

## 🚂 Railway (Recommended - Easiest)

### Option 1: One-Click Deploy
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

### Option 2: Manual Deploy
1. **Fork/Clone** this repository
2. **Connect to Railway**: Link your GitHub repo
3. **Add PostgreSQL**: Add database service in Railway dashboard
4. **Set Environment Variables**:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_GROUP_ID=your_group_id
   ```
5. **Deploy**: Railway builds and deploys automatically

**Benefits:**
- ✅ Managed PostgreSQL database
- ✅ Automatic deployments from GitHub
- ✅ Built-in monitoring and logs
- ✅ Free tier available
- ✅ Zero configuration needed

**Cost:** Free tier (500 hours/month) or $5/month for Pro

---

## 🐳 Docker Compose (Local/VPS)

### Quick Start
```bash
# 1. Clone repository
git clone https://github.com/pivilartisant/france-chomage.git
cd france-chomage

# 2. Configure environment
cp .env.example .env
# Edit .env with your Telegram credentials

# 3. Start services
make docker-up

# 4. Check logs
make docker-logs
```

**Benefits:**
- ✅ Full control over infrastructure
- ✅ Local development friendly
- ✅ Easy backup and restore
- ✅ Can run on any VPS

**Requirements:**
- Docker and Docker Compose
- VPS or local machine
- Manual PostgreSQL management

---

## ☁️ Other Cloud Platforms

### Heroku
- Add `heroku-postgresql` addon
- Set `DATABASE_URL` automatically provided
- Use `Procfile`: `worker: python -m france_chomage scheduler`

### DigitalOcean App Platform
- Connect GitHub repository
- Add managed PostgreSQL database
- Configure environment variables

### AWS ECS/Fargate
- Use ECR for Docker image
- RDS for PostgreSQL
- Configure environment variables via task definition

### Google Cloud Run
- Build image and push to GCR
- Use Cloud SQL for PostgreSQL
- Set environment variables in Cloud Run

---

## 🏠 Local Development

### Without Docker
```bash
# 1. Install PostgreSQL locally
brew install postgresql  # macOS
sudo apt install postgresql  # Ubuntu

# 2. Create database
createdb france_chomage

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
make db-init

# 5. Run development
python -m france_chomage scheduler
```

### With Docker
```bash
# Start PostgreSQL only
docker run -d --name postgres \
  -e POSTGRES_DB=france_chomage \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 postgres:15-alpine

# Run application locally
export DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/france_chomage
python -m france_chomage scheduler
```

---

## 📊 Comparison

| Platform | Ease | Cost | Features | Best For |
|----------|------|------|----------|----------|
| **Railway** | ⭐⭐⭐⭐⭐ | Free/Paid | Auto-deploy, DB, Monitoring | **Recommended** |
| **Docker Compose** | ⭐⭐⭐ | Variable | Full control, Local dev | Self-hosting |
| **Heroku** | ⭐⭐⭐⭐ | Paid | Mature platform | Enterprise |
| **Local** | ⭐⭐ | Free | Development | Testing only |

---

## 🛠️ Migration Between Platforms

### From JSON to Database
```bash
# After setting up database on any platform
make db-migrate
```

### From Local to Cloud
1. Export data: `make db-status` 
2. Deploy to cloud platform
3. Let auto-migration handle the rest

### Backup Strategy
```bash
# Create backup
python -m france_chomage backup --all

# Restore from backup
python -m france_chomage restore --file backup.json
```

---

## 🎯 Recommended Setup

**For beginners:** Railway (one-click deploy)
**For developers:** Docker Compose (local) + Railway (production)
**For enterprises:** Cloud provider with managed services

**Next Step:** Choose your platform and follow the specific guide!
