# Lesson 02 - Layout, Manifest, And Dry-Run

Sonic treats deployment structure as explicit and reviewable.

## Core Concept: Safe Planning

The fundamental idea: **Nothing destructive should feel magical or hidden.**

Before any real changes, Sonic ensures you can:
1. Review what *will* change
2. Validate it before execution
3. Test it safely with dry-run
4. Only then proceed with confidence

## The Three Main Surfaces

Understanding these surfaces is critical:

| Surface | Purpose | Example |
|---------|---------|---------|
| **Layout** | Describes the target hardware and deployment structure | `config/sonic-layout.json` — specifies USB partitions, boot targets, payload locations |
| **Manifest** | Generated plan showing exactly what will happen | `memory/sonic/sonic-manifest.json` — step-by-step deployment recipe |
| **CLI** | Interface to generate plans and apply them | `sonic plan ...`, `scripts/sonic-stick.sh ...` |

---

## Real Example: Generating Your First Manifest

### Step 1: Understand the Layout

Let's start by looking at the deployment layout:

```bash
cat config/sonic-layout.json | jq .
```

**Sample Output:**
```json
{
  "name": "sonic-usb-standard",
  "version": "1.5.5",
  "target": {
    "device": "/dev/sdb",
    "partition_table": "gpt",
    "partitions": [
      {
        "number": 1,
        "size": "500M",
        "type": "EFI System",
        "mount": "/boot/efi",
        "format": "vfat"
      },
      {
        "number": 2,
        "size": "20G",
        "type": "Linux",
        "mount": "/",
        "format": "ext4"
      }
    ]
  },
  "bootloader": "GRUB2",
  "kernel": "linux-zen",
  "payloads": {
    "base_system": "file:///memory/sonic/artifacts/arch-base.tar.gz",
    "kernel_modules": "file:///memory/sonic/artifacts/kernel-modules.tar.gz"
  }
}
```

**What this means**:
- Target device: `/dev/sdb` (your USB drive)
- Two partitions: EFI boot (500M) and root filesystem (20G)
- Bootloader: GRUB2
- Payloads come from local files

### Step 2: Generate a Plan in Dry-Run Mode

```bash
sonic plan \
  --layout-file config/sonic-layout.json \
  --usb-device /dev/sdb \
  --dry-run \
  --out memory/sonic/my-plan.json
```

**What happens**:
- Sonic reads the layout
- Validates the target device exists
- Generates a manifest showing all steps
- **No actual changes** (dry-run mode)

**Sample Output:**
```
[INFO] Loading layout from config/sonic-layout.json
[INFO] Validating target device /dev/sdb (4.0G USB drive)
[INFO] Generating deployment manifest...
[INFO] Manifest written to memory/sonic/my-plan.json
[INFO] Dry-run mode: no changes applied
→ Review manifest: cat memory/sonic/my-plan.json | jq .
```

### Step 3: Inspect the Generated Manifest

```bash
cat memory/sonic/my-plan.json | jq . | head -50
```

**Sample Output (first sections):**
```json
{
  "metadata": {
    "plan_id": "plan-2026-03-10-001",
    "created_at": "2026-03-10T14:32:00Z",
    "layout_version": "1.5.5",
    "target_device": "/dev/sdb",
    "dry_run": true
  },
  "verification": {
    "device_exists": true,
    "device_size": "4.0G",
    "device_type": "USB",
    "can_write": true
  },
  "steps": [
    {
      "step_id": "01-backup",
      "action": "backup",
      "description": "Backup existing USB partition table",
      "command": "sgdisk --backup memory/sonic/sdb-backup.gpt /dev/sdb",
      "destructive": false,
      "estimated_time": "5s"
    },
    {
      "step_id": "02-partition",
      "action": "partition",
      "description": "Create new GPT partition table",
      "command": "sgdisk --zap-all --new 1:0:+500M --typecode 1:EF00 /dev/sdb",
      "destructive": true,
      "estimated_time": "10s"
    },
    {
      "step_id": "03-format-efi",
      "action": "format",
      "description": "Format EFI partition as vfat",
      "command": "mkfs.vfat -F 32 /dev/sdb1",
      "destructive": true,
      "estimated_time": "2s"
    }
  ]
}
```

