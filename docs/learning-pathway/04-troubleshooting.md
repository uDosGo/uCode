# Lesson 04 - Troubleshooting And Recovery

Deployments don't sempre go perfectly. This lesson teaches systematic troubleshooting and recovery procedures.

**Prerequisites**: Complete Lessons 01-03 first. You should understand the three-phase workflow (plan → dry-run → apply).

---

## Troubleshooting Philosophy

When deployment fails, follow this discipline:

1. **Collect evidence** — Understand what actually happened
2. **Classify the problem** — Which phase? Which system?
3. **Know your boundaries** — Is this Sonic's job or someone else's?
4. **Attempt recovery** — Use the right tool for the problem
5. **Escalate if needed** — Raise to the appropriate owner

The goal is **data-driven decisions**, not guessing.

---

## Phase 1: Planning Failures

### Symptom: `sonic plan` command fails

**Common Error 1: Device not found**
```bash
$ sonic plan --usb-device /dev/sdc --out manifest.json
ERROR: Device /dev/sdc not found
```

**Diagnosis**:
```bash
# Verify device is actually connected
lsblk | grep -E "sdb|sdc|sdd"

# List all block devices
sudo fdisk -l | grep "Disk"

# Check USB bus
lsusb
```

**Recovery**:
- Device name is usually `/dev/sdbN` (where N is partition number)
- Use `lsblk` to find the real device
- Verify it's a USB drive (not your main disk!)
- Rerun with correct device

**Common Error 2: Layout file not found**
```bash
$ sonic plan --layout-file /nonexistent/config.json --out manifest.json
ERROR: Layout file not found: /nonexistent/config.json
```

**Diagnosis**:
```bash
# Verify layout file exists
ls -l config/sonic-layout.json

# Check config directory
ls config/
```

**Recovery**:
- Use correct path to layout file (usually `config/sonic-layout.json`)
- Verify layout file is readable
- Check for typos in path

**Common Error 3: Layout validation fails**
```bash
$ sonic plan --layout-file config/sonic-layout.json --out manifest.json
ERROR: Layout validation failed: partition 2 exceeds device capacity (need 25G, have 4G)
```

**Diagnosis**:
```bash
# Check actual USB device size
sudo fdisk -l /dev/sdb | grep "Disk /dev/sdb"

# Check what layout expects
cat config/sonic-layout.json | jq '.target.partitions'
```

**Recovery**:
- Use a larger USB device, OR
- Edit the layout to use smaller partitions, OR
- Create a new layout file for your device

---

## Phase 2: Dry-Run Failures

### Symptom: `--dry-run` shows unexpected steps

**Example**: Dry-run shows wrong device

```bash
$ bash scripts/sonic-stick.sh --manifest memory/sonic/my-plan.json --dry-run
[DRY-RUN] Would execute: sgdisk --zap-all ... /dev/sda ← WRONG DEVICE!
```

**Diagnosis**:
```bash
# Check the manifest target device
cat memory/sonic/my-plan.json | jq '.metadata.target_device'

# Verify which device you actually want
lsblk | grep -E "Name|sda|sdb|sdc"
```

**Recovery**:
- **STOP!** Do not apply this manifest
- Generate a new manifest with the correct device
- This is exactly why dry-run exists

**Example**: Dry-run shows missing files

```bash
$ bash scripts/sonic-stick.sh --manifest memory/sonic/my-plan.json --dry-run
[WARN] Payload not found: file:///memory/sonic/artifacts/arch-base.tar.gz
[ERROR] Cannot proceed with missing payloads
```

**Diagnosis**:
```bash
# Check for the missing file
ls -lh memory/sonic/artifacts/

# Find where the actual file is
find . -name "arch-base.tar.gz" 2>/dev/null

# Check manifest references
cat memory/sonic/my-plan.json | jq '.payloads'
```

**Recovery**:
- Download/extract missing payloads
- Update layout to point to correct paths
- Regenerate manifest
- Retry dry-run

---

## Phase 3: Apply Failures (Most Critical)

### Symptom: Apply starts but fails mid-execution

**Example: Disk full during extraction**
```bash
[EXEC] Step 07/12: Extract base system
tar: write error: No space left on device
[ERROR] Apply halted at step 07/12
```

**Diagnosis**:
```bash
# Check actual partition sizes created
sudo fdisk -l /dev/sdb

# Check mounted filesystems
mount | grep /mnt/sonic

# Check free space
df -h /mnt/sonic-root

# Check what was extracted so far
sudo ls -lh /mnt/sonic-root/
```

