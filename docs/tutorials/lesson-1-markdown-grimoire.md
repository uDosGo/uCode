---
title: "Lesson 1: The Markdown Grimoire"
status: draft
last_updated: 2026-05-26T19:55:01+10:00
category: course
tags: [course, uconnect]
description: "**Course:** uDos Orientation"
---
# Lesson 1: The Markdown Grimoire

**Course:** uDos Orientation
**Time:** 45–60 minutes
**Difficulty:** Beginner
**Output:** A structured vault with contacts, projects, and tasks

---

## What You'll Learn

By the end of this lesson, you will be able to:

- Create a markdown file and add **frontmatter** (YAML metadata)
- Use **`[[wiki]]` links** to connect ideas
- Write tasks with **`- [ ]`** syntax that the vault understands
- Build a **mini vault** with contacts, projects, and tasks
- Explain how your notes could become **story entries** in the Public Story Lane

---

## Prerequisites

- Completed **Lesson 0** (you know your way to `@toybox`)
- A terminal and text editor (any will do – VS Code, Obsidian, even Notepad)
- Imagination (required)

---

## Part 1: Markdown is Magic

**Markdown** is a simple way to write formatted text that any computer can read. It looks like plain text, but it contains **hidden structure** – like runes carved into stone.

Here's a basic spell:

```markdown
# A Hero Rises

The wizard **Merlin** prepares a *fireball* spell.

- Find the dragon
- Cast the incantation
- Save the village
```

That's markdown. The `#` means "heading". `**bold**` and `*italic*` add emphasis. `-` makes a list.

But uDos markdown is **enhanced** – it can hold **frontmatter** (secret metadata), **tasks** (actionable items), and **links** (portals between notes).

---

## Part 2: Your First Spell – A Contact File

In the Student Lane, `vault/user/contacts/` holds information about people (allies, mentors, contributors).

Let's create one in the safety of `@toybox`.

### Step 1: Navigate to the Toybox

```bash
cd ~/vault/user/@toybox
mkdir -p contacts
cd contacts
```

### Step 2: Create a Markdown File

Use your text editor (or `nano`) to create `merlin.md`:

```bash
nano merlin.md
```

Paste this:

```markdown
---
name: Merlin
role: Archwizard
location: Camelot
status: active
tags: [mentor, magic]
---

# Merlin, the Archwizard

Merlin is a legendary wizard who advises King Arthur.

## Known Spells
- Teleportation
- Fireball
- [[mind-reading]]

## Current Tasks
- [ ] Teach the young wizard about frontmatter
- [x] Create the first contact file
- [ ] Brew a potion of clarity

## Notes
> "The vault is the source of truth."

See also: [[arthur|King Arthur]]
```

Notice the **`[[wiki]]` links**:
- `[[mind-reading]]` – links to a note that doesn't exist yet (that's fine!)
- `[[arthur|King Arthur]]` – links to a note with an alias

### Step 3: Save and View

Save the file (`Ctrl+O`, then `Ctrl+X` in nano). Then view it in the terminal:

```bash
cat merlin.md
```

**Congratulations!** You've written your first uDos spell.

---

## Part 3: Frontmatter – The Secret Metadata

Frontmatter is the **hidden power** of each note. It lives at the top, between `---` lines, in YAML format.

```yaml
---
name: Merlin
role: Archwizard
location: Camelot
status: active
tags: [mentor, magic]
---
```

**Why frontmatter matters:**
- uDos can **search** for all contacts with `status: active`
- The **student lane** can generate a directory of wizards
- The **public story lane** might turn Merlin into a recurring character
- You can sort, filter, and query your vault without a database

---

## Part 4: Links – Portals Between Notes

The `[[wiki]]` link is a **portal**. When you write `[[mind-reading]]`, you're saying: "There is a note called `mind-reading.md` somewhere in this vault."

If the note exists, following the link takes you there. If it doesn't, the link is a **dangling portal** – a promise of future knowledge.

**Alias syntax:** `[[arthur|King Arthur]]` – the link points to `arthur.md`, but displays as "King Arthur".

