# Contributing

The architecture catalog is the extension point. Edit `catalog/architectures.yaml`, then run `python3 tools/generate_catalog.py`; do not hand-edit generated README tables or indexes.

- New architecture: copy an existing `architectures/*/architecture.md`; name it by workflow when several tools fit. Add its audience, problem, workflow, scale, security, compliance and links to the catalog. Reuse `examples/` instead of duplicating configs.
- New integration: add it under the relevant catalog architecture with its connection method, `connection_type`, authoritative documentation `url` and, where one exists, a `setup_url` for the B2 setup guide. Count a tool only when its docs or source show a configurable endpoint, a B2 option, or a generic S3-compatible option; "supports S3" is not enough. A tool used by several architectures is defined once and shared with a YAML alias. Connection types and their labels are shared across the B2 category repos (see `CONNECTION_LABELS` in `tools/generate_catalog.py`); using a value not yet in this repo means adding it to the schema enum and `CONNECTION_LABELS` together.
- New sample application: build it in its own repository (for example under `backblaze-b2-samples`) and add a `samples:` entry with `group`, `summary`, `description` and, where it fits, `architectures` and `relevance`.
- Regenerate `README.md`, `docs/related-b2-samples.md`, `docs/architecture-index.md`, `skill/references/architecture-catalog.md`, `llms.txt` and `llms-full.txt` in the same change.

Content rules: attribute to a vendor only what its docs or code show; label B2-side patterns as such; never hardcode a region or endpoint; link B2 pricing instead of quoting numbers.
Security: no real keys anywhere; secrets in gitignored `0600` `.env`; scoped keys, not master, unless provisioning requires it (say so).
Tests: `python3 tools/generate_catalog.py --check`, `python3 tools/check_markdown_links.py`, and `python3 -m pytest tests`. Run `python3 tools/check_markdown_links.py --external` when adding outbound links.
