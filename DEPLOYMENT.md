# Deployment Guide

This guide covers deploying the Zenafide HR AI Tool to production environments.

## Prerequisites

- Airtable account with API access
- OpenAI API key
- Node.js 18+ and Python 3.8+
- Domain name (optional, for custom domains)

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_base_id
OPENAI_API_KEY=your_openai_api_key

# Airtable Tables
AIRTABLE_TABLE_CANDIDATES=Candidates
AIRTABLE_TABLE_APPLICATIONS=Applications

# OpenAI Configuration
EMBEDDING_MODEL=text-embedding-3-small

# Application Settings
MAX_RESULTS=20
INTENT_CAP=5
RELEVANCE_ALPHA=0.6
FINAL_SCORE_WEIGHT=0.4

# Optional: Agent Features
PHIDATA_ENABLED=true
AGENT_MODEL=gpt-4o
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

## Deployment Options

### Option 1: Docker Deployment

1. **Build Docker Images**

```bash
# Backend
cd backend
docker build -t zenafide-backend .

# Frontend
cd ../frontend
docker build -t zenafide-frontend .
```

2. **Docker Compose**

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  backend:
    image: zenafide-backend
    ports:
      - "8000:8000"
    environment:
      - AIRTABLE_API_KEY=${AIRTABLE_API_KEY}
      - AIRTABLE_BASE_ID=${AIRTABLE_BASE_ID}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped

  frontend:
    image: zenafide-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

3. **Run with Docker Compose**

```bash
docker-compose up -d
```

### Option 2: Cloud Platform Deployment

#### Vercel (Frontend) + Railway (Backend)

**Backend on Railway:**

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push

**Frontend on Vercel:**

1. Connect repository to Vercel
2. Set `NEXT_PUBLIC_API_URL` to your Railway backend URL
3. Deploy automatically on push

#### AWS Deployment

**Backend (AWS Lambda + API Gateway):**

1. Use AWS SAM or Serverless Framework
2. Configure environment variables in Lambda
3. Set up API Gateway for routing

**Frontend (AWS S3 + CloudFront):**

1. Build static files: `npm run build && npm run export`
2. Upload to S3 bucket
3. Configure CloudFront distribution

### Option 3: Traditional VPS Deployment

**Backend Setup:**

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nginx

# Setup application
git clone your-repo
cd zenafide-hr-tool/backend
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/zenafide-backend.service
```

Service file content:

```ini
[Unit]
Description=Zenafide Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/path/to/zenafide-hr-tool/backend
Environment=PATH=/usr/bin/python3
ExecStart=/usr/bin/python3 -m uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend Setup:**

```bash
# Build frontend
cd ../frontend
npm install
npm run build

# Setup Nginx
sudo nano /etc/nginx/sites-available/zenafide
```

Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Security Considerations

### API Security

1. **Rate Limiting**: Implement rate limiting for API endpoints
2. **CORS**: Configure CORS properly for production domains
3. **HTTPS**: Always use HTTPS in production
4. **API Keys**: Store API keys securely, never in code

### Data Security

1. **Encryption**: Ensure data is encrypted in transit and at rest
2. **Access Control**: Implement proper authentication/authorization
3. **Data Privacy**: Follow GDPR/privacy regulations for candidate data
4. **Backup**: Regular backups of Airtable data

## Monitoring and Logging

### Application Monitoring

1. **Health Checks**: Implement health check endpoints
2. **Error Tracking**: Use services like Sentry for error monitoring
3. **Performance**: Monitor API response times and throughput
4. **Uptime**: Set up uptime monitoring

### Logging

```python
# Add to backend/app.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Scaling Considerations

### Backend Scaling

1. **Horizontal Scaling**: Deploy multiple backend instances
2. **Load Balancing**: Use load balancer for traffic distribution
3. **Caching**: Implement Redis for caching embeddings
4. **Database**: Consider moving to dedicated database for high volume

### Frontend Scaling

1. **CDN**: Use CDN for static assets
2. **Edge Deployment**: Deploy to edge locations
3. **Caching**: Implement proper caching strategies

## Backup and Recovery

### Data Backup

1. **Airtable**: Regular exports of candidate data
2. **Configuration**: Backup environment variables and configs
3. **Code**: Ensure code is in version control

### Recovery Plan

1. **RTO/RPO**: Define recovery time and point objectives
2. **Procedures**: Document recovery procedures
3. **Testing**: Regular disaster recovery testing

## Cost Optimization

### API Costs

1. **OpenAI**: Monitor embedding API usage
2. **Airtable**: Optimize API calls and caching
3. **Infrastructure**: Right-size compute resources

### Monitoring Costs

1. **Usage Tracking**: Track API usage and costs
2. **Alerts**: Set up cost alerts
3. **Optimization**: Regular cost optimization reviews

## Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS configuration
2. **API Rate Limits**: Implement retry logic
3. **Memory Issues**: Monitor memory usage
4. **Slow Queries**: Optimize database queries

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=DEBUG
```

## Support and Maintenance

### Regular Maintenance

1. **Updates**: Keep dependencies updated
2. **Security**: Regular security audits
3. **Performance**: Monitor and optimize performance
4. **Backups**: Verify backup integrity

### Support Channels

1. **Documentation**: Keep documentation updated
2. **Monitoring**: Set up alerting for issues
3. **Logs**: Centralized logging for troubleshooting
