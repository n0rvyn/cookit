# Linux Inspection Checklist

This checklist defines all inspection items. Each item has a category, ID, severity, the command(s) to run, and what constitutes a finding.

## 1. Security

### SEC-001: SSH Configuration
- **Severity**: HIGH
- **Commands**:
  ```
  cat /etc/ssh/sshd_config
  ```
- **Findings**:
  - PermitRootLogin not set to "no"
  - PasswordAuthentication not set to "no"
  - PermitEmptyPasswords not set to "no"
  - Protocol not set to 2
  - MaxAuthTries > 5
  - X11Forwarding set to "yes"
  - AllowTcpForwarding set to "yes" (if not needed)

### SEC-002: SUID/SGID Files
- **Severity**: MEDIUM
- **Commands**:
  ```
  timeout 60 find / -maxdepth 5 -type f \( -perm -4000 -o -perm -2000 \) -exec ls -la {} \; 2>/dev/null | head -100
  ```
- **Findings**:
  - Unexpected SUID/SGID binaries outside standard paths
  - Custom scripts with SUID bit set

### SEC-003: User Account Audit
- **Severity**: HIGH
- **Commands**:
  ```
  cat /etc/passwd
  cat /etc/shadow 2>/dev/null || echo "NO_SHADOW_ACCESS"
  awk -F: '$3==0{print $1}' /etc/passwd
  awk -F: '($2==""){print $1}' /etc/shadow 2>/dev/null
  lastlog 2>/dev/null | head -50
  ```
- **Findings**:
  - Multiple UID 0 accounts (besides root)
  - Accounts with empty passwords
  - Accounts with no login history (dormant)
  - System accounts with login shells

### SEC-004: Sudo Configuration
- **Severity**: HIGH
- **Commands**:
  ```
  cat /etc/sudoers 2>/dev/null
  ls -la /etc/sudoers.d/ 2>/dev/null
  cat /etc/sudoers.d/* 2>/dev/null
  ```
- **Findings**:
  - NOPASSWD entries
  - Overly broad sudo rules (ALL=(ALL) ALL)
  - Writable sudoers files

### SEC-005: Firewall Status
- **Severity**: HIGH
- **Commands**:
  ```
  iptables -L -n 2>/dev/null || echo "NO_IPTABLES"
  nft list ruleset 2>/dev/null || echo "NO_NFTABLES"
  firewall-cmd --list-all 2>/dev/null || echo "NO_FIREWALLD"
  ufw status verbose 2>/dev/null || echo "NO_UFW"
  ```
- **Findings**:
  - No firewall active
  - Default ACCEPT policy on INPUT chain
  - No rules defined
  - Overly permissive rules (0.0.0.0/0 accept)

### SEC-006: SELinux/AppArmor Status
- **Severity**: MEDIUM
- **Commands**:
  ```
  getenforce 2>/dev/null || echo "NO_SELINUX"
  sestatus 2>/dev/null || echo "NO_SELINUX"
  aa-status 2>/dev/null || echo "NO_APPARMOR"
  ```
- **Findings**:
  - SELinux disabled or permissive
  - AppArmor not loaded or profiles in complain mode

### SEC-007: File Permissions
- **Severity**: MEDIUM
- **Commands**:
  ```
  timeout 60 find / -maxdepth 5 -type f -perm -0002 -not -path "/proc/*" -not -path "/sys/*" 2>/dev/null | head -50
  timeout 60 find / -maxdepth 5 -type d -perm -0002 -not -path "/proc/*" -not -path "/sys/*" -not -path "/tmp" -not -path "/var/tmp" 2>/dev/null | head -50
  ls -la /etc/passwd /etc/shadow /etc/group /etc/gshadow 2>/dev/null
  ls -la /etc/crontab /etc/cron.d/ 2>/dev/null
  ```
- **Findings**:
  - World-writable files outside /tmp, /var/tmp
  - Sensitive files with incorrect permissions (shadow readable, etc.)
  - Crontab files writable by non-root

