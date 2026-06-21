# uHomeNest — base runtime boundary

`uHomeNest` is the **runtime repo for the uHOME product**: media player,
controller-first kiosk/thin UI, decentralised LAN server, Steam/Linux gaming
surfaces, and **presentation** of home automation (fed by `uHOME-matter`). It is
**not** the generic Sonic/Ventoy installer product—that stays in
`sonic-screwdriver`, which is the **bootstrap partner** for dual-boot and
recovery.

## Owns

- host lifecycle and persistent local execution on the uHOME Linux role
- media, playback, scheduling, and thin console surfaces
- LAN-first routing and household service composition
- curated library / vault reader flows exposed through the kiosk UX
- automation **fulfilment** and job queues **on this host** (thin automation lane)

## Transitional Local Support

Some Home Assistant bridge code still lives here historically; new **contracts**
and adapter catalogs belong in **`uHOME-matter`**, while the **kiosk** remains
the operator-visible surface on this repo.

## Does Not Own

- USB/Ventoy **installer product** semantics (`sonic-screwdriver`)
- Matter clone catalogs and HA bridge **contract** ownership (`uHOME-matter`)
- mobile/TV **client apps** as the server (`uHOME-client` / app repos)
- optional cross-family operator tooling unrelated to the home media/console role

Cross-repo **compatibility** (e.g. shared JSON contract shapes) may still exist;
they do **not** redefine uHOME as a sub-service of another product.
