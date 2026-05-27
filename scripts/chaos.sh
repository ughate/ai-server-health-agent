
#!/bin/bash
# ============================================================
# Chaos Testing Script
# Run this on TARGET servers to simulate failures
# ============================================================

echo "💥 Creating chaos for testing..."
echo ""

# Stop nginx service
echo "[1/3] Stopping nginx..."
sudo systemctl stop nginx 2>/dev/null && echo "  ✅ nginx stopped" || {
    echo "  ⚠️  nginx not installed, installing first..."
    sudo yum install -y nginx
    sudo systemctl start nginx
    sudo systemctl stop nginx
    echo "  ✅ nginx installed and stopped"
}

# Fill disk space (writes to root filesystem, not tmpfs)
echo "[2/3] Filling disk space to ~90%..."
sudo fallocate -l 85G /root/disk_filler.img 2>/dev/null && \
    echo "  ✅ Disk filled (~90%)" || \
    echo "  ⚠️  Could not fill disk completely"

# Create high memory usage
echo "[3/3] Creating memory pressure..."
if ! command -v stress &> /dev/null; then
    sudo yum install -y stress 2>/dev/null || {
        sudo yum install -y epel-release 2>/dev/null
        sudo yum install -y stress
    }
fi
stress --vm 1 --vm-bytes 256M --timeout 600s &
echo "  ✅ Memory stress started (10 minutes)"

echo ""
echo "=========================================="
echo "  💥 Chaos Created! The agent should detect:"
echo "    - nginx service is DOWN"
echo "    - Disk usage is HIGH (~90%)"
echo "    - Memory usage is HIGH"
echo "=========================================="
echo ""
echo "To undo all chaos:"
echo "  sudo rm /root/disk_filler.img"
echo "  killall stress"
echo "  sudo systemctl start nginx"
