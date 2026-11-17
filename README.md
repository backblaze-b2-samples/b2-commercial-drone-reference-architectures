# B2 reference architectures for commercial drones

How commercial drone teams use Backblaze B2 across field offload, photogrammetry, cloud-optimized map and 3D delivery, AI inspection, and inspection training data. Each architecture documents the data flow, B2 zones and security boundaries, and links out to the third-party integrations and B2 sample applications that implement it.

Learn more about [Backblaze B2 for AI and machine learning](https://www.backblaze.com/cloud-storage/industries/ai-ml).

Start with the [architecture index](docs/architecture-index.md) or the [agent-readable summary](docs/commercial-drones.md). Current B2 product behavior is documented at [backblaze.com/docs](https://www.backblaze.com/docs/cloud-storage).

## Where does Backblaze B2 fit for commercial drones?

B2 is the S3-compatible system of record for drone captures and everything derived from them. Size mission storage from image count, video bitrate and duration, generated survey products, and retention periods.

- **Store in B2:** raw stills, video, telemetry and flight logs with per-mission manifests. Also reconstruction products, COGs, COPC/EPT point clouds, meshes and splats, inspection results, and versioned training datasets and models.
- **Read in place from B2:** COGs through GDAL `/vsis3/` (TiTiler, QGIS, ArcGIS Pro, GeoServer); COPC and EPT through PDAL and Arbiter; Parquet through DuckDB. All use HTTP range requests.
- **Deliver from B2:** presigned URLs, included egress, and a Cloudflare CDN or signing Worker in front of the bucket.
- **Protect in B2:** Object Lock and legal hold for evidentiary captures and inspections, plus prefix-scoped field keys. Field write access can still hide objects or create new versions; use a trusted upload relay when strict append-only access is required.
- **Automate with B2:** prefix-filtered Event Notifications. A broker filters for `manifest.json` and starts processing.
- **Keep elsewhere:** SfM scratch (local NVMe), job queues, mission and asset registries (Postgres/PostGIS), annotation databases, and tile caches.
- **Managed drone platforms:** for DJI FlightHub, DroneDeploy, PIX4Dcloud and Cesium ion workflows, export artifacts to an application or rclone relay that writes them to B2.

Pricing, egress terms and limits change: see [B2 pricing](https://www.backblaze.com/cloud-storage/pricing) and the [B2 docs](https://www.backblaze.com/docs/cloud-storage).

## Architectures

<!-- catalog:architectures:start -->
| Architecture | Purpose | Samples and setup |
|---|---|---|
| [Offload flight captures into a per-mission archive and trigger processing](architectures/flight-capture-offload/architecture.md) | After each flight, a field laptop, ground station or relay uploads stills, video, telemetry, flight logs and RTK/PPK files into a write-once per-mission prefix, writes manifest.json last, and a prefix-scoped B2 Event Notification starts downstream processing. | [OpenDroneMap Photogrammetry Pipeline](https://github.com/backblaze-b2-samples/opendronemap-photogrammetry-pipeline) · [B2 Event Broker](https://github.com/backblaze-b2-samples/b2-event-broker) · [B2 Browser Upload](https://github.com/backblaze-b2-samples/b2-browser-upload) · [setup](https://www.backblaze.com/docs/cloud-storage-integrate-rclone-with-backblaze-b2) |
| [Reconstruct orthomosaics, elevation models, point clouds and meshes from mission imagery](architectures/photogrammetry-processing/architecture.md) | Stateless CPU/GPU workers pull a mission's raw images from B2, run SfM/MVS with OpenDroneMap NodeODM or COLMAP on local NVMe scratch, and write orthomosaic, DSM/DTM, LAZ point cloud, textured mesh and quality report to an immutable per-run prefix. | [OpenDroneMap Photogrammetry Pipeline](https://github.com/backblaze-b2-samples/opendronemap-photogrammetry-pipeline) · [COLMAP Photogrammetry Archive](https://github.com/backblaze-b2-samples/colmap-photogrammetry-archive) · [B2 Event Broker](https://github.com/backblaze-b2-samples/b2-event-broker) · [setup](https://github.com/OpenDroneMap/NodeODM) |
| [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) | Orthomosaics, DEMs and index maps such as NDVI are converted to Cloud-Optimized GeoTIFFs in `cog/<mission-id>/` and read in place by TiTiler, QGIS, ArcGIS Pro, GeoServer and rasterio through HTTP range requests, with CDN or presigned client delivery and no stored tile pyramid. | [TiTiler COG Map Tiles](https://github.com/backblaze-b2-samples/titiler-cog-map-tiles) · [cloudflare-b2 (private bucket via Worker)](https://github.com/backblaze-b2-samples/cloudflare-b2) |
| [Convert point clouds and meshes into streamable 3D datasets for web viewers](architectures/point-cloud-3d-streaming/architecture.md) | PDAL and Entwine clean, classify and convert photogrammetric and drone-LiDAR point clouds to COPC or EPT on B2 through s3:// paths, meshes and Gaussian splats for site digital twins are versioned alongside, and browser viewers stream them by range request from a public bucket or CDN. | [Open3D Point Cloud Pipeline](https://github.com/backblaze-b2-samples/open3d-point-cloud-pipeline) · [COLMAP Gaussian Splatting Pipeline](https://github.com/backblaze-b2-samples/colmap-gaussian-splatting-pipeline) · [cloudflare-b2 (private bucket via Worker)](https://github.com/backblaze-b2-samples/cloudflare-b2) · [IfcOpenShell BIM Archive](https://github.com/backblaze-b2-samples/ifcopenshell-bim-archive) · [setup](https://pdal.io) |
| [Detect and geolocate defects in inspection imagery and video](architectures/ai-inspection-detection/architecture.md) | YOLO or Roboflow Inference models scan inspection video and stills of towers, lines, solar farms, blades, bridges and roofs; geotagged detections, annotated keyframes, GeoJSON and Parquet roll-ups land in `inspections/<asset-id>/<inspection-id>/<model-version>/` and DuckDB queries them in place. | [YOLO Drone Footage Detection](https://github.com/backblaze-b2-samples/yolo-drone-footage-detection) · [Roboflow Inference Frame Archive](https://github.com/backblaze-b2-samples/roboflow-inference-frame-archive) · [YOLO11 Batch Detection Pipeline](https://github.com/backblaze-b2-samples/yolo11-batch-detection-pipeline) · [DuckDB Query In Place](https://github.com/backblaze-b2-samples/duckdb-query-in-place) · [B2 Event Broker](https://github.com/backblaze-b2-samples/b2-event-broker) |
| [Label inspection frames and publish versioned defect-detection datasets](architectures/inspection-training-data/architecture.md) | Flagged frames and orthomosaic chips are deduplicated, pre-labeled with SAM 2 or labeled in CVAT or Label Studio directly against B2, and exported as immutable dataset versions under `datasets/<name>/<version>/` next to versioned model checkpoints. | [SAM 2 Mask Dataset Builder](https://github.com/backblaze-b2-samples/sam2-mask-dataset-builder) · [fastdup Dataset Cleaning](https://github.com/backblaze-b2-samples/fastdup-dataset-cleaning) · [setup](https://docs.cvat.ai/docs/workspace/attach-cloud-storage/) |
<!-- catalog:architectures:end -->

## Third-party integrations

Each row identifies a native B2 backend, a configurable S3 endpoint, or a CDN origin configuration, with links to the relevant setup documentation. Use the listed connection method, bucket region, and credential scope for each integration.

<!-- catalog:integrations:start -->
| Tool | Role | Connection type | How it connects to B2 | Architectures |
|---|---|---|---|---|
| [rclone](https://rclone.org/b2/) | Resumable, checksum-verified field offload and staging of inputs and exported products for desktop photogrammetry tools without S3 support | Built-in Backblaze B2 option | Configure the native `b2` backend with an application key ID and key scoped to the crew's prefix (write and list); `rclone copy` resumes, skips files already in B2 and verifies SHA-1 on upload. The S3 backend with provider Other and endpoint `https://s3.<region>.backblazeb2.com` also works ([setup guide](https://www.backblaze.com/docs/cloud-storage-integrate-rclone-with-backblaze-b2)) | [Offload flight captures into a per-mission archive and trigger processing](architectures/flight-capture-offload/architecture.md), [Reconstruct orthomosaics, elevation models, point clouds and meshes from mission imagery](architectures/photogrammetry-processing/architecture.md) |
| [AWS SDK for Python (boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/core/session.html) | Presigned PUT/GET URLs, managed multipart upload and pipeline I/O in custom field portals and inference workers | S3 custom endpoint | Set endpoint_url to `https://s3.<region>.backblazeb2.com` derived from B2_REGION, and set request_checksum_calculation and response_checksum_validation to `when_required` in botocore Config; worker code uses boto3 to read frames and write inference results for Ultralytics and Roboflow ([setup guide](https://www.backblaze.com/docs/cloud-storage-use-the-aws-sdk-for-python-with-backblaze-b2)) | [Offload flight captures into a per-mission archive and trigger processing](architectures/flight-capture-offload/architecture.md), [Reconstruct orthomosaics, elevation models, point clouds and meshes from mission imagery](architectures/photogrammetry-processing/architecture.md), [Detect and geolocate defects in inspection imagery and video](architectures/ai-inspection-detection/architecture.md) |
| [OpenDroneMap NodeODM](https://github.com/OpenDroneMap/NodeODM) | Photogrammetry processing node producing orthophoto, DEM, point cloud and textured mesh | S3 custom endpoint | Start NodeODM with --s3_endpoint `s3.<region>.backblazeb2.com`, a dedicated client staging bucket, --s3_upload_everything and --s3_acl none; supply credentials through AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY. The staging key has no name prefix because startup writes root test.txt and results use task-ID paths ([setup guide](https://github.com/OpenDroneMap/NodeODM/blob/master/config.js)) | [Reconstruct orthomosaics, elevation models, point clouds and meshes from mission imagery](architectures/photogrammetry-processing/architecture.md) |
| [GDAL /vsis3/](https://gdal.org/en/stable/user/virtual_file_systems.html) | Range-read and write raster access underlying COG conversion, TiTiler, QGIS and rasterio | S3 custom endpoint | Set `AWS_S3_ENDPOINT=s3.<region>.backblazeb2.com` (host only), AWS_REGION, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY; set AWS_VIRTUAL_HOSTING=FALSE for bucket names that contain dots ([setup guide](https://gdal.org/en/stable/user/virtual_file_systems.html#vsis3-aws-s3-files)) | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) |
| [Rasterio / rio-cogeo](https://github.com/rasterio/rasterio) | Python raster I/O and COG creation | S3 custom endpoint | Pass rasterio.session.AWSSession(endpoint_url="s3.<region>.backblazeb2.com") to rasterio.Env, or set GDAL's AWS_S3_ENDPOINT; rio cogeo create writes COGs straight to /vsis3/ paths ([setup guide](https://github.com/rasterio/rasterio/blob/main/rasterio/session.py)) | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) |
| [TiTiler](https://github.com/developmentseed/titiler) | Dynamic XYZ/WMTS tile server over COGs | S3 custom endpoint | Set GDAL's AWS_S3_ENDPOINT, AWS_REGION and a read-only key in the TiTiler container environment; TiTiler reads COGs through GDAL /vsis3/ ([setup guide](https://github.com/backblaze-b2-samples/titiler-cog-map-tiles)) | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) |
| [QGIS](https://qgis.org) | Desktop GIS viewing and analysis of COGs in place | S3 custom endpoint | Add a raster layer with protocol type AWS S3 and set AWS_S3_ENDPOINT in its credential options, or set the GDAL AWS variables globally under Settings > Options > Variables ([setup guide](https://docs.qgis.org/latest/en/docs/user_manual/managing_data_source/opening_data.html)) | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) |
| [Esri ArcGIS Pro (cloud storage connection file)](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/data-management/create-cloud-storage-connection-file.html) | Desktop GIS access to rasters in object storage | S3 custom endpoint | Run Create Cloud Storage Connection File with service provider Amazon, the bucket name, a read-only key and Service End Point `s3.<region>.backblazeb2.com`; Esri documents the custom endpoint for S3-compatible storage | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) |
| [GeoServer COG community module](https://docs-archive.geoserver.org/stable/en/user/community/cog/cog.html) | OGC WMS/WMTS serving of COGs | S3 custom endpoint | Set IIO_<SCHEME>_AWS_ENDPOINT to `https://s3.<region>.backblazeb2.com`, where <SCHEME> matches the layer URL (S3 for s3://, HTTPS for https://), plus _AWS_USER, _AWS_PASSWORD and _AWS_REGION; install the COG community module | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md) |
| [Cloudflare CDN and Workers](https://www.backblaze.com/docs/cloud-storage-cloudflare-integrations) | Edge cache and request signing for public or private map and 3D tile delivery | CDN origin | Point Cloudflare at the B2 bucket as origin; for private buckets, deploy a Worker that signs S3 requests with a scoped read-only key and passes range requests through ([setup guide](https://github.com/backblaze-b2-samples/cloudflare-b2)) | [Serve orthomosaics and elevation models as cloud-optimized map layers](architectures/cog-map-serving/architecture.md), [Convert point clouds and meshes into streamable 3D datasets for web viewers](architectures/point-cloud-3d-streaming/architecture.md) |
| [PDAL](https://pdal.io) | Point cloud filtering, classification, reprojection and COPC writing | S3 custom endpoint | Set AWS_ENDPOINT_URL=`s3.<region>.backblazeb2.com` (host only; Arbiter prepends https://) or an endpoint key in Arbiter's JSON config; PDAL then reads and writes s3:// paths ([setup guide](https://github.com/PDAL/PDAL/blob/master/vendor/arbiter/arbiter.cpp)) | [Convert point clouds and meshes into streamable 3D datasets for web viewers](architectures/point-cloud-3d-streaming/architecture.md) |
| [Entwine](https://github.com/connormanning/entwine) | EPT index builder for very large or multi-flight point clouds | S3 custom endpoint | Set AWS_ENDPOINT_URL=`s3.<region>.backblazeb2.com` (host only, no scheme); Entwine reads and writes s3:// paths through Arbiter ([setup guide](https://github.com/connormanning/arbiter/blob/master/arbiter/drivers/s3.cpp)) | [Convert point clouds and meshes into streamable 3D datasets for web viewers](architectures/point-cloud-3d-streaming/architecture.md) |
| [DuckDB httpfs](https://duckdb.org/docs/current/core_extensions/httpfs/s3api.html) | SQL over detection Parquet in place and materialized result slices | S3 custom endpoint | CREATE SECRET of TYPE s3 with ENDPOINT `s3.<region>.backblazeb2.com`, REGION and a scoped key; DuckDB reads Parquet row groups by range and writes results back with COPY | [Detect and geolocate defects in inspection imagery and video](architectures/ai-inspection-detection/architecture.md) |
| [CVAT](https://docs.cvat.ai/docs/workspace/attach-cloud-storage/) | Image and video annotation with task data read from and exports written to B2 | S3 custom endpoint | Attach cloud storage with provider Amazon S3, key ID and secret access key pair, and Endpoint URL `https://s3.<region>.backblazeb2.com`, as in CVAT's Backblaze B2 guide ([setup guide](https://docs.cvat.ai/docs/workspace/attach-cloud-storage/#attach-backblaze-b2-storage)) | [Label inspection frames and publish versioned defect-detection datasets](architectures/inspection-training-data/architecture.md) |
| [Label Studio](https://labelstud.io/guide/storage_s3) | Annotation with S3 source storage for media and target storage for labels | S3 custom endpoint | Set the S3 Endpoint field on source and target storage to `https://s3.<region>.backblazeb2.com`; serve media by presigned URLs (configure bucket CORS) or proxy it through Label Studio | [Label inspection frames and publish versioned defect-detection datasets](architectures/inspection-training-data/architecture.md) |
<!-- catalog:integrations:end -->

Vendor-cloud and desktop workflows use an export relay: stage completed mission files, then upload them to B2 with rclone or an SDK. Potree, CesiumJS, and COPC viewers read the published products through HTTP URLs; see [point-cloud delivery](architectures/point-cloud-3d-streaming/architecture.md).

## Sample applications

Sample applications from [`backblaze-b2-samples`](https://github.com/backblaze-b2-samples) demonstrating these storage workflows. Follow the linked repositories for source code, setup, and operating instructions.

<!-- catalog:samples:start -->
| Sample | Demonstrates | Related architectures |
|---|---|---|
| [OpenDroneMap Photogrammetry Pipeline](https://github.com/backblaze-b2-samples/opendronemap-photogrammetry-pipeline) | Presigned-PUT drone photo upload, local NodeODM reconstruction, and managed multipart write-back of orthomosaic, DEM, point cloud and mesh | [flight-capture-offload](architectures/flight-capture-offload/architecture.md), [photogrammetry-processing](architectures/photogrammetry-processing/architecture.md) |
| [YOLO Drone Footage Detection](https://github.com/backblaze-b2-samples/yolo-drone-footage-detection) | Multipart video ingest, Ultralytics YOLO keyframe detection, GPX/SRT geotagging and a GeoJSON track on B2 | [ai-inspection-detection](architectures/ai-inspection-detection/architecture.md) |
| [TiTiler COG Map Tiles](https://github.com/backblaze-b2-samples/titiler-cog-map-tiles) | GeoTIFF-to-COG conversion and dynamic XYZ tiles through GDAL /vsis3/ range reads with no stored tile copy | [cog-map-serving](architectures/cog-map-serving/architecture.md) |
| [Roboflow Inference Frame Archive](https://github.com/backblaze-b2-samples/roboflow-inference-frame-archive) | Edge inference that archives only flagged frames and prediction JSON, with hourly Parquet roll-ups | [ai-inspection-detection](architectures/ai-inspection-detection/architecture.md) |
| [YOLO11 Batch Detection Pipeline](https://github.com/backblaze-b2-samples/yolo11-batch-detection-pipeline) | Batch detection and segmentation over a B2 image and video library, writing COCO JSON, annotated frames and crops | [ai-inspection-detection](architectures/ai-inspection-detection/architecture.md) |
| [Open3D Point Cloud Pipeline](https://github.com/backblaze-b2-samples/open3d-point-cloud-pipeline) | PLY/PCD/LAS/LAZ ingest, downsampling, registration and meshing with a job manifest on B2 | [point-cloud-3d-streaming](architectures/point-cloud-3d-streaming/architecture.md) |
| [COLMAP Photogrammetry Archive](https://github.com/backblaze-b2-samples/colmap-photogrammetry-archive) | pycolmap SfM that archives photos, database, sparse model and point cloud per project, served by presigned URL | [photogrammetry-processing](architectures/photogrammetry-processing/architecture.md) |
| [COLMAP Gaussian Splatting Pipeline](https://github.com/backblaze-b2-samples/colmap-gaussian-splatting-pipeline) | Photos or video to a COLMAP reconstruction and a Nerfstudio/gsplat-ready bundle versioned on B2 | [point-cloud-3d-streaming](architectures/point-cloud-3d-streaming/architecture.md) |
| [SAM 2 Mask Dataset Builder](https://github.com/backblaze-b2-samples/sam2-mask-dataset-builder) | Versioned segmentation datasets built from a raw B2 media archive with local SAM 2 | [inspection-training-data](architectures/inspection-training-data/architecture.md) |
| [fastdup Dataset Cleaning](https://github.com/backblaze-b2-samples/fastdup-dataset-cleaning) | Duplicate, outlier and corrupt-file detection with quality reports and quarantine without deleting originals | [inspection-training-data](architectures/inspection-training-data/architecture.md) |
| [DuckDB Query In Place](https://github.com/backblaze-b2-samples/duckdb-query-in-place) | SQL over Parquet, CSV and JSON in B2 through DuckDB httpfs, materializing results back as Parquet | [ai-inspection-detection](architectures/ai-inspection-detection/architecture.md) |
| [B2 Event Broker](https://github.com/backblaze-b2-samples/b2-event-broker) | Cloudflare Worker that validates signed B2 Event Notifications and fans them out to subscribers | [flight-capture-offload](architectures/flight-capture-offload/architecture.md), [photogrammetry-processing](architectures/photogrammetry-processing/architecture.md), [ai-inspection-detection](architectures/ai-inspection-detection/architecture.md) |
| [cloudflare-b2 (private bucket via Worker)](https://github.com/backblaze-b2-samples/cloudflare-b2) | Cloudflare Worker that signs range requests to a private B2 bucket for CDN delivery | [cog-map-serving](architectures/cog-map-serving/architecture.md), [point-cloud-3d-streaming](architectures/point-cloud-3d-streaming/architecture.md) |
| [B2 Browser Upload](https://github.com/backblaze-b2-samples/b2-browser-upload) | Browser-direct upload by S3 presigned PUT or b2_upload_file through a Node.js back end (5 GB single-upload cap) | [flight-capture-offload](architectures/flight-capture-offload/architecture.md) |
<!-- catalog:samples:end -->

See the [full sample cross-reference](docs/related-b2-samples.md) for domain candidates and selection guidance.

## B2 capability map

| Area | Capabilities | Selection notes |
|---|---|---|
| Access | S3 API with regional endpoint, presigned URLs, CORS, multipart, HTTP range GETs, scoped keys (one bucket + one prefix + capabilities) | Derive `https://s3.<region>.backblazeb2.com` from the bucket region. Multipart is required above 5 GB. Give field crews write-only keys |
| Change and lifecycle | Event Notifications, versions, lifecycle (hide, then delete; cancel unfinished large uploads) | Rules filter by prefix only, so filter for `manifest.json` in the broker. Event Notifications are enabled through Support. B2 has no storage tiers |
| Protection | SSE-B2, Object Lock (governance/compliance), legal hold, Cloud Replication | Lock evidentiary captures and inspections. Object Lock must be enabled on the bucket. Replication is bucket-to-bucket DR, not delivery |
| Delivery | Included egress, Cloudflare CDN origin, signing Worker, presigned GET | Presigned GET for single files. Use a CDN or Worker for multi-file tilesets and public basemaps |
| Performance | Standard B2, [Overdrive](https://www.backblaze.com/cloud-storage/b2-overdrive), local cache | Standard B2 by default. Local NVMe for SfM scratch and training shards. Overdrive only for measured, sustained high-throughput reads |

<!-- catalog:related:start -->
Other B2 reference architecture categories: [AI Data Providers](https://github.com/backblaze-b2-samples/b2-ai-data-provider-reference-architectures), [Generative Video](https://github.com/backblaze-b2-samples/b2-gen-video-reference-architectures), [Image Generation](https://github.com/backblaze-b2-samples/b2-image-generation-reference-architectures), [Robotics](https://github.com/backblaze-b2-samples/b2-robotics-reference-architectures), [Autonomous Vehicles](https://github.com/backblaze-b2-samples/b2-autonomous-vehicle-reference-architectures).
<!-- catalog:related:end -->

[Backblaze B2 documentation](https://www.backblaze.com/docs/cloud-storage) is canonical for product behavior; this repository provides workflow-specific designs.

## Repository layout

- `catalog/`: architecture, integration and sample metadata.
- `schemas/`: the catalog schema.
- `architectures/`: docs and Mermaid diagrams.
- `docs/`: agent-readable pages.
- `examples/`: B2 configs.
- `skill/`: portable agent skill.
- `tools/`: generator and link checker.
- `tests/`: tool tests.
- `.github/`: CI and templates.

## Validate locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements-catalog.txt pytest
python3 tools/generate_catalog.py --check
python3 tools/check_markdown_links.py            # add --external to probe outbound links
python3 -m pytest tests
```

## Contributing, security and license

See [CONTRIBUTING](.github/CONTRIBUTING.md); the catalog is the extension point. Report sensitive issues through the [security policy](.github/SECURITY.md). Released under the [MIT license](LICENSE); cite with [CITATION.cff](CITATION.cff).
