# 🚂 Railway Deployment Guide

## Quick Deploy to Railway

### 1. **Prerequisites**
- Railway account (free tier available)
- GitHub repository with your code
- Telegram bot token and group configuration

### 2. **One-Click Deploy**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/deploy)

Or manual deployment:

### 3. **Manual Setup Steps**

#### Step 1: Create New Project
1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your `france-chomage` repository

#### Step 2: Add PostgreSQL Database
1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create `DATABASE_URL` environment variable

#### Step 3: Configure Environment Variables
In Railway dashboard, add these variables:

**Required:**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_GROUP_ID=your_telegram_group_id
```

**Optional (with defaults):**
```env
TELEGRAM_COMMUNICATION_TOPIC_ID=3
TELEGRAM_DESIGN_TOPIC_ID=40
TELEGRAM_RESTAURATION_TOPIC_ID=326
RESULTS_WANTED=20
LOCATION=Paris
```

#### Step 4: Deploy
1. Railway automatically builds and deploys
2. Check logs for successful database initialization
3. Monitor health status in Railway dashboard

## 🔧 **Railway-Specific Features**

### Automatic Configuration
- **DATABASE_URL**: Automatically provided by PostgreSQL service
- **RAILWAY_ENVIRONMENT**: Auto-detected by the app
- **Docker Build**: Uses optimized Railway entrypoint
- **Health Checks**: Built-in monitoring

### Scaling
```bash
# Railway CLI (optional)
railway up
railway status
railway logs
```

### Custom Domain (Pro Plan)
- Add custom domain in Railway dashboard
- SSL automatically configured

## 📊 **Monitoring & Logs**

### Application Logs
- Real-time logs in Railway dashboard
- Filter by service (app vs database)
- Export logs if needed

### Database Management
- Use Railway's built-in database browser
- Or connect with external tools using provided connection string

### Health Monitoring
- Railway monitors health automatically
- Restarts on failure (configured in railway.toml)
- Email notifications available

## 💰 **Cost Optimization**

### Free Tier Limits
- **Execution time**: 500 hours/month
- **Bandwidth**: 100GB/month
- **Database**: 1GB storage

### Recommendations
- Use Conservative scraping settings (already configured)
- Monitor usage in Railway dashboard
- Set up usage alerts

## 🚀 **Production Considerations**

### Performance Settings
The railway.toml is pre-configured with:
- **LinkedIn-only scraping** (safer, faster)
- **Conservative retry limits**
- **Optimized health checks**
- **Automatic restarts**

### Security
- Environment variables encrypted at rest
- TLS encryption for database connections
- No secrets in repository (Railway manages them)

### Backup Strategy
```bash
# Manual backup (if needed)
railway run python -m france_chomage db-status
railway run pg_dump $DATABASE_URL > backup.sql
```

## 🛠️ **Troubleshooting**

### Common Issues

**Deployment fails:**
- Check logs in Railway dashboard
- Verify all required environment variables are set
- Ensure PostgreSQL service is running

**Database connection errors:**
- Verify PostgreSQL service is created
- Check DATABASE_URL is automatically set
- Look for Railway-specific connection issues in logs

**Bot not responding:**
- Verify TELEGRAM_BOT_TOKEN is correct
- Check TELEGRAM_GROUP_ID matches your group
- Monitor application logs for errors

### Debug Commands
```bash
# Railway CLI debugging
railway shell
railway logs --tail
railway variables
```

## 🔄 **CI/CD Integration**

### Auto-Deploy
- Push to main branch triggers automatic deployment
- Railway builds Docker image and restarts service
- Zero-downtime deployments

### Branch Deployments
- Create PR deployments for testing
- Isolated environments per branch
- Easy rollback to previous versions

## 📈 **Scaling Up**

### Resource Upgrades
- Upgrade Railway plan for more resources
- Scale PostgreSQL storage as needed
- Add monitoring and alerting

### Multiple Environments
- Staging environment for testing
- Production environment for live bot
- Database migrations between environments

## 🎯 **Success Checklist**

After deployment, verify:
- ✅ Application starts successfully
- ✅ Database connection established
- ✅ Tables created automatically
- ✅ Health checks passing
- ✅ Telegram messages sent correctly
- ✅ Jobs stored in database
- ✅ No duplicate messages
- ✅ Proper date formatting (dd/mm/yyyy)

**Your bot is now running in the cloud! 🚀**
