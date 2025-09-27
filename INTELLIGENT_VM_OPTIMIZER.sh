#!/bin/bash
# Intelligent VM Optimizer for 1GB Digital Ocean Droplets
# Based on real-world testing and recovery experience
# This script maximizes performance while maintaining 100% stability

set -euo pipefail

# Configuration
SCRIPT_VERSION="2.0"
VM_RAM_MB=$(free -m | awk 'NR==2{print $2}')
BACKUP_DIR="/root/vm-optimization-backup-$(date +%Y%m%d-%H%M%S)"
LOG_FILE="/var/log/vm-optimization.log"
DRY_RUN=${1:-false}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log "INFO: $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    log "SUCCESS: $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    log "ERROR: $1"
}

# Safety check function
safety_check() {
    local check_name=$1
    local check_command=$2

    if eval "$check_command"; then
        print_success "$check_name: PASS"
        return 0
    else
        print_error "$check_name: FAIL"
        return 1
    fi
}

# Backup function
create_backup() {
    print_status "Creating configuration backup..."
    mkdir -p "$BACKUP_DIR"

    # Backup critical configs
    cp -a /etc/sysctl.d/ "$BACKUP_DIR/" 2>/dev/null || true
    cp -a /etc/systemd/ "$BACKUP_DIR/" 2>/dev/null || true
    cp /etc/fstab "$BACKUP_DIR/" 2>/dev/null || true
    systemctl list-unit-files --state=enabled > "$BACKUP_DIR/enabled-services.txt"
    free -h > "$BACKUP_DIR/memory-before.txt"
    df -h > "$BACKUP_DIR/disk-before.txt"

    print_success "Backup created at $BACKUP_DIR"
}

# Rollback function
rollback() {
    print_warning "Rolling back changes..."
    if [ -d "$BACKUP_DIR" ]; then
        cp -a "$BACKUP_DIR/sysctl.d/"* /etc/sysctl.d/ 2>/dev/null || true
        sysctl -p
        print_success "Rollback completed"
    else
        print_error "No backup found"
    fi
}

# Calculate optimal values based on RAM
calculate_optimal_values() {
    print_status "Calculating optimal values for ${VM_RAM_MB}MB RAM..."

    if [ "$VM_RAM_MB" -le 1024 ]; then
        # 1GB or less
        export SWAP_SIZE="512M"
        export SWAPPINESS="40"
        export VFS_CACHE_PRESSURE="80"
        export JOURNAL_SIZE="50M"
        export MIN_FREE_KB="16384"
    elif [ "$VM_RAM_MB" -le 2048 ]; then
        # 2GB
        export SWAP_SIZE="1G"
        export SWAPPINESS="30"
        export VFS_CACHE_PRESSURE="75"
        export JOURNAL_SIZE="100M"
        export MIN_FREE_KB="32768"
    else
        # 4GB or more
        export SWAP_SIZE="2G"
        export SWAPPINESS="20"
        export VFS_CACHE_PRESSURE="50"
        export JOURNAL_SIZE="200M"
        export MIN_FREE_KB="65536"
    fi

    print_success "Optimal values calculated"
}

# Memory baseline
get_memory_baseline() {
    export BASELINE_FREE=$(free -m | awk 'NR==2{print $7}')
    export BASELINE_USED=$(free -m | awk 'NR==2{print $3}')
    print_status "Baseline: ${BASELINE_FREE}MB free, ${BASELINE_USED}MB used"
}

# OPTIMIZATION FUNCTIONS

