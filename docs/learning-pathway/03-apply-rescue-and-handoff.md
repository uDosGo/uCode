# Lesson 03 - Apply, Rescue, And Handoff

Once a plan is reviewed through dry-run, Sonic can apply it on Linux.

Execution should stay explicit, and recovery should be straightforward.

## The Applied Workflow

The standard application workflow is:

```bash
# Generate and review plan (from Lesson 02)
sonic plan \
  --layout-file config/sonic-layout.json \
  --usb-device /dev/sdb \
  --out memory/sonic/sonic-manifest.json

# Dry-run to verify (from Lesson 02)
bash scripts/sonic-stick.sh \
  --manifest memory/sonic/sonic-manifest.json \
  --dry-run

# Now apply for real
bash scripts/sonic-stick.sh \
  --manifest memory/sonic/sonic-manifest.json
```

The key difference from Lesson 02: **No `--dry-run` flag**. Real changes happen.

---

## Real Example: Applying to Hardware

### Pre-Apply Checklist

Before you hit enter on the apply command:

- [ ] Manifested generated successfully
- [ ] Manifest reviewed and correct (checked `--dry-run`)
- [ ] Dry-run completed without errors
- [ ] You know which USB device is `/dev/sdb` (checked `lsblk` or `fdisk -l`)
- [ ] Backups exist if this USB had important data
- [ ] You're running from Linux (checked `uname -s`)
- [ ] You understand you **cannot undo this** without restoration

### Real Apply Output

```bash
$ bash scripts/sonic-stick.sh \
  --manifest memory/sonic/sonic-manifest.json

[INFO] Apply mode: changes will be written
[INFO] Loading manifest from memory/sonic/sonic-manifest.json
[INFO] Target device: /dev/sdb (4.0G)
[INFO] Proceeding in 10 seconds... (Ctrl+C to cancel)
9...8...7...6...5...4...3...2...1...

[EXEC] Step 01/12: Backup existing partition table
→ sgdisk --backup memory/sonic/sdb-backup.gpt /dev/sdb
✓ Backup saved: memory/sonic/sdb-backup.gpt

[EXEC] Step 02/12: Create new GPT partition table
→ sgdisk --zap-all --new 1:0:+500M --typecode 1:EF00 /dev/sdb
✓ Partitions created

[EXEC] Step 03/12: Format EFI partition
→ mkfs.vfat -F 32 /dev/sdb1
mke2fs 1.46.2 (28-Feb-2021)
✓ EFI partition formatted

[EXEC] Step 04/12: Format root partition
→ mkfs.ext4 /dev/sdb2
mke2fs 1.46.2 (28-Feb-2021)
Discarding device blocks: done                            
Creating filesystem with 8912896 4k blocks and 2228224 inodes
✓ Root partition formatted

[EXEC] Step 05/12: Mount boot partition
→ mount /dev/sdb1 /mnt/sonic-boot
✓ Mounted

[EXEC] Step 06/12: Mount root partition
→ mount /dev/sdb2 /mnt/sonic-root
✓ Mounted

[EXEC] Step 07/12: Extract base system
→ tar -xzf memory/sonic/artifacts/arch-base.tar.gz -C /mnt/sonic-root
✓ Extracted (3.2G, took 45 seconds)

[EXEC] Step 08/12: Install bootloader configuration
→ cp -r config/bootloader/grub-config /mnt/sonic-boot/grub
✓ Bootloader config installed

[EXEC] Step 09/12: Install kernel
→ chroot /mnt/sonic-root pacman -S linux-zen linux-firmware
:: Synchronizing package databases...
[many lines of package installation...]
✓ Kernel installed

[EXEC] Step 10/12: Generate boot entries
→ grub-mkconfig -o /mnt/sonic-boot/grub/grub.cfg
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-linux-zen
✓ Boot entries generated

[EXEC] Step 11/12: Verify boot device
→ efibootmgr --create --disk /dev/sdb --part 1 --label "Sonic USB" --loader /EFI/BOOT/BOOTX64.EFI
✓ Boot device registered

[EXEC] Step 12/12: Finalize and unmount
→ umount /mnt/sonic-boot /mnt/sonic-root
✓ Unmounted

[SUCCESS] Deployment completed in 2 minutes 34 seconds
[INFO] USB device /dev/sdb is ready to boot
→ Next: Boot device on target hardware, then Sonic hands off to uHOME

Deployment summary: memory/sonic/deployment-2026-03-10-14-35.log
```

**What this tells you**:
- Each step executed in order
- Progress shown for long operations (extraction, package install)
- Errors would stop the process immediately
- Summary log saved for reference

---

## When Things Go Wrong: Rescue Procedures

Deployments can fail. Here's how to handle it.

### Scenario 1: Apply Stops Mid-Way

**Example failure**:
```
[EXEC] Step 07/12: Extract base system
ERROR: Insufficient disk space (need 3.5G, have 2.1G)
[ERROR] Apply halted at step 07
→ Device state: Partially deployed
→ Partition table modified, root filesystem empty
```

**Recovery**:

1. **Collect evidence**:
   ```bash
   # Check what was actually applied
   lsblk | grep sdb
   mount | grep mnt/sonic
   ```

