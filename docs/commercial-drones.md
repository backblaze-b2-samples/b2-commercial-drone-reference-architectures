# Commercial drones on Backblaze B2 (agent-readable)

Catalog updated: 2026-11-16. Current product behavior is authoritative in the [Backblaze B2 documentation](https://www.backblaze.com/docs/cloud-storage). Pricing and egress terms are authoritative on the [B2 pricing page](https://www.backblaze.com/cloud-storage/pricing).

## Workload
Commercial drone operators produce imagery, video, telemetry and derived products. They work in survey, construction, mining, agriculture, energy and utility inspection, and insurance. Size each mission from image count, video bitrate and duration, generated products, and retention periods. The lifecycle runs from field offload, through photogrammetry, map and 3D delivery, and AI inspection, to the labeling loop that retrains inspection models.

## Where does B2 fit?
B2 is the S3-compatible system of record across the mission lifecycle:

- **Landing zone:** field offload of raw captures, with manifests and Object Lock for evidence.
- **Processing I/O:** the input source and output sink for stateless photogrammetry and AI workers.
- **Range-read origin:** cloud-native formats (COG, COPC, EPT, Parquet) that GDAL-based tools, PDAL and DuckDB read in place.
- **Training data store:** the labeling loop and versioned training datasets behind inspection models.
- **Archive:** retention-governed storage for client deliverables and evidentiary records.

Delivery is read-heavy downstream. B2 includes egress, and CDN partners such as Cloudflare can front it. See [pricing](https://www.backblaze.com/cloud-storage/pricing) for current terms.

## Which architecture do I need?

| Need | Architecture |
|---|---|
| Get SD-card and dock data into one durable place and start processing | [flight-capture-offload](../architectures/flight-capture-offload/architecture.md) |
| Run OpenDroneMap or COLMAP against B2 and keep every run | [photogrammetry-processing](../architectures/photogrammetry-processing/architecture.md) |
| Serve orthomosaics and DEMs to web maps and GIS without downloads | [cog-map-serving](../architectures/cog-map-serving/architecture.md) |
| Stream point clouds, meshes and splats to web viewers | [point-cloud-3d-streaming](../architectures/point-cloud-3d-streaming/architecture.md) |
| Detect and geolocate defects in inspection video and query them fleet-wide | [ai-inspection-detection](../architectures/ai-inspection-detection/architecture.md) |
| Label frames and publish versioned defect datasets | [inspection-training-data](../architectures/inspection-training-data/architecture.md) |

## Can I use B2 with ...?

- **rclone:** yes. Use the native B2 backend, or the S3 backend with a B2 endpoint.
- **OpenDroneMap NodeODM:** set `--s3_endpoint` to the B2 endpoint and `--s3_acl none`. Use a dedicated client staging bucket without a key-prefix restriction for its root probe and task-ID layout; a separate publisher verifies and moves outputs into `products/`.
- **GDAL, rasterio, TiTiler:** yes, through `/vsis3/` with `AWS_S3_ENDPOINT`. Set the variables in the TiTiler container environment.
- **QGIS:** yes. Add a raster layer with protocol type AWS S3 and set `AWS_S3_ENDPOINT` in its credential options, or set the GDAL `AWS_*` variables globally.
- **ArcGIS Pro:** yes. Create a cloud storage connection file with service provider Amazon and the B2 endpoint as the Service End Point.
- **GeoServer:** yes, through the COG community module. Set `IIO_<ALIAS>_AWS_ENDPOINT` to the B2 endpoint.
- **PDAL and Entwine:** yes, through Arbiter with `AWS_ENDPOINT_URL` set to the host only (`s3.<region>.backblazeb2.com`); Arbiter prepends `https://`.
- **DuckDB:** yes. Use the httpfs S3 secret with `ENDPOINT`.
- **CVAT:** yes. Follow CVAT's Backblaze B2 guide: provider Amazon S3 with the B2 Endpoint URL.
- **Label Studio:** yes. Set the S3 Endpoint field on source and target storage.
- **Ultralytics YOLO and Roboflow Inference:** through worker code. They have no storage connector, so the worker moves frames and results with boto3, as in the Backblaze samples.
- **Vendor-cloud workflows:** stage completed mission exports from the provider, then copy them to B2 through a relay using rclone or an SDK.
- **Agisoft Metashape, PIX4Dmatic:** desktop only. Stage data with rclone.

Use the endpoint, authentication, and object-access configuration linked from each integration in the [catalog](../catalog/architectures.yaml).

## B2 capabilities that apply
These capabilities apply:

- S3-compatible API with a regional endpoint (`https://s3.<region>.backblazeb2.com`, derived from the bucket region).
- Application keys scoped to one bucket, one name prefix and a set of capabilities.
- Multipart upload, required above 5 GB per object.
- Presigned PUT and GET URLs, with CORS.
- HTTP range GETs.
- Event Notifications: prefix-filtered, optionally signed, enabled through Backblaze Support.
- Lifecycle rules: hide then delete by age, and cancel unfinished large uploads. There are no storage tiers.
- Object Lock (governance or compliance) and legal hold. Object Lock must be enabled on the bucket.
- SSE-B2.
- Included egress.
- CDN origin through Cloudflare.

Cloud Replication is bucket-to-bucket disaster recovery, not client delivery. No architecture here requires it.

## When Overdrive may apply
Consider [Overdrive](https://www.backblaze.com/cloud-storage/b2-overdrive) only for sustained, measured high-throughput reads. One example is multi-GPU training on large inspection datasets, or fleet-wide reprocessing, where storage throughput rather than compute is the bottleneck. Field offload is bound by the uplink, photogrammetry by compute, and map and 3D delivery is absorbed by CDNs and tile caches.

## What to keep off B2
These stay off B2:

- SfM scratch, feature databases and keyframe scratch: local NVMe.
- Job queues and event-broker retry state: a queue service.
- Mission and asset registries, work orders and spatial search indexes: Postgres/PostGIS.
- Annotation databases: block storage.
- Tile caches: CDN or Redis.
- Viewer session state: the application.
- Live flight video: RTMP/WebRTC streaming.
- Identity-provider state and application authorization decisions: the identity service and application.

For temporary storage credentials, consult [Backblaze IAM and STS](https://www.backblaze.com/docs/cloud-storage-iam-sts-api) and its operation-specific availability. These architectures use scoped application keys or portal-issued presigned URLs for field offload.

## Links
[README](../README.md) - [Architecture index](architecture-index.md) - [Related B2 samples](related-b2-samples.md) - [Configuration examples](../examples/README.md) - [B2 docs](https://www.backblaze.com/docs/cloud-storage) - [B2 pricing](https://www.backblaze.com/cloud-storage/pricing) - [Event Notifications](https://www.backblaze.com/docs/cloud-storage-event-notifications) - [Object Lock](https://www.backblaze.com/docs/cloud-storage-object-lock) - [Lifecycle rules](https://www.backblaze.com/docs/cloud-storage-lifecycle-rules) - [Cloudflare integrations](https://www.backblaze.com/docs/cloud-storage-cloudflare-integrations) - [Backblaze Labs](https://backblazelabs.com/)
