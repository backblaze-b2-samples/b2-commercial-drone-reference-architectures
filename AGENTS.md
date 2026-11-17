# Agent guide

Use this repository to design or review storage workflows for commercial drone data on Backblaze B2: flight capture offload, photogrammetry, cloud-optimized map and 3D delivery, AI inspection and inspection training data.

<!-- CODEGRAPH_START -->
## CodeGraph

When a `.codegraph/` directory exists at the repository root, use `codegraph explore "<question or symbols>"` before grep, find, or broad file reads when locating or understanding code. If the directory does not exist, skip CodeGraph; indexing is a maintainer decision.
<!-- CODEGRAPH_END -->

## Sources of truth

1. `catalog/architectures.yaml` is the machine-readable catalog of architectures, third-party integrations (with `connection_type`) and external sample applications.
2. `schemas/architecture-catalog.schema.json` validates the catalog.
3. `architectures/*/architecture.md` contains the detailed design, B2 zones and security boundaries.
4. `examples/` contains B2 configuration templates.
5. Current Backblaze product behavior is authoritative at <https://www.backblaze.com/docs/cloud-storage>. Pricing is authoritative at <https://www.backblaze.com/cloud-storage/pricing>.

Describe the documented connection for each integration: a B2 backend or provider preset, a custom S3 endpoint, presigned URLs, or an application worker using an SDK. Specify the endpoint, region, addressing style, required operations, and credential scope. Attribute product capabilities to the linked vendor documentation or source code. Describe sample applications by the workflow they implement. Use `native-b2-option` for an actual B2 backend or B2-specific provider preset; use `s3-custom-endpoint` for a configurable S3 connection.

For a single-file read of the summary and every architecture, use `llms-full.txt`.

## Generated files

Run `python3 tools/generate_catalog.py` after editing the catalog. Do not hand-edit generated sections in `README.md`, `docs/related-b2-samples.md`, `docs/architecture-index.md`, `skill/references/architecture-catalog.md`, `llms.txt`, or `llms-full.txt`. `llms-full.txt` concatenates narrative pages, so regenerate after editing `docs/commercial-drones.md` or any `architecture.md`.

Validate generated output with:

```bash
python3 tools/generate_catalog.py --check
python3 tools/check_markdown_links.py            # add --external to probe outbound links
python3 -m pytest tests
```

## Operational invariants

- Derive `https://s3.<region>.backblazeb2.com` from the bucket region; do not hardcode a real region.
- Use application keys scoped to one bucket, one prefix and the needed capabilities. Field write-and-list keys deny object reads and permanent version deletion, but `writeFiles` still permits hiding objects or writing new versions. Strict append-only access needs a trusted upload relay that allocates new authorized keys and refuses replacements; presigned PUTs can be replayed until expiry. Keep master or administrative keys out of field devices and runtime services.
- Write `manifest.json` last as the completion marker; B2 Event Notification rules filter by prefix only, so the event receiver filters for the manifest key.
- Keep runs, inspections and dataset versions immutable under new prefixes; never overwrite.
- Keep SfM scratch, queues, registries, annotation databases, spatial indexes and tile caches off object storage.
- Set `--s3_acl none` for NodeODM; its default ACL is `public-read`.
- Treat presigned URLs as bearer credentials. Never commit credentials, customer imagery or real presigned URLs.
