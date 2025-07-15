# Docker Setup Guide

## 🐳 Quick Start with Docker Compose

### 1. **Prerequisites**
- Docker and Docker Compose installed
- Your `.env` file with Telegram configuration

### 2. **Start Services**
```bash
# Start bot with PostgreSQL database
make docker-up
# or
docker-compose up -d
```

### 3. **Check Status**
```bash
# View application logs
make docker-logs

# View database logs  
make docker-db-logs

# Check container status
docker-compose ps
```

### 4. **Database Management**
```bash
# Start with admin interface (Adminer)
make docker-admin

# Access Adminer at: http://localhost:8081
# Server: db, Username: postgres, Password: postgres, Database: france_chomage
```

## 🔧 **Available Commands**

### Docker Compose (Recommended)
```bash
make docker-up          # Start all services
make docker-down        # Stop all services
make docker-logs        # Show app logs
make docker-db-logs     # Show database logs
make docker-admin       # Start with admin interface
make docker-rebuild     # Rebuild and restart
make docker-clean       # Clean up everything
```

### Standalone Docker
```bash
make docker-build       # Build image only
make docker-run         # Run without database
make docker-test        # Test configuration
```

## 🏗️ **Architecture**

The Docker setup includes:

### **Services**
- **app**: France Chômage Bot application
- **db**: PostgreSQL 15 database
- **adminer**: Database admin interface (optional)

### **Features**
- **Automatic database initialization**
- **Health checks** for all services
- **Persistent data volumes**
- **Proper service dependencies**
- **LinkedIn-only scraping** (safer in Docker)

### **Volumes**
- `postgres_data`: Database persistence
- `job_data`: Backup files and logs
- `./logs`: Application logs (mounted)

## 🔍 **Monitoring**

### Application Health
```bash
# Check if app is healthy
docker-compose exec app python -c "from france_chomage.config import settings; print('App OK')"

# Check database status
docker-compose exec app python -m france_chomage db-status
```

### Database Access
```bash
# Connect to PostgreSQL directly
docker-compose exec db psql -U postgres -d france_chomage

# Example queries:
# SELECT COUNT(*) FROM jobs;
# SELECT category, COUNT(*) FROM jobs GROUP BY category;
```

## 🚀 **Production Deployment**

### Environment Variables
The docker-compose.yml reads from your `.env` file:
```env
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_GROUP_ID=your_group_id
TELEGRAM_COMMUNICATION_TOPIC_ID=3
TELEGRAM_DESIGN_TOPIC_ID=40
TELEGRAM_RESTAURATION_TOPIC_ID=326
```

### Scaling
```bash
# Run multiple app instances
docker-compose up --scale app=2

# Load balancer would be needed for multiple instances
```

### Backup
```bash
# Backup database
docker-compose exec db pg_dump -U postgres france_chomage > backup.sql

# Restore database
docker-compose exec -T db psql -U postgres france_chomage < backup.sql
```

## 🛠️ **Troubleshooting**

### Common Issues

**Database connection failed:**
```bash
# Check if database is ready
docker-compose exec db pg_isready -U postgres

# Restart services
make docker-rebuild
```

**App won't start:**
```bash
# Check logs
make docker-logs

# Check environment variables
docker-compose exec app env | grep TELEGRAM
```

**Permission errors:**
```bash
# Fix file permissions
chmod +x docker-entrypoint.sh
make docker-rebuild
```

### Reset Everything
```bash
# Nuclear option - removes all data
make docker-clean
docker volume prune
make docker-up
```

## 📊 **Performance**

### Resource Usage
- **PostgreSQL**: ~100MB RAM, minimal CPU
- **App**: ~50MB RAM, CPU varies with scraping
- **Total**: ~200MB RAM recommended minimum

### Optimization
- Uses Alpine PostgreSQL (smaller image)
- Multi-stage build potential for smaller app image
- Proper health checks prevent cascade failures
- LinkedIn-only mode reduces anti-bot detection