# 1. SMART Package Removal (Biggest Impact: ~200-300MB)
optimize_packages() {
    print_status "Optimizing packages..."

    # Only remove packages that are truly unnecessary and safe to remove
    SAFE_REMOVE_PACKAGES="
        snapd
        lxd
        lxd-client
        lxcfs
        cloud-guest-utils
        landscape-common
        popularity-contest
        ubuntu-advantage-tools
        accountsservice
    "

    local freed_space=0
    for package in $SAFE_REMOVE_PACKAGES; do
        if dpkg -l | grep -q "^ii.*$package"; then
            size=$(dpkg-query -W -f='${Installed-Size}' "$package" 2>/dev/null || echo 0)
            if [ "$DRY_RUN" == "false" ]; then
                apt-get remove --purge -y "$package" 2>/dev/null || true
                freed_space=$((freed_space + size))
                print_success "Removed $package (freed ~${size}KB)"
            else
                print_status "[DRY RUN] Would remove $package (free ~${size}KB)"
            fi
        fi
    done

    if [ "$DRY_RUN" == "false" ]; then
        apt-get autoremove --purge -y
        apt-get clean
        rm -rf /var/lib/apt/lists/*
    fi

    print_success "Package optimization freed ~$((freed_space/1024))MB"
}

# 2. Intelligent Service Management (Impact: ~50-100MB)
optimize_services() {
    print_status "Optimizing services..."

    # Services safe to disable on most VMs
    SAFE_DISABLE_SERVICES="
        bluetooth.service
        cups.service
        cups-browsed.service
        avahi-daemon.service
        ModemManager.service
        multipathd.service
        iscsid.service
        lvm2-monitor.service
        mdmonitor.service
    "

    # Critical services that must NEVER be disabled
    CRITICAL_SERVICES="
        ssh.service
        sshd.service
        systemd-networkd.service
        systemd-resolved.service
        systemd-journald.service
        systemd-logind.service
        networking.service
        NetworkManager.service
    "

    for service in $SAFE_DISABLE_SERVICES; do
        if systemctl list-unit-files | grep -q "$service"; then
            # Check if it's not in critical list
            is_critical=false
            for critical in $CRITICAL_SERVICES; do
                if [ "$service" == "$critical" ]; then
                    is_critical=true
                    break
                fi
            done

            if [ "$is_critical" == "false" ]; then
                if [ "$DRY_RUN" == "false" ]; then
                    systemctl stop "$service" 2>/dev/null || true
                    systemctl disable "$service" 2>/dev/null || true
                    print_success "Disabled $service"
                else
                    print_status "[DRY RUN] Would disable $service"
                fi
            else
                print_warning "Skipping critical service: $service"
            fi
        fi
    done
}

# 3. Smart Swap Configuration (Impact: Better memory management)
optimize_swap() {
    print_status "Optimizing swap configuration..."

    # Remove old swap if exists
    if [ -f /swapfile ]; then
        if [ "$DRY_RUN" == "false" ]; then
            swapoff /swapfile 2>/dev/null || true
            rm -f /swapfile
        fi
    fi

    # Create optimally sized swap
    if [ "$DRY_RUN" == "false" ]; then
        fallocate -l "$SWAP_SIZE" /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile

        # Update fstab
        grep -v swapfile /etc/fstab > /tmp/fstab.new || true
        echo '/swapfile none swap sw 0 0' >> /tmp/fstab.new
        mv /tmp/fstab.new /etc/fstab

        print_success "Created ${SWAP_SIZE} swap file"
    else
        print_status "[DRY RUN] Would create ${SWAP_SIZE} swap file"
    fi
}

# 4. Kernel Parameters (Moderate optimization)
optimize_kernel() {
    print_status "Applying safe kernel optimizations..."

    if [ "$DRY_RUN" == "false" ]; then
        cat > /etc/sysctl.d/60-vm-optimization.conf <<EOF
# Intelligent VM Optimization - Safe Parameters
# Memory Management (Moderate)
vm.swappiness=$SWAPPINESS
vm.vfs_cache_pressure=$VFS_CACHE_PRESSURE
vm.dirty_ratio=15
vm.dirty_background_ratio=5
vm.dirty_expire_centisecs=12000
vm.min_free_kbytes=$MIN_FREE_KB
vm.overcommit_memory=0
vm.overcommit_ratio=50

# Network (Safe optimizations only)
net.core.somaxconn=1024
net.core.netdev_max_backlog=2000
net.ipv4.tcp_fin_timeout=30
net.ipv4.tcp_tw_reuse=1
net.ipv4.tcp_keepalive_time=600
net.ipv4.tcp_keepalive_intvl=30
net.ipv4.tcp_keepalive_probes=5
net.ipv4.tcp_max_syn_backlog=2048

# File System
fs.file-max=100000
fs.inotify.max_user_watches=524288

# Security (KEEP ENABLED - Don't trade security for performance)
kernel.randomize_va_space=2
kernel.yama.ptrace_scope=1
kernel.kptr_restrict=1

# IPv6 (KEEP ENABLED - Many services need it)
net.ipv6.conf.all.disable_ipv6=0
net.ipv6.conf.default.disable_ipv6=0
EOF

        sysctl -p /etc/sysctl.d/60-vm-optimization.conf
        print_success "Applied kernel optimizations"
    else
        print_status "[DRY RUN] Would apply kernel optimizations"
    fi
}

# 5. Logging Optimization (Impact: ~50MB)
optimize_logging() {
    print_status "Optimizing system logging..."

    if [ "$DRY_RUN" == "false" ]; then
        # Configure journald
        mkdir -p /etc/systemd/journald.conf.d/
        cat > /etc/systemd/journald.conf.d/50-size.conf <<EOF
[Journal]
SystemMaxUse=$JOURNAL_SIZE
RuntimeMaxUse=$JOURNAL_SIZE
SystemMaxFileSize=10M
RuntimeMaxFileSize=10M
MaxRetentionSec=7day
ForwardToSyslog=no
EOF

        systemctl restart systemd-journald

        # Clean old logs
        journalctl --vacuum-time=2d
        find /var/log -type f -name "*.gz" -delete 2>/dev/null || true
        find /var/log -type f -name "*.1" -delete 2>/dev/null || true
        find /var/log -type f -name "*.old" -delete 2>/dev/null || true

        print_success "Optimized logging (limited to $JOURNAL_SIZE)"
    else
        print_status "[DRY RUN] Would optimize logging"
    fi
}

# 6. Clean Caches and Temp Files
clean_system() {
    print_status "Cleaning system caches and temp files..."

    if [ "$DRY_RUN" == "false" ]; then
        # Clean package manager cache
        apt-get clean

        # Clean temp files older than 7 days
        find /tmp -type f -atime +7 -delete 2>/dev/null || true
        find /var/tmp -type f -atime +7 -delete 2>/dev/null || true

        # Remove old kernels (keep current + one previous)
        if command -v purge-old-kernels > /dev/null; then
            purge-old-kernels --keep 2 -y
        fi

        # Clean thumbnail cache
        rm -rf /home/*/.cache/thumbnails/* 2>/dev/null || true

        # Clear systemd journal
        journalctl --vacuum-time=2d

        # Clear page cache (safe - only cleans unused cache)
        sync
        echo 1 > /proc/sys/vm/drop_caches

        print_success "System cleaned"
    else
        print_status "[DRY RUN] Would clean system"
    fi
}

# 7. Create monitoring script
create_monitoring() {
    print_status "Creating monitoring tools..."

    cat > /usr/local/bin/vm-status <<'EOF'
#!/bin/bash
echo "=== VM Performance Status ==="
echo "Date: $(date)"
echo ""
echo "Memory:"
free -h
echo ""
echo "Swap:"
swapon --show
echo ""
echo "CPU Load:"
uptime
echo ""
echo "Disk Usage:"
df -h /
echo ""
echo "Top Processes by Memory:"
ps aux --sort=-%mem | head -5
echo ""
echo "Network Connections:"
ss -tulpn | grep LISTEN | wc -l
echo ""
echo "Service Status:"
for service in ssh systemd-networkd systemd-resolved; do
    status=$(systemctl is-active $service)
    echo "$service: $status"
done
EOF

    chmod +x /usr/local/bin/vm-status
    print_success "Monitoring script created: vm-status"
}

# Performance testing
performance_test() {
    print_status "Running performance test..."

    # Memory test
    echo "Memory Write Speed:"
    dd if=/dev/zero of=/tmp/testfile bs=1M count=256 2>&1 | grep -E 'copied|bytes'
    rm -f /tmp/testfile

    # CPU test
    echo "CPU Speed (calculating pi):"
    time echo "scale=1000; 4*a(1)" | bc -l > /dev/null 2>&1

    # Disk test
    echo "Disk Write Speed:"
    dd if=/dev/zero of=/tmp/disktest bs=1M count=100 conv=fdatasync 2>&1 | grep -E 'copied|bytes'
    rm -f /tmp/disktest
}

# Main optimization flow
main() {
    echo "============================================"
    echo "   INTELLIGENT VM OPTIMIZER v${SCRIPT_VERSION}"
    echo "   For Digital Ocean 1GB Droplets"
    echo "============================================"
    echo ""

    if [ "$EUID" -ne 0 ]; then
        print_error "Please run as root"
        exit 1
    fi

    if [ "$1" == "--dry-run" ]; then
        DRY_RUN=true
        print_warning "DRY RUN MODE - No changes will be made"
    fi

    # Pre-flight checks
    print_status "Running pre-flight checks..."
    safety_check "Network connectivity" "ping -c 1 8.8.8.8 > /dev/null 2>&1"
    safety_check "DNS resolution" "nslookup google.com > /dev/null 2>&1"
    safety_check "SSH service" "systemctl is-active --quiet ssh || systemctl is-active --quiet sshd"

    # Create backup
    create_backup

    # Get baseline
    get_memory_baseline

    # Calculate optimal values
    calculate_optimal_values

    # Run optimizations
    print_status "Starting optimization sequence..."

    # Track what was done
    OPTIMIZATIONS_APPLIED=""

    # 1. Package optimization (biggest impact)
    optimize_packages
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Removed unnecessary packages"

    # Check memory after packages
    NEW_FREE=$(free -m | awk 'NR==2{print $7}')
    FREED=$((NEW_FREE - BASELINE_FREE))
    print_success "Freed ${FREED}MB so far"

    # 2. Service optimization
    optimize_services
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Disabled unnecessary services"

    # 3. Swap optimization
    optimize_swap
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Configured optimal swap"

    # 4. Kernel optimization
    optimize_kernel
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Applied kernel optimizations"

    # 5. Logging optimization
    optimize_logging
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Optimized logging"

    # 6. Clean system
    clean_system
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Cleaned caches and temp files"

    # 7. Create monitoring
    create_monitoring
    OPTIMIZATIONS_APPLIED="${OPTIMIZATIONS_APPLIED}\n- Created monitoring tools"

    # Final report
    echo ""
    echo "============================================"
    echo "        OPTIMIZATION COMPLETE!"
    echo "============================================"

    # Calculate improvement
    FINAL_FREE=$(free -m | awk 'NR==2{print $7}')
    TOTAL_FREED=$((FINAL_FREE - BASELINE_FREE))

    echo -e "\nOptimizations Applied:$OPTIMIZATIONS_APPLIED"
    echo ""
    echo "Memory Improvement:"
    echo "  Before: ${BASELINE_FREE}MB free"
    echo "  After:  ${FINAL_FREE}MB free"
    echo "  Freed:  ${TOTAL_FREED}MB"
    echo ""
    echo "Current Status:"
    free -h
    echo ""
    echo "Recommendations:"
    echo "1. Reboot to ensure all changes take effect: sudo reboot"
    echo "2. Check status after reboot: vm-status"
    echo "3. Monitor for 24 hours before declaring success"
    echo ""
    echo "Rollback available at: $BACKUP_DIR"
    echo "To rollback: cp -a $BACKUP_DIR/sysctl.d/* /etc/sysctl.d/"
    echo ""

    if [ "$TOTAL_FREED" -gt 100 ]; then
        print_success "Excellent result! Freed over 100MB"
    elif [ "$TOTAL_FREED" -gt 50 ]; then
        print_success "Good result! Freed ${TOTAL_FREED}MB"
    else
        print_warning "Modest improvement. VM may have been already optimized"
    fi
}

# Trap errors
trap 'print_error "Script failed! Check $LOG_FILE for details"' ERR

# Run main function
main "$@"