### SEC-008: Password Policy
- **Severity**: MEDIUM
- **Commands**:
  ```
  cat /etc/login.defs | grep -E "^(PASS_MAX_DAYS|PASS_MIN_DAYS|PASS_MIN_LEN|PASS_WARN_AGE)"
  cat /etc/pam.d/common-password 2>/dev/null || cat /etc/pam.d/system-auth 2>/dev/null
  chage -l root 2>/dev/null
  ```
- **Findings**:
  - PASS_MAX_DAYS > 90 or not set
  - PASS_MIN_LEN < 8
  - No password complexity requirements in PAM
  - Password never expires for privileged accounts

## 2. Vulnerabilities

### VUL-001: Kernel Version
- **Severity**: HIGH
- **Commands**:
  ```
  uname -r
  uname -a
  cat /proc/version
  ```
- **Findings**:
  - Kernel version significantly outdated (compare against known EOL)
  - Known vulnerable kernel versions

### VUL-002: Package Updates
- **Severity**: HIGH
- **Commands**:
  ```
  # Detect package manager and list available updates
  if command -v apt-get &>/dev/null; then
    apt-get -s upgrade 2>/dev/null | grep -c "^Inst" || echo "0"
    apt-get -s upgrade 2>/dev/null | grep "^Inst" | head -30
  elif command -v yum &>/dev/null; then
    yum check-update --quiet 2>/dev/null | tail -n +2 | head -30
    yum check-update --quiet 2>/dev/null | tail -n +2 | wc -l
  elif command -v dnf &>/dev/null; then
    dnf check-update --quiet 2>/dev/null | tail -n +2 | head -30
    dnf check-update --quiet 2>/dev/null | tail -n +2 | wc -l
  elif command -v zypper &>/dev/null; then
    zypper list-updates 2>/dev/null | head -30
  fi
  ```
- **Findings**:
  - Security updates available
  - Large number of pending updates (>50)
  - Critical packages outdated (openssl, openssh, kernel)

### VUL-003: Security Updates (CVE)
- **Severity**: CRITICAL
- **Commands**:
  ```
  # Check for security-specific updates
  if command -v apt-get &>/dev/null; then
    apt-get -s upgrade 2>/dev/null | grep -i security | head -20
    unattended-upgrades --dry-run 2>/dev/null | head -20
  elif command -v yum &>/dev/null; then
    yum updateinfo list security 2>/dev/null | head -30
  elif command -v dnf &>/dev/null; then
    dnf updateinfo list --security 2>/dev/null | head -30
  elif command -v zypper &>/dev/null; then
    zypper list-patches --category security 2>/dev/null | head -30
  fi
  ```
- **Findings**:
  - Outstanding security/CVE patches
  - Critical CVEs unpatched

### VUL-004: Listening Services
- **Severity**: MEDIUM
- **Commands**:
  ```
  ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null
  ss -ulnp 2>/dev/null || netstat -ulnp 2>/dev/null
  ```
- **Findings**:
  - Services listening on 0.0.0.0 (all interfaces)
  - Unexpected ports open
  - Services running as root unnecessarily

### VUL-005: Outdated Software Versions
- **Severity**: MEDIUM
- **Commands**:
  ```
  openssl version 2>/dev/null
  ssh -V 2>/dev/null
  curl --version 2>/dev/null | head -1
  python3 --version 2>/dev/null
  java -version 2>/dev/null 2>&1 | head -1
  php --version 2>/dev/null | head -1
  nginx -v 2>/dev/null 2>&1
  apache2 -v 2>/dev/null 2>&1 || httpd -v 2>/dev/null 2>&1
  mysql --version 2>/dev/null
  postgres --version 2>/dev/null
  ```
- **Findings**:
  - Known vulnerable versions of critical software
  - End-of-life software versions

## 3. Logs

