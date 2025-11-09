# Production Deployment Guide

Complete guide for deploying Ollama Chatbot in production environments.

---

## 🚀 Deployment Options

1. [Docker Deployment](#docker-deployment) - Recommended for most cases
2. [Linux systemd Services](#linux-systemd-deployment) - Native Linux deployment
3. [Manual Deployment](#manual-deployment) - Custom configurations

---

## 🐳 Docker Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 15GB free disk space

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/fouada/Assignment1_Ollama_Chatbot.git
cd Assignment1_Ollama_Chatbot

# 2. Build and start services
docker-compose up -d --build

# 3. View logs
docker-compose logs -f

# 4. Access services
# Streamlit UI:  http://localhost:8501
# Flask API:     http://localhost:5000
# Ollama API:    http://localhost:11434
```

### Configuration

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - LOG_LEVEL=INFO  # Change to DEBUG, WARNING, or ERROR
  - OLLAMA_HOST=0.0.0.0
  - TZ=America/New_York  # Set your timezone
```

### Resource Limits

Adjust based on your hardware:

```yaml
deploy:
  resources:
    limits:
      cpus: '8.0'  # Use more CPUs if available
      memory: 16G  # Increase for larger models
```

### Management Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]

# Pull new models
docker-compose exec ollama-chatbot ollama pull mistral

# List models
docker-compose exec ollama-chatbot ollama list

# Shell access
docker-compose exec ollama-chatbot bash

# Remove everything (including volumes)
docker-compose down -v
```

---

## 🐧 Linux systemd Deployment

### Prerequisites
- Linux system (Ubuntu, Debian, RHEL, etc.)
- systemd init system
- Python 3.10+
- Ollama installed

### Installation Steps

```bash
# 1. Create application user
sudo useradd -r -s /bin/bash -d /opt/ollama-chatbot -m ollama

# 2. Clone repository
sudo git clone https://github.com/fouada/Assignment1_Ollama_Chatbot.git /opt/ollama-chatbot

# 3. Set permissions
sudo chown -R ollama:ollama /opt/ollama-chatbot

# 4. Setup virtual environment (as ollama user)
sudo -u ollama bash -c "cd /opt/ollama-chatbot && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"

# 5. Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# 6. Pull models
sudo -u ollama ollama pull llama3.2

# 7. Copy systemd service files
sudo cp /opt/ollama-chatbot/ollama-chatbot-*.service /etc/systemd/system/

# 8. Reload systemd
sudo systemctl daemon-reload

# 9. Enable services
sudo systemctl enable ollama-chatbot-streamlit
sudo systemctl enable ollama-chatbot-flask

# 10. Start services
sudo systemctl start ollama-chatbot-streamlit
sudo systemctl start ollama-chatbot-flask
```

### Service Management

```bash
# Check status
sudo systemctl status ollama-chatbot-streamlit
sudo systemctl status ollama-chatbot-flask

# Start services
sudo systemctl start ollama-chatbot-streamlit
sudo systemctl start ollama-chatbot-flask

# Stop services
sudo systemctl stop ollama-chatbot-streamlit
sudo systemctl stop ollama-chatbot-flask

# Restart services
sudo systemctl restart ollama-chatbot-streamlit
sudo systemctl restart ollama-chatbot-flask

# View logs
sudo journalctl -u ollama-chatbot-streamlit -f
sudo journalctl -u ollama-chatbot-flask -f

# Disable services
sudo systemctl disable ollama-chatbot-streamlit
sudo systemctl disable ollama-chatbot-flask
```

### Troubleshooting systemd

```bash
# Check service status
sudo systemctl status ollama-chatbot-streamlit

# View recent logs
sudo journalctl -u ollama-chatbot-streamlit -n 50

# Check for errors
sudo journalctl -u ollama-chatbot-streamlit -p err

# Verify permissions
ls -la /opt/ollama-chatbot/logs/
```

---

## ⚙️ Manual Deployment

### Setup Process

```bash
# 1. Clone repository
git clone https://github.com/fouada/Assignment1_Ollama_Chatbot.git
cd Assignment1_Ollama_Chatbot

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Ollama
ollama serve &

# 5. Pull models
ollama pull llama3.2

# 6. Start Flask API (background)
nohup python apps/app_flask.py > logs/flask_app.log 2>&1 &

# 7. Start Streamlit UI (background)
nohup streamlit run apps/app_streamlit.py --server.port=8501 > logs/streamlit_app.log 2>&1 &
```

---

## 🔒 Security Considerations

### Production Checklist

- [ ] Use HTTPS with reverse proxy (nginx/Apache)
- [ ] Enable authentication (Flask-HTTPAuth)
- [ ] Configure firewall rules
- [ ] Set up log rotation
- [ ] Enable audit logging
- [ ] Use secrets management (not hardcoded)
- [ ] Regular security updates
- [ ] Monitor resource usage

### Reverse Proxy Configuration (nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Streamlit UI
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Flask API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 Monitoring & Logging

### Log Files

```
logs/
├── flask_app.log      # Flask API logs
└── streamlit_app.log  # Streamlit UI logs
```

### Log Rotation

Create `/etc/logrotate.d/ollama-chatbot`:

```
/opt/ollama-chatbot/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ollama ollama
}
```

### Health Monitoring

```bash
# Check Flask API health
curl http://localhost:5000/health

# Monitor with script
watch -n 5 'curl -s http://localhost:5000/health | jq'
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Docker deployment
cd Assignment1_Ollama_Chatbot
git pull origin main
docker-compose down
docker-compose up -d --build

# systemd deployment
cd /opt/ollama-chatbot
sudo -u ollama git pull origin main
sudo -u ollama bash -c "source .venv/bin/activate && pip install -r requirements.txt --upgrade"
sudo systemctl restart ollama-chatbot-streamlit
sudo systemctl restart ollama-chatbot-flask
```

### Update Models

```bash
# Docker
docker-compose exec ollama-chatbot ollama pull llama3.2

# systemd/manual
ollama pull llama3.2
```

---

## 🐛 Troubleshooting Production Issues

### Service Won't Start

```bash
# Check logs
docker-compose logs
# OR
sudo journalctl -u ollama-chatbot-streamlit -n 100

# Common issues:
# - Port already in use: Change port in configuration
# - Insufficient memory: Increase resources or use smaller model
# - Ollama not running: Start Ollama service first
```

### High Memory Usage

```bash
# Check memory usage
docker stats
# OR
htop

# Solutions:
# - Use smaller models (phi3 instead of mistral)
# - Limit Docker resources in docker-compose.yml
# - Restart services to clear memory
```

### Slow Performance

```bash
# Check CPU usage
docker stats
# OR
top

# Solutions:
# - Increase CPU allocation
# - Use GPU if available
# - Lower temperature parameter
# - Use smaller models
```

---

## 📚 Additional Resources

- [README.md](../README.md) - Main documentation
- [TESTING.md](TESTING.md) - Testing guide
- [API.md](API.md) - API documentation
- [PRD.md](PRD.md) - Product requirements

---

**Last Updated**: November 2025  
**Maintainers**: Fouad Azem, Tal Goldengorn

