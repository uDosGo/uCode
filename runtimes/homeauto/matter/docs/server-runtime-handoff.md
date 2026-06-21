# uHOME-matter Server Runtime Handoff

`uHOME-matter` is the extension lane that sits on top of the `uHOME-server`
base runtime.

## Read This Boundary As

- `uHOME-server` executes local bridge support and exposes runtime health or
  service surfaces
- `uHOME-matter` defines the adapter, clone, and target contracts that the
  runtime consumes
- `uHOME-matter` also defines shared bridge metadata such as allowlists and
  discoverable entity maps

## Put Changes Here When

- the change adds or updates a Matter clone definition
- the change adds a Home Assistant adapter profile
- the change updates target maps or extension examples
- the change explains local automation ownership

## Put Changes In `uHOME-server` When

- the change alters runtime startup, health checks, or service supervision
- the change alters scheduling, playback, launcher, or LAN host behavior
- the change alters installer toggles or runtime config needed to host the
  extension
