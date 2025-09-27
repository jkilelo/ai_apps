#!/bin/bash
# VM RECOVERY SCRIPT - Undo Extreme Optimizations
# Run this in recovery mode to restore system functionality

echo "==================================="
echo "VM RECOVERY SCRIPT - STARTING"
echo "==================================="
echo ""

# Mount filesystem as read-write if in recovery mode
mount -o remount,rw /

# 1. RESTORE CRITICAL KERNEL PARAMETERS
echo "Restoring safe kernel parameters..."
cat > /etc/sysctl.d/99-recovery.conf <<'EOF'
# Safe recovery settings
vm.swappiness = 60
vm.vfs_cache_pressure = 100
vm.dirty_ratio = 20
vm.dirty_background_ratio = 10
vm.overcommit_memory = 0
kernel.randomize_va_space = 2
kernel.yama.ptrace_scope = 1
kernel.kptr_restrict = 1
kernel.dmesg_restrict = 1
net.ipv6.conf.all.disable_ipv6 = 0
net.ipv6.conf.default.disable_ipv6 = 0
net.ipv6.conf.lo.disable_ipv6 = 0
EOF

# Remove the extreme optimization config
rm -f /etc/sysctl.d/99-extreme-optimization.conf
rm -f /etc/sysctl.d/01-swap-optimization.conf
rm -f /etc/sysctl.d/02-scheduler.conf
rm -f /etc/sysctl.d/03-netfilter.conf

# Apply safe settings
sysctl -p /etc/sysctl.d/99-recovery.conf 2>/dev/null || true

# 2. RE-ENABLE CRITICAL SERVICES
echo "Re-enabling critical system services..."

# Unmask all services that were masked
for service in $(systemctl list-unit-files | grep masked | awk '{print $1}'); do
    systemctl unmask $service 2>/dev/null || true
done

# Enable critical services
CRITICAL_SERVICES="
systemd-resolved
systemd-networkd
NetworkManager
systemd-journald
systemd-logind
systemd-timesyncd
ssh
sshd
"

for service in $CRITICAL_SERVICES; do
    echo "Enabling $service..."
    systemctl unmask $service 2>/dev/null || true
    systemctl enable $service 2>/dev/null || true
done

# 3. RESTORE SYSTEMD JOURNAL CONFIGURATION
echo "Restoring systemd journal configuration..."
rm -f /etc/systemd/journald.conf.d/01-minimal.conf
cat > /etc/systemd/journald.conf.d/99-recovery.conf <<'EOF'
[Journal]
Storage=persistent
SystemMaxUse=100M
RuntimeMaxUse=100M
ForwardToSyslog=yes
EOF

# 4. RESTORE NETWORK CONFIGURATION
echo "Restoring network configuration..."
rm -f /etc/systemd/network/10-optimize.network

# Ensure NetworkManager or systemd-networkd is configured properly
if [ -f /etc/netplan/50-cloud-init.yaml ]; then
    # Digital Ocean typically uses netplan
    echo "Restoring netplan configuration..."
    cat > /etc/netplan/50-cloud-init.yaml <<'EOF'
network:
    version: 2
    ethernets:
        eth0:
            dhcp4: true
            dhcp6: false
EOF
    netplan generate 2>/dev/null || true
    netplan apply 2>/dev/null || true
fi

# 5. FIX SWAP CONFIGURATION
echo "Fixing swap configuration..."
# Remove bad swap entries
sed -i '/swapfile/d' /etc/fstab
# Re-create proper swap
if [ -f /swapfile ]; then
    swapoff /swapfile 2>/dev/null || true
    rm -f /swapfile
fi
# Create reasonable swap (512MB for 1GB VM)
dd if=/dev/zero of=/swapfile bs=1M count=512 2>/dev/null
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap defaults 0 0' >> /etc/fstab

# 6. REMOVE PROBLEMATIC OPTIMIZATIONS
echo "Removing problematic optimization scripts..."
rm -f /usr/local/bin/smart-extreme-optimize
rm -f /usr/local/bin/clear-memory
rm -f /usr/local/bin/vm-maintain
rm -f /etc/systemd/system/cpu-performance.service
rm -f /etc/systemd/system/ksm.service

# 7. RESTORE APT FUNCTIONALITY
echo "Restoring package management..."
mkdir -p /var/lib/apt/lists
apt-get update 2>/dev/null || true

# 8. CLEAR AND RESET SYSTEMD
echo "Resetting systemd state..."
systemctl daemon-reexec
systemctl daemon-reload

# 9. ENSURE SSH ACCESS
echo "Ensuring SSH access..."
# Make sure SSH is configured properly
if [ -f /etc/ssh/sshd_config ]; then
    sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
    sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
fi

# 10. CLEAN UP CRON JOBS
echo "Cleaning up cron jobs..."
crontab -l 2>/dev/null | grep -v vm-maintain | crontab - 2>/dev/null || true

# 11. FINAL CLEANUP
echo "Performing final cleanup..."
sync
echo 3 > /proc/sys/vm/drop_caches

echo ""
echo "==================================="
echo "RECOVERY COMPLETE!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Reboot the system: 'reboot'"
echo "2. After reboot, verify SSH access"
echo "3. Check system status: 'systemctl status'"
echo "4. Monitor system: 'journalctl -f'"
echo ""
echo "If system still won't boot normally:"
echo "- Try Digital Ocean's recovery ISO"
echo "- Consider rebuilding the droplet from a snapshot"
echo ""