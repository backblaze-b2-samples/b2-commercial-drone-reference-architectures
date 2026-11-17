---
name: b2-commercial-drone
description: Design or review Backblaze B2 storage for commercial drone data, covering flight capture offload, OpenDroneMap/COLMAP photogrammetry, COG map serving with GDAL/TiTiler/QGIS/ArcGIS/GeoServer, PDAL/Entwine COPC and EPT point cloud streaming, YOLO/Roboflow inspection with DuckDB, and CVAT/Label Studio training data. Use it for mission object layout, key scoping, event-driven processing, Object Lock for evidence, and CDN or presigned delivery.
---

# B2 for commercial drones

Choose a workflow from the bundled [architecture catalog](references/architecture-catalog.md). It also lists related B2 sample applications.

For changing service behavior, limits and setup steps, use the canonical [Backblaze B2 documentation](https://www.backblaze.com/docs/cloud-storage). Link pricing and egress claims to [B2 pricing](https://www.backblaze.com/cloud-storage/pricing) instead of copying numbers.

## Rules

### Credentials and endpoints
- Use the S3-compatible API. Derive `https://s3.<region>.backblazeb2.com` from `B2_REGION`; never hardcode a region or endpoint.
- Env vars: `B2_APPLICATION_KEY_ID`, `B2_APPLICATION_KEY`, `B2_BUCKET_NAME`, `B2_REGION`, and optionally `B2_ENDPOINT`. Keep secrets in a gitignored `0600` `.env`, and never print keys.
- A key scopes to one bucket, one prefix and a set of capabilities.
  - Field crews get write-and-list keys on `raw/<client>/` without object reads or permanent version deletion. `writeFiles` still permits hiding or creating a new version. Strict append-only access needs a trusted upload relay that allocates fresh authorized keys and refuses replacements; presigned PUTs can be replayed until expiry.
  - Processing reads `raw/` and writes `products/`. Viewers and tile servers are read-only on `cog/`.
  - Use the master key only for provisioning.
- Bucket names are globally unique, so expect collisions.

### Layout and events
- Object layout:
  - `raw/<client>/<site>/<mission-id>/` with `manifest.json` written last.
  - `products/<mission-id>/<run-id>/`, `cog/<mission-id>/`, `pointcloud/...`, `twins/...` and `inspections/<asset-id>/<inspection-id>/<model-version>/`.
  - `datasets/<name>/<version>/` and `models/<name>/<version>/`.
  - Never overwrite a run, an inspection or a dataset version.
- Event Notifications filter by prefix only. They are enabled through Backblaze Support, and signing is optional. The receiver filters for `*/manifest.json`, verifies the signature, and stays idempotent.
- Multipart is required above 5 GB, so presigned single PUTs are for stills only.
- Lifecycle uses B2 semantics: hide then delete by age, and cancel unfinished large uploads. There are no tiers. Object Lock must be enabled on the bucket. Use governance mode by default; compliance mode is irreversible.

### Tools
- **rclone:** native B2 backend; use `copy`, not `sync`, for field offload.
- **NodeODM:** `--s3_endpoint s3.<region>.backblazeb2.com` and `--s3_acl none`. Use a dedicated client staging bucket with no key-prefix restriction for the root probe and task-ID layout. Publish verified outputs to `products/` with separate credentials.
- **GDAL, rasterio, TiTiler:** `AWS_S3_ENDPOINT` (host only) and `AWS_REGION`. TiTiler accepts validated layer ids, never URLs.
- **QGIS:** an AWS S3 raster layer with `AWS_S3_ENDPOINT` in its credential options, or global GDAL `AWS_*` variables.
- **ArcGIS Pro:** a cloud storage connection file with service provider Amazon and the B2 endpoint as Service End Point.
- **GeoServer:** the COG community module with `IIO_S3_AWS_ENDPOINT`.
- **PDAL and Entwine:** Arbiter with `AWS_ENDPOINT_URL=s3.<region>.backblazeb2.com` (host only; Arbiter prepends `https://`) and `AWS_REGION`.
- **DuckDB:** an httpfs secret with `ENDPOINT`.
- **CVAT:** CVAT's Backblaze B2 guide: provider Amazon S3 with the B2 Endpoint URL.
- **Label Studio:** the S3 Endpoint field, with presigned URLs and CORS, or proxy mode.
- **Ultralytics and Roboflow:** no B2 connector. Worker code uses boto3.
- **Vendor-cloud exports:** stage completed files in a relay and upload them with scoped B2 application keys. Use the provider's documented export workflow; IAM-enabled B2 accounts can use temporary role credentials where the integration supports them.

### Delivery and scope
- Delivery: presigned GET for single files, and a Cloudflare CDN or signing Worker for tilesets and basemaps. Cloud Replication is bucket-to-bucket DR, not delivery.
- Keep SfM scratch, queues, registries, spatial indexes, annotation databases and tile caches off B2.
- Use Overdrive only for measured, sustained high-throughput reads. Otherwise use Standard B2.

## Verify

Inside the full repository, use the validation commands in its `AGENTS.md`. When this skill is installed by itself, check recommendations against the linked canonical product and integration documentation; repository-local tests are not bundled with the portable skill.
