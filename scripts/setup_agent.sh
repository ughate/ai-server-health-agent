
#!/bin/bash
# ============================================================
# Agent Setup Script - Install all dependencies
# ============================================================

set -e

echo "=========================================="
echo "  Setting Up AI Server Health Agent"
echo "=========================================="

# Install Python and pip
echo "[1/4] Installing Python and pip..."
sudo yum install -y python3-pip git

# Install Python packages
echo "[2/4] Installing Python packages..."
pip install boto3 ansible requests langchain langchain-community langchain-core python-dotenv

# Generate SSH key for Ansible
echo "[3/4] Generating SSH key..."
if [ ! -f ~/.ssh/agent_key ]; then
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/agent_key -N ""
    echo ""
    echo "SSH key generated. Copy to target servers with:"
    echo "  ssh-copy-id -i ~/.ssh/agent_key.pub ec2-user@<TARGET_SERVER_IP>"
    echo ""
    echo "Public key:"
    cat ~/.ssh/agent_key.pub
else
    echo "SSH key already exists at ~/.ssh/agent_key"
fi

# Create project structure
echo "[4/4] Creating project structure..."
mkdir -p ansible scripts docs

echo ""
echo "=========================================="
echo "  ✅ Agent Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit ansible/inventory.yml with your server IPs"
echo "  2. Copy SSH key to target servers"
echo "  3. Test: ansible all -i ansible/inventory.yml -m ping"
echo "  4. Run: python3 health_agent.py"


