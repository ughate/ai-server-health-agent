
#!/bin/bash
# ============================================================
# Ollama Installation Script for Amazon Linux 2023
# ============================================================

set -e

echo "=========================================="
echo "  Installing Ollama on EC2 Instance"
echo "=========================================="

# Update system
echo "[1/5] Updating system packages..."
sudo yum update -y

# Install Ollama
echo "[2/5] Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Enable and start Ollama service
echo "[3/5] Enabling Ollama service..."
sudo systemctl enable --now ollama

# Configure Ollama to listen on all interfaces
echo "[4/5] Configuring Ollama..."
sudo mkdir -p /etc/systemd/system/ollama.service.d/
cat << 'EOF' | sudo tee /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=0.0.0.0"
Environment="OLLAMA_KEEP_ALIVE=-1"
EOF

sudo systemctl daemon-reload
sudo systemctl restart ollama

# Pull the model
echo "[5/5] Pulling llama3 model..."
ollama pull llama3

echo ""
echo "=========================================="
echo "  ✅ Ollama Installation Complete!"
echo "=========================================="
echo ""
echo "Verify with:"
echo "  ollama list"
echo "  curl http://[IP_ADDRESS]:11434/api/tags"


