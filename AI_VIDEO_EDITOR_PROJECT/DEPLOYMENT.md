# AI VIDEO EDITOR - DEPLOYMENT GUIDE

**Last Updated:** December 26, 2024  
**Status:** Ready for Implementation

---

## DEPLOYMENT OVERVIEW

This guide covers deploying the AI Video Editor to production on AWS.

### Deployment Environments
- **Development:** Local machine with Docker Compose
- **Staging:** AWS EC2 with Docker
- **Production:** AWS ECS with load balancing and auto-scaling

---

## PREREQUISITES

### AWS Account Setup
1. Create AWS account (https://aws.amazon.com/)
2. Create IAM user with programmatic access
3. Configure AWS CLI: `aws configure`
4. Create S3 bucket for file storage
5. Create RDS PostgreSQL database
6. Create ElastiCache Redis cluster

### Required Tools
- AWS CLI v2
- Docker & Docker Compose
- Terraform (optional, for infrastructure as code)
- kubectl (for Kubernetes deployments)

---

## STAGING DEPLOYMENT (AWS EC2)

### Step 1: Launch EC2 Instance

```bash
# AWS Console → EC2 → Launch Instance

Instance Details:
├─ AMI: Ubuntu 22.04 LTS
├─ Instance Type: t3.large (2 vCPU, 8GB RAM)
├─ Storage: 50GB gp3
├─ Security Group: Allow 80, 443, 8000, 3000
└─ Key Pair: Create and download

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip
```

### Step 2: Install Docker & Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install FFmpeg
sudo apt install ffmpeg -y

# Verify installations
docker --version
docker-compose --version
ffmpeg -version
```

### Step 3: Clone Repository

```bash
# Clone your repository
git clone https://github.com/yourusername/ai-video-editor.git
cd ai-video-editor

# Create environment file
cp backend/.env.example backend/.env

# Edit .env with production values
nano backend/.env

# Key variables to update:
DATABASE_URL=postgresql://editor:password@your-rds-endpoint:5432/ai_video_editor
REDIS_URL=redis://your-elasticache-endpoint:6379/0
SECRET_KEY=generate-strong-secret-key
UPLOAD_DIR=/mnt/storage/uploads
```

### Step 4: Create Storage Volume

```bash
# Create uploads directory
sudo mkdir -p /mnt/storage/uploads
sudo chown ubuntu:ubuntu /mnt/storage/uploads
sudo chmod 755 /mnt/storage/uploads

# Or mount EBS volume
sudo mkfs -t ext4 /dev/xvdf
sudo mkdir -p /mnt/storage
sudo mount /dev/xvdf /mnt/storage
```

### Step 5: Configure RDS PostgreSQL

```bash
# Create database
aws rds create-db-instance \
  --db-instance-identifier ai-video-editor-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username editor \
  --master-user-password your-password \
  --allocated-storage 100

# Wait for database to be available
aws rds describe-db-instances --db-instance-identifier ai-video-editor-db

# Connect and create database
psql -h your-rds-endpoint -U editor -d postgres
CREATE DATABASE ai_video_editor;
\q
```

### Step 6: Configure ElastiCache Redis

```bash
# Create Redis cluster
aws elasticache create-cache-cluster \
  --cache-cluster-id ai-video-editor-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1

# Get endpoint
aws elasticache describe-cache-clusters --cache-cluster-id ai-video-editor-redis
```

### Step 7: Build and Start Services

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### Step 8: Run Database Migrations

```bash
# Run migrations
docker-compose exec backend alembic upgrade head

# Create tables
docker-compose exec backend python -c "from app.models import *; from app.config import engine; Base.metadata.create_all(bind=engine)"
```

### Step 9: Configure Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/default

# Add this configuration:
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Test and restart Nginx
sudo nginx -t
sudo systemctl restart nginx
```

### Step 10: Set Up SSL Certificate

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

---

## PRODUCTION DEPLOYMENT (AWS ECS)

### Step 1: Create ECR Repositories

```bash
# Create repositories for backend and frontend
aws ecr create-repository --repository-name ai-video-editor-backend
aws ecr create-repository --repository-name ai-video-editor-frontend

# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account-id.dkr.ecr.us-east-1.amazonaws.com
```

### Step 2: Build and Push Docker Images

```bash
# Build backend image
docker build -t ai-video-editor-backend:latest backend/
docker tag ai-video-editor-backend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-backend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-backend:latest

# Build frontend image
docker build -t ai-video-editor-frontend:latest frontend/
docker tag ai-video-editor-frontend:latest your-account-id.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-frontend:latest
docker push your-account-id.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-frontend:latest
```

### Step 3: Create ECS Cluster

```bash
# Create cluster
aws ecs create-cluster --cluster-name ai-video-editor

# Create task definition (backend)
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json

# Create task definition (frontend)
aws ecs register-task-definition --cli-input-json file://frontend-task-definition.json
```

### Step 4: Create Services

```bash
# Create backend service
aws ecs create-service \
  --cluster ai-video-editor \
  --service-name backend \
  --task-definition ai-video-editor-backend:1 \
  --desired-count 2 \
  --launch-type EC2

# Create frontend service
aws ecs create-service \
  --cluster ai-video-editor \
  --service-name frontend \
  --task-definition ai-video-editor-frontend:1 \
  --desired-count 2 \
  --launch-type EC2
```

### Step 5: Configure Load Balancer

```bash
# Create Application Load Balancer
aws elbv2 create-load-balancer \
  --name ai-video-editor-alb \
  --subnets subnet-12345 subnet-67890 \
  --security-groups sg-12345

# Create target groups
aws elbv2 create-target-group \
  --name backend-targets \
  --protocol HTTP \
  --port 8000 \
  --vpc-id vpc-12345

aws elbv2 create-target-group \
  --name frontend-targets \
  --protocol HTTP \
  --port 3000 \
  --vpc-id vpc-12345

# Create listeners
aws elbv2 create-listener \
  --load-balancer-arn arn:aws:elasticloadbalancing:... \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=arn:aws:elasticloadbalancing:...
```

---

## CONTINUOUS DEPLOYMENT (CI/CD)

### GitHub Actions Workflow

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
      
      - name: Build and push backend
        run: |
          docker build -t backend:${{ github.sha }} backend/
          docker tag backend:${{ github.sha }} ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-backend:${{ github.sha }}
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-backend:${{ github.sha }}
      
      - name: Build and push frontend
        run: |
          docker build -t frontend:${{ github.sha }} frontend/
          docker tag frontend:${{ github.sha }} ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-frontend:${{ github.sha }}
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/ai-video-editor-frontend:${{ github.sha }}
      
      - name: Update ECS service
        run: |
          aws ecs update-service \
            --cluster ai-video-editor \
            --service backend \
            --force-new-deployment
```

---

## MONITORING & LOGGING

### CloudWatch Setup

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/ai-video-editor

# Create log streams
aws logs create-log-stream --log-group-name /ecs/ai-video-editor --log-stream-name backend
aws logs create-log-stream --log-group-name /ecs/ai-video-editor --log-stream-name frontend
```

### CloudWatch Alarms

```bash
# CPU utilization alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ai-video-editor-high-cpu \
  --alarm-description "Alert when CPU exceeds 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold

# Error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name ai-video-editor-high-errors \
  --alarm-description "Alert when error rate exceeds 5%" \
  --metric-name ErrorCount \
  --namespace AWS/ApplicationELB \
  --statistic Sum \
  --period 300 \
  --threshold 50 \
  --comparison-operator GreaterThanThreshold
```

---

## BACKUP & DISASTER RECOVERY

### Database Backups

```bash
# Enable automated backups
aws rds modify-db-instance \
  --db-instance-identifier ai-video-editor-db \
  --backup-retention-period 30 \
  --preferred-backup-window "03:00-04:00"

# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier ai-video-editor-db \
  --db-snapshot-identifier ai-video-editor-backup-$(date +%Y%m%d)
```

### S3 Backups

```bash
# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ai-video-editor-uploads \
  --versioning-configuration Status=Enabled

# Enable lifecycle policy (delete old versions after 30 days)
aws s3api put-bucket-lifecycle-configuration \
  --bucket ai-video-editor-uploads \
  --lifecycle-configuration file://lifecycle.json
```

### Disaster Recovery Plan

```
RTO (Recovery Time Objective): 1 hour
RPO (Recovery Point Objective): 1 hour

Recovery Steps:
1. Restore RDS from latest snapshot (15 min)
2. Restore S3 files from versioning (5 min)
3. Redeploy ECS services (10 min)
4. Run database migrations (5 min)
5. Verify application (10 min)
Total: ~45 minutes
```

---

## PERFORMANCE TUNING

### Database Optimization

```sql
-- Create indexes
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_videos_job_id ON videos(job_id);

-- Enable query optimization
ANALYZE;
VACUUM ANALYZE;
```

### Redis Optimization

```bash
# Configure Redis for caching
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
redis-cli CONFIG REWRITE
```

### CDN Configuration

```bash
# Create CloudFront distribution
aws cloudfront create-distribution \
  --distribution-config file://cloudfront-config.json

# Cache static assets
# - Cache-Control: max-age=31536000 (1 year)
# - Gzip compression enabled
# - Minified CSS/JS
```

---

## SECURITY CHECKLIST

### Pre-Deployment
- [ ] Environment variables secured (.env not in git)
- [ ] Database password changed from default
- [ ] Redis password configured
- [ ] SSL certificate installed
- [ ] Security groups configured (least privilege)
- [ ] IAM roles configured
- [ ] Secrets stored in AWS Secrets Manager

### Post-Deployment
- [ ] HTTPS enforced (redirect HTTP to HTTPS)
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] DDoS protection enabled (AWS Shield)
- [ ] WAF rules configured
- [ ] Logging enabled
- [ ] Monitoring alerts configured
- [ ] Regular security audits scheduled