### LOG-001: Authentication Logs
- **Severity**: HIGH
- **Commands**:
  ```
  # Failed SSH logins (last 7 days)
  journalctl -u sshd --since "7 days ago" --no-pager 2>/dev/null | grep -i "failed\|invalid\|error" | tail -50
  grep -i "failed\|invalid" /var/log/auth.log 2>/dev/null | tail -50
  grep -i "failed\|invalid" /var/log/secure 2>/dev/null | tail -50
  # Successful logins
  last -n 20 2>/dev/null
  lastb -n 20 2>/dev/null
  ```
- **Findings**:
  - Brute-force patterns (many failed attempts from same IP)
  - Successful login from unexpected IPs
  - Root login via SSH
  - Login at unusual hours

### LOG-002: System Logs
- **Severity**: MEDIUM
- **Commands**:
  ```
  journalctl -p err --since "7 days ago" --no-pager 2>/dev/null | tail -50
  dmesg -T 2>/dev/null | grep -i "error\|warn\|fail\|oom\|segfault" | tail -30
  cat /var/log/syslog 2>/dev/null | grep -i "error\|critical" | tail -30
  cat /var/log/messages 2>/dev/null | grep -i "error\|critical" | tail -30
  ```
- **Findings**:
  - OOM killer invocations
  - Segfaults in critical services
  - Hardware errors (disk, memory)
  - Service crash/restart loops

### LOG-003: Audit Logs
- **Severity**: MEDIUM
- **Commands**:
  ```
  auditctl -l 2>/dev/null || echo "NO_AUDITD"
  ausearch -m execve --start recent 2>/dev/null | tail -30
  ausearch -m USER_AUTH --start recent 2>/dev/null | tail -30
  cat /var/log/audit/audit.log 2>/dev/null | tail -50
  ```
- **Findings**:
  - Audit daemon not running
  - No audit rules configured
  - Suspicious command execution patterns
  - Privilege escalation events

### LOG-004: Log Rotation & Retention
- **Severity**: LOW
- **Commands**:
  ```
  cat /etc/logrotate.conf 2>/dev/null
  ls -la /etc/logrotate.d/ 2>/dev/null
  du -sh /var/log/ 2>/dev/null
  ls -lt /var/log/*.log 2>/dev/null | head -10
  ```
- **Findings**:
  - Log rotation not configured
  - Logs consuming excessive disk space (>5GB)
  - Missing log files
  - Logs not written to recently (possible logging failure)

## 4. System Health

### SYS-001: Disk Usage
- **Severity**: MEDIUM
- **Commands**:
  ```
  df -h
  df -i
  du -sh /var/log/ /tmp/ /home/ 2>/dev/null
  ```
- **Findings**:
  - Partition usage > 85%
  - Inode usage > 85%
  - /var/log abnormally large

### SYS-002: Memory & Swap
- **Severity**: MEDIUM
- **Commands**:
  ```
  free -h
  cat /proc/meminfo | head -10
  swapon --show 2>/dev/null
  ```
- **Findings**:
  - Memory usage > 90%
  - No swap configured
  - Swap usage > 50%

### SYS-003: CPU & Load
- **Severity**: LOW
- **Commands**:
  ```
  uptime
  cat /proc/loadavg
  nproc
  top -bn1 | head -20
  ```
- **Findings**:
  - Load average > 2x number of CPUs
  - Single process consuming >80% CPU
  - System uptime extremely long (>365 days, likely unpatched)

### SYS-004: Running Services
- **Severity**: LOW
- **Commands**:
  ```
  systemctl list-units --type=service --state=running 2>/dev/null | head -40
  systemctl list-units --type=service --state=failed 2>/dev/null
  ```
- **Findings**:
  - Failed services
  - Unnecessary services running (telnet, ftp, rsh, etc.)
  - Missing expected services (sshd, rsyslog, crond)

