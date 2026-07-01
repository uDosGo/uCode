# Course Project: Universal Sonic Screwdriver Hands-On

**Status**: Active learning project  
**Timeline**: Complete all phases in 2-3 hours (or work at your own pace)  
**Prerequisite**: Complete `prerequisites.md` checks

---

## Project Overview

This project teaches you to safely plan, inspect, validate, and apply a Sonic deployment by working through three scaffolded phases:

1. **Phase 1: Planning & Inspection** (45 min) — Build and understand a deployment plan
2. **Phase 2: Dry-Run Safety** (30 min) — Practice safe validation before applying
3. **Phase 3: Apply & Recovery** (45 min) — Execute a deployment with recovery options

Each phase reinforces concepts from the corresponding lesson.

---

## What You'll Learn

By completing this project, you'll know how to:

- [ ] Read and explain a Sonic deployment layout (`config/sonic-layout.json`)
- [ ] Generate a manifest safely with `sonic plan`
- [ ] Inspect and interpret manifest output
- [ ] Use dry-run to validate before applying
- [ ] Understand boundaries with `uDOS-core`, `uDOS-wizard`, and `uHOME-server`
- [ ] Recover from deployment failures
- [ ] Document a deployment for handoff

---

## Phase 1: Planning & Inspection (Lesson 2 + Project P1)

**Goal**: Create your first deployment plan and understand every part of it.  
**Time**: ~45 minutes  
**Corresponds to**: Lesson 2 - Plan, Inspect, Dry-Run

### Phase 1 Tasks

#### Task P1.1: Examine the Layout Configuration
Start by reading the layout that defines your deployment:

```bash
# View the Sonic layout configuration
cat config/sonic-layout.json
```

**Your job**: Create a short document (`my-first-deployment.md`) that answers:
1. What surfaces (USB, archive, payload location, etc.) does this layout define?
2. What is the role of each surface in a deployment?
3. Which parts are read-only plans vs. destructive operations?

Hint: Refer back to Lesson 2's "Configuration Walkthrough" section.

#### Task P1.2: Generate a Deployment Plan
Generate your first manifest *in dry-run mode* (safe, no changes):

```bash
# Edit installers/setup/ to match your environment, then:
cd /path/to/sonic-screwdriver

# Install Sonic CLI (first time only)
bash installers/setup/install-sonic-editable.sh

# Generate a plan
sonic plan \
  --usb-device /dev/sdb \
  --out memory/sonic/my-first-manifest.json
```

**Your job**: 
1. Run the command to success
2. Save the generated manifest location
3. Note any warnings or special messages

#### Task P1.3: Inspect the Manifest
Open and explore the generated manifest:

```bash
# View the manifest in your editor
cat memory/sonic/my-first-manifest.json | jq .

# Or examine parts of it:
cat memory/sonic/my-first-manifest.json | jq .plan
cat memory/sonic/my-first-manifest.json | jq .verify
```

**Your job**: Create a short report (`manifest-inspection.md`) that answers:
1. What sections does the manifest contain? (plan, verify, apply, etc.)
2. For each section, explain what information it holds
3. Which sections are safe to inspect vs. require careful handling during apply?
4. Where can you see this manifest being referenced in the layout?

Hint: Refer to Lesson 2's "Understanding the Manifest" section.

#### Task P1.4: Identify Boundaries
Based on your manifest, identify where Sonic hands off work to other systems:

**Your job**: Create a `boundaries.md` document that identifies:
1. Any `uHOME` bundle references (would go to `uHOME-server`)
2. Any `uDOS-core` or `uDOS-wizard` references that belong back to those repos
3. What Sonic *does* own in this deployment
4. What Sonic *doesn't* own or delegates

Hint: Refer to Lesson 1's "Sonic Boundaries" section.

### Phase 1 Completion Checklist

- [ ] Layout analyzed in `my-first-deployment.md`
- [ ] Manifest generated successfully
- [ ] Manifest inspection documented in `manifest-inspection.md`
- [ ] Boundaries identified in `boundaries.md`
- [ ] You can explain each section to a colleague

---

## Phase 2: Dry-Run Safety (Lesson 2 + Project P2)

**Goal**: Practice applying a deployment plan safely using dry-run.  
**Time**: ~30 minutes  
**Corresponds to**: Lesson 2 - Dry-Run Discipline

### Phase 2 Tasks

Prerequisites:
- Completed Phase 1
- Generated manifest from Phase 1

#### Task P2.1: Run Sonic Stick Apply in Dry-Run Mode
Practice the apply workflow without making real changes:

```bash
# Use your manifest from Phase 1
bash scripts/sonic-stick.sh \
  --manifest memory/sonic/my-first-manifest.json \
  --dry-run
```

**Your job**:
1. Run the command to completion
2. Observe what would happen (without actually happening)
3. Note any changes that would be staged
4. Document what you see in `dry-run-output.md`

#### Task P2.2: Verify Dry-Run Safety
Compare what dry-run said vs. what a real apply would do:

