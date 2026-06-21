# Course 05 - Configurable Webhook Server

Purpose:

- explain why online API calls, webhooks, and scheduled sync jobs stay **outside**
  the `uHOME` stream
- contrast `uHOME-server` local automation with family-level online integration

Topics:

- configurable webhook receivers as a cross-cutting concern, not uHOME-owned
- scheduled outbound API calls and CRM-style hosts on the Ubuntu stack
- keeping household runtime separate from operator web surfaces

Repo anchors:

- `uDOS-wizard` networking and contract docs for Wizard-owned policy surfaces
- `uDOS-ubuntu` activation and host documentation for always-on local services
- `docs/pathway/REPO-FAMILY.md`

Boundary note:

- `uHOME-server` owns the base runtime and local execution surfaces
- `uHOME-matter` owns local automation and bridge contracts
- uHOME does not ship an online API or webhook broker; use Wizard and Ubuntu
  host docs for those lanes

First project:

- design a small local automation trigger in `uHOME-server` or `uHOME-matter`
  that does **not** assume a uHOME-side online broker