**Why links matter:**
- Build a **knowledge graph** – ideas connect, just like neurons in a brain
- The student lane can generate a **map** of your realm
- The public story lane can turn links into "quest lines"

---

## Part 5: Tasks – Actionable Spells

The `- [ ]` syntax creates a **task** – something you need to do.

```markdown
- [ ] Teach the young wizard about frontmatter
- [x] Create the first contact file
- [ ] Brew a potion of clarity
```

- `- [ ]` means "not done"
- `- [x]` means "done"

**Why tasks matter:**
- uDos can **list all pending tasks** across your entire vault
- The student lane can show your "quest log"
- The public story lane could turn completed tasks into "achievements"

---

## Part 6: Build Your Mini Vault (Exercise)

Now it's your turn to **extend the vault** creatively.

**Choose one of these paths:**

### Path A – The Hero's Journey
Create a new contact: `contacts/yourname.md` with your own frontmatter (role, location, powers). Then create a project: `projects/my-epic-quest.md` that lists tasks you want to accomplish in uDos. Link your contact to the quest.

### Path B – The Monster Manual
Create a `monsters/` folder and add a file for a creature (e.g., `dragon.md`). Include frontmatter: `health`, `damage`, `loot`. Link it to the `quest-for-grail.md` as an obstacle.

### Path C – The Spellbook
Create a `spells/` folder. Write a markdown file for a new uCode spell (e.g., `teleport.md`). Describe what it does, and frontmatter with `mana_cost`, `range`. Link it to your contact.

**Spend at least 15 minutes on this.** The goal is not perfection – it's understanding how markdown, frontmatter, links, and tasks work together.

---

## What You've Learned

- ✅ Markdown is the source of truth – plain text with hidden structure
- ✅ Frontmatter (YAML) stores **metadata** like a character sheet
- ✅ `[[wiki]]` links create **portals** between notes
- ✅ `- [ ]` tasks are **actionable items** the vault can track
- ✅ You built a mini vault with contacts, projects, and links

---

## How This Becomes a Story

When a developer (not you, yet) adds a feature like "support for teletext grid" and commits it with a game-tagged message, the `storyteller` daemon generates a **public story entry**:

> *"The Wizard carved a new teletext grid on level 12. The walls shimmer with runes."*

And a **student tutorial**:

> *"Level 12 – Implementing a Teletext Grid – Step-by-step guide to adding a grid renderer in Rust."*

Your student notes, however, are your **private grimoire**. They won't appear on the public site unless you choose to share them.

But one day, when you become a contributor, your commits will become legend.

---

## Next Up

**Lesson 2: Local-First Development** – You'll run a local server that reads your vault and turns it into a live API. Your contacts will become JSON. Your tasks will become a REST endpoint. The magic becomes **real**.

But first, spend some time in `@toybox`. Add more notes. Link them. Create tasks. Break things (with compost, not trash). This is your workshop.

```ascii
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│   ╔═══════════════════════════════════════════════════════════════════╗    │
│   ║                                                                   ║    │
│   ║   LESSON 1 COMPLETE!                                              ║    │
│   ║                                                                   ║    │
│   ║   You have learned:                                               ║    │
│   ║   ✓ Markdown basics (headings, lists, emphasis)                  ║    │
│   ║   ✓ Frontmatter (YAML metadata)                                  ║    │
│   ║   ✓ Wiki links [[like this]]                                     ║    │
│   ║   ✓ Task syntax - [ ] and - [x]                                  ║    │
│   ║   ✓ How your notes relate to the three lanes                     ║    │
│   ║                                                                   ║    │
│   ║   Your first grimoire entries are written.                       ║    │
│   ║   The vault remembers.                                           ║    │
│   ║                                                                   ║    │
│   ║   PRESS [SPACE] TO CONTINUE TO LESSON 2                          ║    │
│   ║                                                                   ║    │
│   ╚═══════════════════════════════════════════════════════════════════╝    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Ready for Lesson 2, or want to adjust anything in Lesson 1?** 🔧
