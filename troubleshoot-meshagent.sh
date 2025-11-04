#!/bin/bash

echo "=== MeshCentral Agent Troubleshooting ==="
echo ""

echo "1. Checking agent service status..."
sudo systemctl status meshagent --no-pager -l

echo ""
echo "2. Checking if agent process is running..."
ps aux | grep meshagent | grep -v grep

echo ""
echo "3. Checking agent log file location..."
if [ -f /usr/local/mesh_services/meshagent/meshagent.log ]; then
    echo "✓ Log file exists at /usr/local/mesh_services/meshagent/meshagent.log"
    echo ""
    echo "Last 30 lines of agent log:"
    sudo tail -30 /usr/local/mesh_services/meshagent/meshagent.log
elif [ -f /usr/local/mesh/meshagent.log ]; then
    echo "✓ Log file exists at /usr/local/mesh/meshagent.log"
    echo ""
    echo "Last 30 lines of agent log:"
    sudo tail -30 /usr/local/mesh/meshagent.log
else
    echo "✗ Agent log file not found in standard locations"
fi

echo ""
echo "4. Checking network connectivity to server..."
if curl -I https://tee.up.railway.app 2>&1 | head -5; then
    echo "✓ Can reach server"
else
    echo "✗ Cannot reach server"
fi

echo ""
echo "5. Checking agent configuration..."
if [ -f /usr/local/mesh_services/meshagent/meshagent.msh ]; then
    echo "✓ Configuration file exists"
    echo "File size:" $(ls -lh /usr/local/mesh_services/meshagent/meshagent.msh | awk '{print $5}')
elif [ -f /usr/local/mesh/meshagent.msh ]; then
    echo "✓ Configuration file exists"
    echo "File size:" $(ls -lh /usr/local/mesh/meshagent.msh | awk '{print $5}')
fi

echo ""
echo "6. Checking firewall status..."
if command -v ufw &> /dev/null; then
    sudo ufw status | head -10
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --list-all | head -10
else
    echo "No ufw or firewalld detected"
fi

echo ""
echo "7. Checking all agent logs (systemd journal)..."
sudo journalctl -u meshagent -n 100 --no-pager

echo ""
echo "=== Troubleshooting Complete ==="