**Your job**: Create `dry-run-verification.md` that explains:
1. What operations are truly safe (read-only)?
2. What operations would be staged but not executed?
3. How would you know if something went wrong before apply?
4. What safety mechanisms does dry-run provide?

Hint: Refer to Lesson 2's "Dry-Run Discipline" section.

#### Task P2.3: Plan for Failure
Before progressing to Phase 3 (real apply), plan your recovery:

**Your job**: Create `contingency-plan.md` that documents:
1. What could go wrong during apply?
2. For each risk, what's the recovery procedure?
3. When would you escalate vs. attempt recovery yourself?
4. How would you communicate the issue?

### Phase 2 Completion Checklist

- [ ] Dry-run executed successfully
- [ ] Dry-run output documented in `dry-run-output.md`
- [ ] Safety mechanisms understood in `dry-run-verification.md`
- [ ] Contingency plan created in `contingency-plan.md`
- [ ] You understand what would happen during apply

---

## Phase 3: Apply & Recovery (Lesson 3 + Project P3)

**Goal**: Execute a real deployment and practice recovery if needed.  
**Time**: ~45 minutes (varies by hardware)  
**Corresponds to**: Lesson 3 - Apply, Rescue, Handoff

**⚠️ Important**: Phase 3 involves real changes. Only proceed if you:
- [ ] Completed Phase 1 & 2
- [ ] Have backups of your USB device
- [ ] Have tested dry-run multiple times
- [ ] Have documented your contingency plan
- [ ] Are ready to troubleshoot if needed

### Phase 3 Tasks

#### Task P3.1: Execute the Deployment
Apply the plan from Phase 1:

```bash
# Use your manifest (remove --dry-run)
bash scripts/sonic-stick.sh \
  --manifest memory/sonic/my-first-manifest.json
```

**Your job**:
1. Run the deploy command
2. Monitor progress and note any issues
3. Document the execution in `deployment-log.md` with timestamps
4. Record any warnings or required manual steps

#### Task P3.2: Validate the Deployment
Verify the deployment succeeded:

**Your job**: Create `deployment-validation.md` that confirms:
1. Did all expected changes apply?
2. Are there any partial failures?
3. Are all safety gates still in place?
4. Can you boot the target device?
5. What does the device look like now vs. before?

#### Task P3.3: Document Handoff
Prepare documentation for the next engineer/operator:

**Your job**: Create `handoff-brief.md` that documents:
1. What was deployed and when
2. Current state of the device
3. Known issues or workarounds
4. What to do if something needs rolling back
5. Who to contact for questions

Hint: Refer to Lesson 3's "Handoff Boundaries" section.

#### Task P3.4: Practice Recovery (Optional)
If something went wrong, practice recovery:

**Your job**: 
1. Refer to `contingency-plan.md` from Phase 2
2. Follow the recovery procedure if applicable
3. Document what you learned in `recovery-log.md`
4. Note any improvements for next time

### Phase 3 Completion Checklist

- [ ] Deployment executed successfully
- [ ] Deployment logged in `deployment-log.md`
- [ ] Validation confirmed in `deployment-validation.md`
- [ ] Handoff documented in `handoff-brief.md`
- [ ] (Optional) Recovery tested and documented
- [ ] You could guide someone else through this

---

## Project Completion & Reflection

Congratulations! You've completed the Universal Sonic Screwdriver course project.

### Reflection Prompts

Before you finish, spend 10 minutes answering these:

1. **What surprised you most** about the Sonic workflow?
2. **What was the most important** safety mechanism you learned?
3. **Where would you feel confident** acting independently vs. needing help?
4. **What would you teach someone else** about using Sonic?
5. **What questions do you still have**?

### Next Steps

Now that you've completed the course:

- **Troubleshooter**: If you encountered issues, see [Lesson 4 - Troubleshooting](../lessons/04-troubleshooting.md) (under development)
- **Operator**: You're ready to deploy Sonic to production hardware
- **Developer**: Explore [lessons/03-apply-rescue-and-handoff.md](../lessons/03-apply-rescue-and-handoff.md) for extension points
- **Continued Learning**: Explore `docs/v1/howto/` and `docs/v1/specs/` for deeper dives

---

## Submitting Your Project

Optional: Share your project for feedback:

1. Create a folder `projects/my-first-sonic-deployment/` in your local workspace
2. Include all your documentation files
3. Share the path or link with your instructor/mentor
4. Get feedback on your approach, documentation, and understanding

---

## Project Resources

- **Lesson 2 reference**: [Lesson 02 - Layout, Manifest, Dry-Run](../lessons/02-layout-manifest-and-dry-run.md)
- **Lesson 3 reference**: [Lesson 03 - Apply, Rescue, Handoff](../lessons/03-apply-rescue-and-handoff.md)
- **CLI reference**: `sonic plan --help`, `sonic --help`
- **Troubleshooting**: [Docs - Quickstart](../../docs/v1/howto/quickstart.md)

---

**Project Status**: Ready to begin!