### SYS-005: Scheduled Tasks
- **Severity**: MEDIUM
- **Commands**:
  ```
  crontab -l 2>/dev/null
  ls -la /etc/cron.d/ 2>/dev/null
  cat /etc/cron.d/* 2>/dev/null
  ls -la /etc/cron.daily/ /etc/cron.hourly/ /etc/cron.weekly/ /etc/cron.monthly/ 2>/dev/null
  for user in $(awk -F: '$3==0||$3>=1000{print $1}' /etc/passwd); do echo "=== $user ==="; crontab -u "$user" -l 2>/dev/null; done
  systemctl list-timers --all 2>/dev/null | head -20
  ```
- **Findings**:
  - Suspicious cron jobs (wget/curl to external URLs, reverse shells)
  - Cron jobs running as root unnecessarily
  - Cron jobs with world-writable scripts

## 5. Network

### NET-001: Network Configuration
- **Severity**: LOW
- **Commands**:
  ```
  ip addr show 2>/dev/null || ifconfig -a 2>/dev/null
  ip route show 2>/dev/null || route -n 2>/dev/null
  cat /etc/resolv.conf 2>/dev/null
  cat /etc/hosts 2>/dev/null
  ```
- **Findings**:
  - Interfaces in promiscuous mode
  - Unexpected routes
  - DNS pointing to suspicious servers
  - Suspicious entries in /etc/hosts

### NET-002: Network Connections
- **Severity**: MEDIUM
- **Commands**:
  ```
  ss -tnp 2>/dev/null | head -50 || netstat -tnp 2>/dev/null | head -50
  ss -tnp state established 2>/dev/null | head -30
  ```
- **Findings**:
  - Connections to known malicious IPs/ports
  - Unexpected outbound connections
  - Connections on non-standard ports

### NET-003: DNS & Name Resolution
- **Severity**: LOW
- **Commands**:
  ```
  cat /etc/nsswitch.conf 2>/dev/null | grep hosts
  systemd-resolve --status 2>/dev/null | head -20
  ```
- **Findings**:
  - Non-standard name resolution order
  - DNS over non-standard ports

## 6. Compliance

### CMP-001: File Integrity
- **Severity**: MEDIUM
- **Commands**:
  ```
  rpm -Va 2>/dev/null | head -30 || dpkg -V 2>/dev/null | head -30
  aide --check 2>/dev/null | tail -20 || echo "NO_AIDE"
  ```
- **Findings**:
  - Modified system files
  - No file integrity monitoring (AIDE/OSSEC/Tripwire) installed

### CMP-002: Time Synchronization
- **Severity**: LOW
- **Commands**:
  ```
  timedatectl status 2>/dev/null
  chronyc tracking 2>/dev/null || ntpq -p 2>/dev/null || echo "NO_NTP"
  ```
- **Findings**:
  - Time not synchronized
  - No NTP/Chrony service running
  - Clock drift > 1 second

### CMP-003: Kernel Parameters
- **Severity**: MEDIUM
- **Commands**:
  ```
  sysctl net.ipv4.ip_forward 2>/dev/null
  sysctl net.ipv4.conf.all.accept_redirects 2>/dev/null
  sysctl net.ipv4.conf.all.send_redirects 2>/dev/null
  sysctl net.ipv4.conf.all.accept_source_route 2>/dev/null
  sysctl net.ipv4.conf.all.log_martians 2>/dev/null
  sysctl net.ipv4.icmp_echo_ignore_broadcasts 2>/dev/null
  sysctl net.ipv4.tcp_syncookies 2>/dev/null
  sysctl kernel.randomize_va_space 2>/dev/null
  sysctl fs.suid_dumpable 2>/dev/null
  sysctl kernel.core_uses_pid 2>/dev/null
  ```
- **Findings**:
  - IP forwarding enabled (unless router)
  - ICMP redirects accepted
  - Source routing accepted
  - SYN cookies disabled
  - ASLR disabled
  - Core dumps with SUID enabled
