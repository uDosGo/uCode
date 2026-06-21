# Bridge

Purpose:

- connect `uHOME` runtime services to local automation systems
- expose bridge status, discovery, and commands
- isolate external-home-system integration from core server flows
- provide the runtime execution lane that `uHOME-matter` extension contracts
  target

Current runtime anchors:

- `src/uhome_server/services/home_assistant/`
- `src/uhome_server/services/home_assistant_service.py`
- `src/uhome_server/routes/home_assistant.py`

Boundary note:

- keep execution support here
- keep long-term extension contracts, clone catalogs, and target maps in
  `uHOME-matter`