2. **Assess recovery options**:
   - Option A: Fix the issue (get a larger USB) and re-apply clean
   - Option B: Restore from backup
   - Option C: Manual cleanup and re-attempt

3. **If restarting from scratch**:
   ```bash
   # Restore original partition table from backup
   sgdisk --load-backup=memory/sonic/sdb-backup.gpt /dev/sdb
   ```

4. **If fixing and retrying**:
   ```bash
   # Use a larger USB device
   sonic plan --layout-file config/sonic-layout.json --usb-device /dev/sdc --out memory/sonic/sonic-manifest.json
   bash scripts/sonic-stick.sh --manifest memory/sonic/sonic-manifest.json
   ```

### Scenario 2: Device Won't Boot

**Symptom**: USB connects, no boot menu appears

**Diagnosis**:
```bash
# Check partition table
sgdisk -p /dev/sdb

# Check if EFI partition exists
ls /dev/sdb1 && echo "Partition 1 exists"

# Try to mount and verify boot files
mount /dev/sdb1 /mnt/check-boot
ls /mnt/check-boot && echo "Boot partition readable"
```

**Recovery**:
- If partition table is corrupt: Restore from `memory/sonic/sdb-backup.gpt`
- If boot files missing: Re-extract them manually or re-apply
- If BIOS doesn't recognize: Verify USB is in list, or try USB legacy mode

### Scenario 3: Deployment Succeeded but Runtime Failed

**Symptom**: USB boots, but uHOME runtime won't start

**This is NOT Sonic's problem anymore.** At this point:
1. Collect logs from `/home/.uhome/logs/` (or wherever uHOME stores them)
2. Escalate to uHOME-server team with evidence
3. Sonic's job is complete

---

## Rescue Workflows

Sonic carries several rescue tools:

### Collect Evidence

```bash
bash scripts/collect-logs.sh --device /dev/sdb --output memory/sonic/logs/
```

Creates a diagnostic bundle with:
- Partition table
- Mount status
- Boot configuration
- System logs

### Verify USB Layout

```bash
bash scripts/verify-usb-layout.sh /dev/sdb
```

Checks:
- Correct partition count and sizes
- Correct filesystem types
- Required boot files present
- Device is bootable

### Access Recovery Mode

```bash
# Boot the USB and access recovery shell
# (Exact procedure depends on your hardware)
# Once booted:
mount /dev/sdb2 /mnt/recovery
chroot /mnt/recovery
```

---

## Handoff: When Sonic's Job Ends

After a successful apply, Sonic hands off control:

### What Sonic Prepared

- ✅ Bootable USB with Linux base system
- ✅ Partitions and filesystem configured
- ✅ Bootloader ready
- ✅ Initial system extracted

### What Sonic Does NOT Own

- ❌ Runtime initialization (uHOME-server)
- ❌ Package updates (uHOME-server)
- ❌ User configuration (uHOME + user)
- ❌ Long-term maintenance (uHOME-server)

### Point of Handoff

When the USB device boots and uHOME-server takes over:

```
Sonic → [USB boots with prepared system] → uHOME-server → Runtime
```

At this handoff:
1. Sonic's role is complete
2. Issues in runtime are uHOME-server's responsibility
3. If runtime fails to start, contact uHOME-server with evidence
4. Sonic's rescue tools help collect evidence for escalation

---

## Deeper Dive: Advanced Recovery

For complex rescue scenarios:
- **Rescue procedures**: `modules/rescue/` in the repo
- **Archived diagnostics reference**: [docs/v1/howto/dry-run.md](../../../docs/v1/howto/dry-run.md)
- **Troubleshooting guide**: [Lesson 04 - Troubleshooting](04-troubleshooting.md)
- **Deployment note examples**: [vault/deployment-notes/README.md](../../../vault/deployment-notes/README.md)

---

## Checkpoint: When Do You Stop?

Before handing off, verify your understanding:

**Question 1**: After apply succeeds, Kodi won't start. What do you do?
- A) Troubleshoot Kodi yourself
- B) Contact uHOME-server team with logs from the USB
- C) Run Sonic recovery tools
- **Answer**: B — Runtime issues belong to uHOME-server. Sonic's job is done.

**Question 2**: Apply fails mid-way. What's your first action?
- A) Immediately run `bash scripts/sonic-stick.sh` again
- B) Collect evidence with `bash scripts/collect-logs.sh`
- C) Restore the backup partition table
- **Answer**: B — Always collect evidence first. Understand the failure before retrying.

**Question 3**: USB boots but has weird behavior. Who should investigate?
- A) You should try Sonic recovery tools first
- B) Escalate immediately to uHOME-server
- C) Check if the issue is boot-time (Sonic) or runtime (uHOME)
- **Answer**: C — First determine which system owns the problem, then escalate accordingly.

---

## Key Takeaway

**Sonic owns deployment, not runtime.** After successfully applying a deployment:
- The USB is bootable ✓
- The Linux base is ready ✓
- But you haven't "completed" anything—you've just handed off to the next team

Know the boundary. When things fail, knowing who owns the problem is half the battle.