**Recovery**:

Option A: Use a larger USB drive
```bash
# Restore old device partition table
sudo sgdisk --load-backup=memory/sonic/sdb-backup.gpt /dev/sdb

# Clean up mounts
sudo umount /mnt/sonic-root
sudo umount /mnt/sonic-boot

# Use new device
sonic plan --usb-device /dev/sdc --out new-manifest.json
bash scripts/sonic-stick.sh --manifest new-manifest.json
```

Option B: Modify layout for smaller device
```bash
# Edit layout to use less space
nano config/sonic-layout.json
# (reduce partition sizes)

# Regenerate and retry
sonic plan --layout-file config/sonic-layout.json --usb-device /dev/sdb --out manifest.json
bash scripts/sonic-stick.sh --manifest manifest.json --dry-run
bash scripts/sonic-stick.sh --manifest manifest.json
```

**Example: Bootloader installation fails**
```bash
[EXEC] Step 10/12: Generate boot entries
grub-mkconfig: error: no known filesystem
[ERROR] Apply halted at step 10/12
```

**Diagnosis**:
```bash
# Check if partitions are mounted correctly
mount | grep sonic

# Verify bootloader filesystem
ls /mnt/sonic-boot/

# Check if boot files are present
sudo ls -lh /mnt/sonic-root/boot/
```

**Recovery**:
```bash
# Manually fix boot configuration
sudo chroot /mnt/sonic-root
grub-mkconfig -o /boot/grub/grub.cfg
exit

# Continue from where it failed (or restart full apply)
bash scripts/sonic-stick.sh --manifest manifest.json --resume-from=10
```

**Example: Permission denied during apply**
```bash
[EXEC] Step 02/12: Create new GPT partition table
Error: Operation not permitted
[ERROR] Apply requires sudo/root privileges
```

**Diagnosis**:
```bash
whoami  # Check current user
sudo whoami  # Check if sudo works
sudo fdisk -l | head -1  # Verify sudo access
```

**Recovery**:
```bash
# Apply must run as root or with sudo
sudo bash scripts/sonic-stick.sh --manifest manifest.json

# Or configure sudoers to not require password
visudo  # (requires editing sudoers carefully)
```

---

## Post-Apply Issues

### Symptom: Apply succeeds but device won't boot

**Diagnosis**:
```bash
# Check partition table
sudo sgdisk -p /dev/sdb

# Verify boot partition exists and is readable
sudo mount /dev/sdb1 /mnt/check-boot
ls /mnt/check-boot
ls /mnt/check-boot/EFI/BOOT/

# Check if MBR is valid
sudo fdisk -l /dev/sdb | head -20
```

**Recovery**:
```bash
# Restore and retry
sudo sgdisk --load-backup=memory/sonic/sdb-backup.gpt /dev/sdb
sudo umount /mnt/check-boot

# Note which step failed and run apply again
bash scripts/sonic-stick.sh --manifest manifest.json --resume-from=10

# Or start completely fresh
sonic plan --layout-file config/sonic-layout.json --usb-device /dev/sdb --out manifest.json
bash scripts/sonic-stick.sh --manifest manifest.json
```

### Symptom: Device boots but runtime initialization fails

**Example: uHOME won't start**
```
[Boot successful]
Sonic-deployed system ready
uHOME initialization...
ERROR: uHOME runtime failed to initialize
```

**At this point, **Sonic's job is done.** This is a uHOME-server issue.**

**Diagnosis** (collect evidence for escalation):
```bash
# Boot the device and collect logs
sudo mount /dev/sdb2 /mnt/uhome-device
ls /mnt/uhome-device/var/log/
cat /mnt/uhome-device/var/log/uhome-init.log

# Collect output
tar -czf uhome-failure-logs.tar.gz /mnt/uhome-device/var/log/
```

**Escalation (contact uHOME-server team)**:
- Share logs from above
- Include the manifest used
- Include device specs (USB size, hardware target)
- Document exact symptoms

---

## Decision Tree: Where's the Problem?

Use this flowchart to classify the issue:

