# Production Deployment Guide

**Bareera Intl. HR Module**  
**Complete Guide for Production Deployment**

---

## ⚠️ Important Warning

**This application is currently configured for DEVELOPMENT ONLY**. Before deploying to production, you MUST complete all security and configuration steps outlined in this guide.

---

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Deployment Options](#deployment-options)
3. [Server Setup](#server-setup)
4. [Security Hardening](#security-hardening)
5. [Production Configuration](#production-configuration)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

### Essential Tasks (Must Complete)

- [ ] **Migrate to Database** - Follow [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)
- [ ] **Change Secret Key** - Generate secure random key
- [ ] **Update Default Passwords** - Change all test account passwords
- [ ] **Disable Debug Mode** - Set `debug=False` in production
- [ ] **Setup HTTPS** - Configure SSL/TLS certificates
- [ ] **Configure Firewall** - Only allow necessary ports
- [ ] **Setup Backups** - Automated daily backups
- [ ] **Error Logging** - Configure proper logging system
- [ ] **Environment Variables** - Move sensitive config to env vars

### Recommended Tasks

- [ ] Setup monitoring and alerting
- [ ] Configure rate limiting
- [ ] Add CSRF protection
- [ ] Implement audit logging
- [ ] Setup email notifications
- [ ] Configure CDN for static files
- [ ] Add automated testing
- [ ] Setup staging environment

---

## Deployment Options

### Option 1: Cloud Platform (Recommended)

**Best for**: Most organizations, scalable, managed infrastructure

#### Platforms:
- **Heroku**: Easy deployment, managed PostgreSQL
- **AWS**: Full control, EC2 + RDS
- **Google Cloud Platform**: App Engine or Compute Engine
- **DigitalOcean**: Simple VPS, App Platform
- **Railway/Render**: Modern platforms with easy setup

### Option 2: On-Premise Server

**Best for**: Organizations with existing infrastructure, data sovereignty requirements

#### Requirements:
- Ubuntu Server 20.04+ or similar Linux distribution
- Minimum 2GB RAM, 2 CPU cores
- 20GB+ storage
- Static IP address or domain name

### Option 3: Docker Container

**Best for**: Consistent deployment across environments

---

## Server Setup

### Option A: Ubuntu Server Setup (Detailed)

#### Step 1: Initial Server Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.10 python3-pip python3-venv nginx supervisor postgresql git

# Create application user
sudo adduser --disabled-password --gecos "" hrapp
sudo usermod -aG sudo hrapp

# Switch to application user
sudo su - hrapp
```

#### Step 2: Setup Application

```bash
# Create application directory
mkdir -p /home/hrapp/bareera-hr
cd /home/hrapp/bareera-hr

# Clone or upload your application
# If using git:
git clone <your-repository-url> .
# Or use SCP/SFTP to upload files

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

#### Step 3: Configure PostgreSQL

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE bareera_hr;
CREATE USER hrapp_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE bareera_hr TO hrapp_user;
\q

# Run migration (if completed)
psql bareera_hr < migration_schema.sql
```

#### Step 4: Configure Gunicorn

Create `/home/hrapp/bareera-hr/gunicorn_config.py`:

```python
# Gunicorn configuration file
import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Logging
accesslog = "/home/hrapp/bareera-hr/logs/access.log"
errorlog = "/home/hrapp/bareera-hr/logs/error.log"
loglevel = "info"

# Process naming
proc_name = "bareera_hr"

# Server mechanics
daemon = False
pidfile = "/home/hrapp/bareera-hr/gunicorn.pid"
user = "hrapp"
group = "hrapp"
```

Create log directory:
```bash
mkdir -p /home/hrapp/bareera-hr/logs
```

#### Step 5: Configure Supervisor

Create `/etc/supervisor/conf.d/bareera-hr.conf`:

```ini
[program:bareera-hr]
command=/home/hrapp/bareera-hr/venv/bin/gunicorn -c /home/hrapp/bareera-hr/gunicorn_config.py app:app
directory=/home/hrapp/bareera-hr
user=hrapp
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/home/hrapp/bareera-hr/logs/supervisor_error.log
stdout_logfile=/home/hrapp/bareera-hr/logs/supervisor_access.log
environment=PATH="/home/hrapp/bareera-hr/venv/bin"
```

Start supervisor:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start bareera-hr
sudo supervisorctl status
```

#### Step 6: Configure Nginx

Create `/etc/nginx/sites-available/bareera-hr`:

```nginx
upstream bareera_hr {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;
    
    client_max_body_size 16M;  # For resume uploads
    
    # Static files
    location /static {
        alias /home/hrapp/bareera-hr/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Application
    location / {
        proxy_pass http://bareera_hr;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/bareera-hr /etc/nginx/sites-enabled/
sudo nginx -t  # Test configuration
sudo systemctl restart nginx
```

#### Step 7: Configure SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

After SSL setup, uncomment the HTTPS redirect in Nginx config:
```bash
sudo nano /etc/nginx/sites-available/bareera-hr
# Uncomment: return 301 https://$server_name$request_uri;
sudo systemctl reload nginx
```

---

### Option B: Docker Deployment

#### Step 1: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application files
COPY . .

# Create non-root user
RUN useradd -m -u 1000 hrapp && chown -R hrapp:hrapp /app
USER hrapp

# Expose port
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "60", "app:app"]
```

#### Step 2: Create docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://hrapp:password@db:5432/bareera_hr
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    depends_on:
      - db
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=bareera_hr
      - POSTGRES_USER=hrapp
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./certs:/etc/nginx/certs:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
```

#### Step 3: Deploy

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down
```

---

### Option C: Heroku Deployment

#### Step 1: Prepare Application

Create `Procfile`:
```
web: gunicorn app:app
```

Create `runtime.txt`:
```
python-3.10.12
```

#### Step 2: Deploy

```bash
# Install Heroku CLI
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create app
heroku create bareera-hr-prod

# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Set config vars
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')
heroku config:set FLASK_ENV=production

# Deploy
git push heroku main

# Run migrations
heroku run python migrate_data.py

# Open app
heroku open
```

---

## Security Hardening

### 1. Change Secret Key

**In `app.py`, replace:**
```python
app.secret_key = 'your-secret-key-change-in-production'
```

**With environment variable:**
```python
import os
app.secret_key = os.environ.get('SECRET_KEY') or os.urandom(32)
```

**Generate secure key:**
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Update Default Passwords

```python
# Login as admin and change password in UI
# Or use Python script to update users.json (before DB migration)

import bcrypt
import json

password = 'new_secure_password'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Update user record with new hashed password
```

### 3. Disable Debug Mode

```python
# app.py - Change from:
app.run(debug=True, port=5002, host='127.0.0.1')

# To:
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
```

### 4. Add Security Headers

```python
from flask import Flask

@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 5. Setup Environment Variables

Create `.env` file (DON'T commit to git):
```bash
SECRET_KEY=your_secret_key_here
DATABASE_URL=postgresql://user:pass@localhost/bareera_hr
FLASK_ENV=production
ADMIN_EMAIL=admin@example.com
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Load in app:
```python
from dotenv import load_dotenv
load_dotenv()
```

### 6. Configure Firewall

```bash
# Ubuntu UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable
sudo ufw status
```

---

## Production Configuration

### 1. Logging Configuration

Create `logging_config.py`:

```python
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug:
        # Create logs directory
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler
        file_handler = RotatingFileHandler(
            'logs/bareera_hr.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Bareera HR startup')
```

Use in `app.py`:
```python
from logging_config import setup_logging
setup_logging(app)
```

### 2. Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verify connections before using
)
```

### 3. Rate Limiting

```bash
pip install flask-limiter
```

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
    pass
```

---

## Monitoring and Maintenance

### 1. Application Monitoring

**Using Supervisor:**
```bash
# Check status
sudo supervisorctl status bareera-hr

# Restart
sudo supervisorctl restart bareera-hr

# View logs
sudo tail -f /home/hrapp/bareera-hr/logs/error.log
```

### 2. Database Backups

Create `/home/hrapp/backup_db.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/home/hrapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
FILENAME="db_backup_$DATE.sql"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump bareera_hr > "$BACKUP_DIR/$FILENAME"

# Compress
gzip "$BACKUP_DIR/$FILENAME"

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $FILENAME.gz"
```

Make executable and schedule:
```bash
chmod +x /home/hrapp/backup_db.sh

# Add to crontab (runs daily at 2 AM)
crontab -e
0 2 * * * /home/hrapp/backup_db.sh >> /home/hrapp/logs/backup.log 2>&1
```

### 3. Log Rotation

Logs are automatically rotated by:
- Application: Using `RotatingFileHandler` (configured above)
- Nginx: Default logrotate configuration
- Supervisor: Configured in supervisor config

### 4. Health Check Endpoint

Add to `app.py`:

```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return {'status': 'healthy', 'database': 'connected'}, 200
    except:
        return {'status': 'unhealthy', 'database': 'disconnected'}, 500
```

---

## Troubleshooting

### Common Issues

#### 1. Application Won't Start

```bash
# Check supervisor logs
sudo tail -f /home/hrapp/bareera-hr/logs/supervisor_error.log

# Check permissions
ls -la /home/hrapp/bareera-hr

# Test application manually
cd /home/hrapp/bareera-hr
source venv/bin/activate
python app.py
```

#### 2. 502 Bad Gateway

```bash
# Check if Gunicorn is running
sudo supervisorctl status

# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Verify Gunicorn socket
curl http://127.0.0.1:8000
```

#### 3. Database Connection Errors

```bash
# Test PostgreSQL connection
psql -U hrapp_user -d bareera_hr -h localhost

# Check PostgreSQL is running
sudo systemctl status postgresql

# View PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

#### 4. SSL Certificate Issues

```bash
# Test certificate
sudo certbot certificates

# Renew manually
sudo certbot renew

# Check Nginx SSL config
sudo nginx -t
```

---

## Performance Optimization

### 1. Enable Gzip Compression

In Nginx config:
```nginx
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/xml+rss application/json;
```

### 2. Cache Static Files

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 365d;
    add_header Cache-Control "public, immutable";
}
```

### 3. Database Indexing

Ensure all foreign keys and frequently queried columns are indexed (already in migration schema).

---

## Post-Deployment Checklist

- [ ] Application accessible via domain name
- [ ] HTTPS working correctly
- [ ] All features tested in production
- [ ] Default passwords changed
- [ ] Backups running and tested
- [ ] Monitoring alerts configured
- [ ] Error logging working
- [ ] Documentation updated
- [ ] Team trained on deployment process
- [ ] Rollback plan documented and tested

---

## Additional Resources

- [Flask Production Best Practices](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Administration](https://www.postgresql.org/docs/current/admin.html)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

## Support

For deployment assistance, contact:
- **Developer**: Codecraft Studios Pakistan (CSP)
- **Project**: Bareera Intl. HR Module
- **Email**: support@example.com

---

**Last Updated**: October 1, 2025  
**Version**: 1.0