**What you're seeing**:
- `metadata`: Plan ID, creation time, target device
- `verification`: Pre-flight checks (device exists, writable, etc.)
- `steps`: Each action that will be executed, in order
  - Each has a clear description
  - Each shows the exact command
  - Marked as destructive or safe
  - Estimated execution time

### Step 4: Verify Specific Sections

Check just the partitioning steps:

```bash
cat memory/sonic/my-plan.json | jq '.steps[] | select(.action == "partition")'
```

**Sample Output:**
```json
{
  "step_id": "02-partition",
  "action": "partition",
  "description": "Create new GPT partition table",
  "command": "sgdisk --zap-all --new 1:0:+500M --typecode 1:EF00 /dev/sdb",
  "destructive": true,
  "estimated_time": "10s"
}
```

If this looks wrong, **stop here**. Do not proceed. Fix the layout.

---

## Dry-Run Workflow: Practice Safe Execution

Once you have a manifest, test it with dry-run:

```bash
bash scripts/sonic-stick.sh \
  --manifest memory/sonic/my-plan.json \
  --dry-run
```

**Sample Output:**
```
[INFO] Loading manifest from memory/sonic/my-plan.json
[INFO] Verifying all steps (dry-run mode)
[DRY-RUN] Would execute: sgdisk --backup memory/sonic/sdb-backup.gpt /dev/sdb
[DRY-RUN] Would execute: sgdisk --zap-all --new 1:0:+500M --typecode 1:EF00 /dev/sdb
[DRY-RUN] Would execute: mkfs.vfat -F 32 /dev/sdb1
[DRY-RUN] Would execute: mkfs.ext4 /dev/sdb2
[DRY-RUN] Would execute: mount /dev/sdb1 /mnt/sonic-boot
[DRY-RUN] Completed 6 of 12 steps (dry-run verification)
[INFO] All steps validated
→ Run without --dry-run to apply changes
```

**What this tells you**:
- Each step is listed
- " `[DRY-RUN] Would execute:`" = this will happen when you remove `--dry-run`
- No actual changes made
- All validation passed

---

## Why Dry-Run Matters: A Real Story

Imagine this scenario:

**Without dry-run**:
- User runs deploy without checking
- Script partitions the wrong device (their laptop!)
- Disaster

**With dry-run**:
- User generates manifest
- User inspects manifest
- User runs dry-run
- Output shows: "**Wait, step 2 shows `/dev/sda`, not `/dev/sdb`!**"
- User stops, fixes the device name
- Then proceeds safely

**The lesson**: Dry-run is not optional. It's how you catch mistakes before they break things.

---

## Deeper Dive: Manifest Schema

For details on manifest format and validation:
- **Archived manifest spec**: See [docs/v1/specs/sonic-screwdriver.md](../../../docs/v1/specs/sonic-screwdriver.md)
- **Plan file format**: `docs/architecture/services-manifest.md` (under development)
- **Validation rules**: Check `services/manifest/` in the repo
- **Vault manifest examples**: [vault/manifests/README.md](../../../vault/manifests/README.md)
- **Vault profile templates**: [vault/templates/device-profiles/README.md](../../../vault/templates/device-profiles/README.md)

---

## Checkpoint: Can You Read a Manifest?

Before moving to Lesson 03, verify you understand manifests:

**Question 1**: You run `sonic plan` and get a manifest. What's the first thing you should do?
- A) Run it with `--dry-run` immediately
- B) Review the manifest file to check the steps
- C) Run it without `--dry-run` to deploy
- **Answer**: B — Always review before dry-run. Review before applying.

**Question 2**: In the manifest output, what does `"destructive": true` mean?
- A) The operation is safe to run multiple times
- B) The operation will destroy data if applied
- C) The operation requires administrator privileges
- **Answer**: B — Destructive means data will be lost. Take it seriously.

**Question 3**: Dry-run shows 12 steps. After reviewing, you want to apply step 1-6 only. What do you do?
- A) Edit the manifest to remove steps 7-12, then apply
- B) Run with `--dry-run` again to verify
- C) Sonic doesn't support partial applies; you must do all steps or none
- **Answer**: C — Sonic is all-or-nothing by design (safer). If you only want some steps, create a new layout.

---

## Key Takeaway

**The Sonic workflow is review-focused**:
1. Generate plan
2. **Review the manifest**
3. Dry-run it
4. Only then apply

This three-step discipline prevents the vast majority of deployment disasters.
