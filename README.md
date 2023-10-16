
# API Monitoring

API Monitoring provides a tool to monitor your API's availability and notify in case of its downtime or other issues.

## Features
- Checks API availability.
- Sends alerts to Telegram upon detecting issues.
- Traces using `mtr` when the API is down.
- Auto-resolves alerts when the issue is fixed.

## Getting Started

### Installing Dependencies

1. Install the required Python libraries from `requirements.txt`:
```
sudo pip3 install -r requirements.txt
```

2. Install the `mtr` tracing tool:
- On Ubuntu/Debian:
```
sudo apt-get install mtr
```
- On CentOS:
```
sudo yum install mtr
```

### Configuration

1. Copy the example configuration file:
```
cp .env.example .env
```

2. Open `.env` in a text editor and provide the required parameters.

### Running

To run the script, execute:
```
sudo python3 main.py
```

### Adding to systemd

To automatically start the script on system boot and ensure it runs continuously, you can add it as a systemd service.

1. Create a systemd service file:
```
sudo nano /etc/systemd/system/api-monitoring.service
```

2. Add the following content, replacing `/path/to/your/script` with the actual path to your script:
```
[Unit]
Description=API Monitoring Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/path/to/your/script
ExecStart=/usr/bin/python3 /path/to/your/script/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Reload systemd and start the service:
```
sudo systemctl daemon-reload
sudo systemctl start api-monitoring
```

4. To have the service start automatically on system boot:
```
sudo systemctl enable api-monitoring
```

---

You now have an updated and detailed README for your project.
