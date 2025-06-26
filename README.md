
<div align="center">

# 🚀 API Monitoring

[![CI](https://github.com/dkamenkov/api-monitoring/workflows/CI/badge.svg)](https://github.com/dkamenkov/api-monitoring/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/dkamenkov/api-monitoring/branch/main/graph/badge.svg)](https://codecov.io/gh/dkamenkov/api-monitoring)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://hub.docker.com/r/dkamenkov/api-monitoring)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**A modern, asynchronous tool for monitoring AWS-compatible APIs and sending intelligent alerts when issues are detected.**

[Features](#-features) •
[Quick Start](#-quick-start) •
[Documentation](#-documentation) •
[Contributing](#-contributing) •
[License](#-license)

</div>

## ✨ Features

- 🚀 **Asynchronous Architecture**: Built with asyncio and aiohttp for efficient, non-blocking operations
- ☁️ **AWS-Compatible API Monitoring**: Monitors the availability of AWS-compatible APIs
- 🔧 **Maintenance Mode Detection**: Skips checks when the API is in maintenance mode
- 🤖 **Intelligent Alerting**: Sends detailed alerts to Telegram with MTR traces when issues are detected
- 💬 **Custom Alert Comments**: Add optional comments to alerts for additional context
- ✅ **Auto-Resolution**: Automatically sends resolution notifications when issues are fixed
- 📊 **Structured Logging**: JSON-formatted logs for better analysis
- 🐳 **Containerized Deployment**: Docker and Docker Compose support for easy deployment
- ⚙️ **Configuration Validation**: Pydantic-based settings with validation
- 🏗️ **Modular Design**: Well-organized code structure for maintainability

## 🏗️ Architecture

The application is structured as a Python package with the following components:

- ⚙️ **Configuration**: Environment-based settings with validation
- 📝 **Logging**: Structured JSON logging
- ☁️ **AWS Client**: Asynchronous AWS API client
- 🔧 **Maintenance Checker**: Checks if the API is in maintenance mode
- 🌐 **Network Utilities**: Functions for network operations like MTR traces
- 📢 **Alerting**: Telegram-based alerting system
- 👁️ **Monitoring**: Core monitoring logic
- 🚀 **Main**: Entry point for the application

The main entry point is now located inside the api_monitoring package, making the project structure more modular and maintainable.

## 🚀 Quick Start

Get up and running in minutes with Docker:

```bash
# Clone the repository
git clone https://github.com/dkamenkov/api-monitoring.git
cd api-monitoring

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your settings

# Run with Docker Compose
docker-compose up -d
```

That's it! Your API monitoring is now running. Check the logs with:
```bash
docker-compose logs -f
```

## 📦 Installation

### 📋 Prerequisites

- 🐍 Python 3.13+
- 🌐 MTR (My Traceroute) tool

### Option 1: 🐍 Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/dkamenkov/api-monitoring.git
cd api-monitoring
```

2. Install the required Python libraries:
```bash
pip install -r requirements.txt
```

3. Install the MTR tool:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install mtr
     ```
   - On CentOS:
     ```bash
     sudo yum install mtr
     ```

### Option 2: 🐳 Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/dkamenkov/api-monitoring.git
cd api-monitoring
```

2. Build and run with Docker Compose:
```bash
docker-compose up -d
```

## ⚙️ Configuration

1. Copy the example configuration file:
```bash
cp .env.example .env
```

2. Edit the `.env` file with your settings:
```
# API Endpoint Configuration
ENDPOINT_URL=your_api_endpoint_here

# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_DEFAULT_REGION=your_default_region

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Optional Settings
CHECK_INTERVAL=60
API_TIMEOUT=15
MAINTENANCE_CHECK_TIMEOUT=10
LOG_LEVEL=INFO
```

## 🚀 Running

### 🐍 Standard Method

```bash
python -m api_monitoring.main
```

### 🐳 Docker Method

```bash
docker-compose up -d
```

### 🔧 Systemd Service

To run as a systemd service:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/api-monitoring.service
```

2. Add the following content:
```
[Unit]
Description=API Monitoring Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/api-monitoring
ExecStart=/usr/bin/python3 -m api_monitoring.main
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable api-monitoring
sudo systemctl start api-monitoring
```

## 📊 Logs

Logs are written to `logs.log` in the project directory and to stdout in JSON format when running locally. When running with Docker, logs are output only to stdout in JSON format for better container log management.

## 🤝 Contributing

We love contributions! Please read our [Contributing Guide](CONTRIBUTING.md) to get started.

### 🐛 Found a Bug?

Please [open an issue](https://github.com/dkamenkov/api-monitoring/issues/new?template=bug_report.md) with details about the bug.

### 💡 Have an Idea?

We'd love to hear about it! [Open a feature request](https://github.com/dkamenkov/api-monitoring/issues/new?template=feature_request.md).

### 🔒 Security

Please review our [Security Policy](SECURITY.md) for reporting security vulnerabilities.

## 📈 Roadmap

- [ ] Web dashboard for monitoring status
- [ ] Support for multiple notification channels (Slack, Discord, Email)
- [ ] Prometheus metrics export
- [ ] Custom health check endpoints
- [ ] Multi-region monitoring
- [ ] Advanced alerting rules and conditions

## 🙏 Acknowledgments

- Built with [aiohttp](https://aiohttp.readthedocs.io/) for async HTTP operations
- Uses [aiobotocore](https://aiobotocore.readthedocs.io/) for AWS API interactions
- Configuration management with [Pydantic](https://pydantic-docs.helpmanual.io/)
- Network tracing powered by [MTR](https://www.bitwizard.nl/mtr/)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**⭐ Star this repository if you find it useful! ⭐**

Made with ❤️ by the API Monitoring team

</div>
