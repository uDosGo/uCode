# Course 03 - Home Automation

Purpose:

- explain local automation flows and bridge patterns
- connect schedules, triggers, and household devices

Topics:

- event automation
- scheduling
- smart device control
- bridge boundaries
- local-first automation distinct from online integration lanes outside uHOME

Repo anchors:

- `modules/home-assistant-bridge/`
- `services/bridge/`
- `services/scheduling/`
- `src/uhome_server/routes/home_assistant.py`
- sibling repo: `../../uHOME-matter/src/matter-bridge-contract.json`
- sibling repo: `../../uHOME-matter/src/matter-clone-catalog.json`

First project:

- implement a simple automation workflow over the sample vault

Boundary note:

- `uHOME-server` owns local execution, scheduling, and host runtime support
- `uHOME-matter` owns Home Assistant, Matter, and local device automation
  contracts or clone definitions
- custom online APIs and webhook jobs are not part of the uHOME stream