```
┌─ Does `sonic plan` succeed?
│  └─ NO → Phase 1 failure (see Phase 1 section)
│  └─ YES ↓
│
├─ Does `--dry-run` succeed?
│  └─ NO → Phase 2 failure (see Phase 2 section)
│  └─ YES ↓
│
├─ Does `apply` (without --dry-run) succeed?
│  └─ NO → Phase 3 failure (see Phase 3 section)
│  └─ YES ↓
│
├─ Does device boot?
│  └─ NO → Boot configuration issue (see Phase 3: "won't boot")
│  └─ YES ↓
│
└─ Does runtime initialize?
   └─ NO → uHOME-server issue (Sonic is done, escalate)
   └─ YES → SUCCESS! Deployment complete
```

---

## Recovery Tools

### Evidence Collection

```bash
# Collect diagnostic bundle
bash scripts/collect-logs.sh --device /dev/sdb --output recovery-logs/
```

Creates:
- Partition table snapshot
- Mount status
- Boot configuration
- System logs
- Manifest copy

### Partition Verification

```bash
# Verify partition layout
bash scripts/verify-usb-layout.sh /dev/sdb

# Output:
# ✓ Partition 1: EFI System (500M)
# ✓ Partition 2: Linux (20G)
# ✓ Boot files: Present
# ✓ Device is bootable
```

### Manual Inspection

```bash
# Mount and explore
sudo mount /dev/sdb2 /mnt/inspect-root
sudo mount /dev/sdb1 /mnt/inspect-boot

# Check filesystem integrity
sudo fsck -n /dev/sdb2  # (read-only check)

# Explore directory structure
sudo ls -la /mnt/inspect-root/
sudo ls -la /mnt/inspect-root/boot/
```

### Backup and Restore

```bash
# Save partition table before major changes
sudo sgdisk --backup=$HOME/sdb-backup.gpt /dev/sdb

# Restore partition table
sudo sgdisk --load-backup=$HOME/sdb-backup.gpt /dev/sdb

# Full device backup (takes time)
sudo dd if=/dev/sdb of=$HOME/sdb-full-backup.img bs=4M status=progress
```

---

## Escalation Guide

**When to escalate** (it's not your problem):

| Issue | Owner | How to Escalate |
|-------|-------|---|
| Runtime won't start | uHOME-server | Share logs + manifest |
| Sonic CLI errors | Sonic team | GitHub issue + error message |
| Device won't boot after Sonic applies correctly | System/firmware | Escalate with boot logs |
| uDOS profile issues | uDOS team | Profile validation errors |

**What to include** when escalating:
- Exact error messages (full output if possible)
- Command you ran
- Manifest (if relevant)
- Evidence collection output
- What you've already tried

---

## When to Give Up and Restart

Sometimes, the best recovery is starting fresh:

```bash
# Restore original partition table
sudo sgdisk --load-backup=memory/sonic/sdb-backup.gpt /dev/sdb

# Verify restoration
sudo sgdisk -p /dev/sdb

# Wipe clean (if needed)
sudo sgdisk --zap-all /dev/sdb

# Try again with fresh manifest
sonic plan --layout-file config/sonic-layout.json --usb-device /dev/sdb --out manifest-v2.json
bash scripts/sonic-stick.sh --manifest manifest-v2.json --dry-run
bash scripts/sonic-stick.sh --manifest manifest-v2.json
```

---

## Deeper Dive: Advanced Recovery

- **Chroot recovery**: `modules/rescue/chroot-recovery.sh`
- **Partition recovery**: `modules/rescue/partition-recover.sh`
- **Bootloader debugging**: `docs/howto/bootloader-debug.md`

---

## Checkpoint: Can You Troubleshoot?

**Scenario 1**: Apply fails at step 7/12 with "No space left." What's your first action?
- A) Try applying again
- B) Collect evidence with `bash scripts/collect-logs.sh`
- C) Immediately restore from backup
- **Answer**: B — Always understand the problem first

**Scenario 2**: Dry-run shows device `/dev/sda` but you wanted `/dev/sdb`. What do you do?
- A) Apply anyway and hope
- B) Stop and regenerate manifest with correct device
- C) Manually edit manifest to change device
- **Answer**: B — Never apply a plan with wrong device. Regenerate.

**Scenario 3**: Device boots but runtime fails. Who do you contact?
- A) Sonic team (it's a deployment issue)
- B) uHOME-server team (it's a runtime issue)
- C) Your device manufacturer (hardware issue)
- **Answer**: B — Runtime failures are uHOME-server's responsibility

---

## Key Takeaway

**Troubleshooting is about boundaries and evidence**.

Collect data → Classify the problem → Apply the right tool → Escalate when needed.

The vast majority of deployment issues can be avoided or fixed with the discipline you learned in Lessons 01-03 (review, dry-run, understand boundaries).