---

## TROUBLESHOOTING

### Service Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check port availability
lsof -i :8000
lsof -i :3000

# Restart services
docker-compose restart
```

### Database Connection Error

```bash
# Check database is running
aws rds describe-db-instances

# Test connection
psql -h your-rds-endpoint -U editor -d ai_video_editor

# Check security group
aws ec2 describe-security-groups --group-ids sg-12345
```

### Video Processing Fails

```bash
# Check FFmpeg installation
ffmpeg -version

# Check disk space
df -h

# Check Celery worker
docker-compose logs celery

# Check Redis connection
redis-cli ping
```

---

## ROLLBACK PROCEDURE

```bash
# Rollback to previous ECS task definition
aws ecs update-service \
  --cluster ai-video-editor \
  --service backend \
  --task-definition ai-video-editor-backend:previous-version

# Rollback database
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ai-video-editor-db-restored \
  --db-snapshot-identifier ai-video-editor-backup-20241226

# Verify rollback
aws ecs describe-services --cluster ai-video-editor --services backend
```

---

## COST OPTIMIZATION

### Estimated Monthly Costs

```
EC2 (t3.large, 730 hours): $60
RDS (db.t3.micro, 730 hours): $30
ElastiCache (cache.t3.micro): $15
S3 (100GB storage): $2.30
Data transfer (100GB): $9.20
CloudFront (100GB): $8.50
Total: ~$125/month
```

### Cost Reduction Tips
1. Use Reserved Instances (save 30-40%)
2. Use Spot Instances for Celery workers
3. Archive old videos to Glacier
4. Compress videos before storage
5. Use CloudFront for CDN (reduce data transfer)

---

**Document Version:** 1.0  
**Created:** December 26, 2024  
**Status:** Ready for Implementation
