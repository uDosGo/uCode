# uHomeNest — uHOME architecture

**uHomeNest** (**v3.9.x**) is the Git repository for the **uHOME** **household media, console, and LAN server** product: a
**decentralised** node on the home network that runs **Jellyfin**, a
**controller-first** kiosk/thin UI, **Steam/Linux** gaming surfaces, a **curated
library** of games and apps, and **Home Assistant** integration **through the
same thin UX** (bridge contracts live in `uHOME-matter`).

Install, recovery, and **dual-boot (Linux uHOME + Windows/Steam)** workflows are
**driven by `sonic-screwdriver`**—the Ventoy/USB and bootstrap lane—not by
Empire- or Wizard-centric operator flows.

uHOME is designed **local-first** and without mandatory cloud dependency.

## Main Areas

- `services/` exposes runtime and service surfaces.
- `scheduling/` holds recurring execution logic.
- `modules/` organizes service modules and extensions.
- `config/` stores runtime configuration.
- `config/base-runtime-profile.example.json` is the starter checked-in base
  runtime profile.
- `src/uhome_server/` remains the active standalone server package while the
  repo converges on the v2 spine.
- `scripts/run-uhome-server-checks.sh` is the activation validation entrypoint.
- `apps/tablet-kiosk/` is the tablet-and-living-room kiosk application surface.
- `apps/dashboard/` is the household dashboard UI surface.

---

## Topology

Preferred deployment: **Linux** as the uHOME host on a **normal LAN**
(consumer or small-office router). The machine may be **dual-boot** with
**Windows + Steam** for a dedicated gaming/desktop side; **Linux remains the
orchestration authority** for uHOME (media, kiosk, HA integration, LAN
services). **`sonic-screwdriver`** is the family path for imaging, Ventoy sticks,
and bootstrap—not Wizard/Empire.

Linux host typically runs:

- **uHomeNest** / **uHOME** server — API, thin UI, scheduling, library surfaces
- **Jellyfin** — household media library and playback metadata
- **Home Assistant** (optional) — automation brain; **kiosk surfaces** consume
  bridge/metadata from `uHOME-matter` contracts
- **Matter / device adapters** (via `uHOME-matter`)

Windows side (optional dual-boot):

- Steam and auxiliary games/apps; **not** the uHOME server runtime

---

## Kiosk Environment

uHomeNest provides a **Steam-console-style launcher interface** designed
for TVs, tablets, and living-room displays.

Primary design principle: **controller-first navigation**.

Supported input:

- Xbox controllers, PlayStation controllers, Bluetooth HID gamepads
- keyboard, mouse, touch

Gamepad is the **primary interaction model**.

### UX Surfaces

**Living-Room Launcher** — tile-based, big-screen-friendly, controller-first.
Launch targets: **media**, **games** (curated library / Steam), **home
automation** (HA-backed scenes and status), vault content, dashboards.

**Thin-GUI Kiosk Mode** — tablets, TVs, secondary displays. Shows playback,
queues, **automation status** (Home Assistant–backed where configured), and thin
job surfaces.

**Media Panel** — Jellyfin library browsing, playback controls, queue management.

**Jobs / Scheduling Panel** — local schedules, automation fulfilment, retries;
primary story is **uHOME-local** and HA/Matter, not an external command-centre.

---

## Included Services

### Jellyfin

Jellyfin is the primary media server:

- media library hosting
- local streaming and playback metadata
- household media management
- integrates directly into kiosk UI surfaces

### Steam / Game Services

uHomeNest supports Steam presence and gaming launch surfaces:

- Steam library access
- remote play support
- game launcher integration
- controller-first navigation

---

## Networking Modes

### Default: regular LAN

Ship and run uHOME on a **normal** home or office network: Wi‑Fi or Ethernet,
consumer or small-business router, private addresses, DNS as provided by the
LAN. Policy contracts and JSON schema ship **inside** `uHomeNest`
(`src/uhome_server/contracts/`); no `uDOS-wizard` checkout is required.

The bundled **`lan`** profile matches typical router-backed operation. Optional
profiles (`beacon`, `crypt`, `tomb`, `home`) remain for stricter or alternate
visibility stories; they describe policy payloads, not custom link layers.

### Future: uDOS-ubuntu command-centre

A **later** uHOME release may align or extend these profiles with
**uDOS-ubuntu** command-centre networking. That is explicitly out of scope for
the current regular-LAN baseline.

---

## Extension Model

| Extension | Responsibility |
| --- | --- |
| `uHOME-matter` | Home Assistant and Matter **contracts**, bridge definitions, clone/target maps—so the **kiosk thin UX** can show **real home state** (rooms, scenes, entities) without reimplementing HA inside the server repo |

`uHomeNest` **hosts** the thin presentation; `uHOME-matter` **defines** what
the runtime is allowed to know about devices and bridges.

---

## Contract Edges

Family-level sequencing and Wizard/core boundaries: **`uDOS-dev/docs/uhome-stream.md`**
(operator checkout: `uDOS-family/uDOS-dev`).

- **`sonic-screwdriver`** — **first-class** for getting uHOME onto metal: USB,
  Ventoy, dual-boot layout, recovery; not an afterthought.
- **`uHomeNest`** bundles household **network policy** for regular LANs
  (`src/uhome_server/contracts/`).
- **`uHOME-matter`** — HA/Matter extension contracts consumed by this runtime.
- **`uDOS-core`** (when present on disk) — optional **shared** sync-record and
  workflow **artifact paths** for family compatibility; uHOME remains a
  **standalone product**, not a subordinate service.

---

## Design Principles

- local-first, decentralised LAN
- controller-first UX (kiosk / TUI parity where it matters)
- curated library + thin presentation (media, games, apps)
- modular extensions (Matter/HA via `uHOME-matter`)
- no mandatory cloud dependency
- server-hosted automation and scheduling on the uHOME host

## Transitional Note

Some Matter-adjacent or Home Assistant runtime code still exists here under
legacy module and service roots. In v2 those surfaces are treated as
transitional local runtime support, while new contract and clone definitions
belong in `uHOME-matter`.
