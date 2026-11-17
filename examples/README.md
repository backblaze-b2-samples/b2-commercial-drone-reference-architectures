# B2 configuration examples

Configuration templates for the buckets in these [reference architectures](../docs/architecture-index.md). Run command blocks from this repository's `examples/` directory using Bash and the B2 CLI v4. Authenticate the CLI with a provisioning credential before creating buckets or application keys. Configuration fields are documented in the [B2 API reference](https://www.backblaze.com/apidocs).

Set `ORG` to a globally unique bucket-name prefix. Set the additional variables used by the selected command block, and replace values shown in `<angle brackets>` before running it. Choose retention periods, lifecycle settings, and application-key capabilities for the workload; lifecycle rules permanently delete expired object versions.

| Variable | Purpose |
|---|---|
| `ORG` | Globally unique bucket-name prefix. |
| `CLIENT` | Internal client identifier used to isolate mission objects. |
| `CREW` | Crew identifier used in the field-key name. |
| `DEVICE` | Device identifier used to scope edge uploads. |

| File | Applies to | Purpose | Architectures |
|---|---|---|---|
| `event-notifications-raw.json` | raw bucket | Webhook on uploads under `raw/`; the broker keeps only `*/manifest.json` | [flight-capture-offload](../architectures/flight-capture-offload/architecture.md) |
| `event-notifications-products.json` | products bucket | Webhook on uploads under `products/`; the broker keeps only run `manifest.json` | [photogrammetry-processing](../architectures/photogrammetry-processing/architecture.md) |
| `lifecycle-raw.json` | raw bucket | Cancel unfinished large uploads; expire `staging/`. Raw captures are never hidden by age | [flight-capture-offload](../architectures/flight-capture-offload/architecture.md) |
| `lifecycle-nodeodm.json` | client NodeODM staging bucket | Expire task outputs after publication; cancel unfinished large uploads | [photogrammetry-processing](../architectures/photogrammetry-processing/architecture.md) |
| `lifecycle-products.json` | products bucket | Expire `staging/`, `query-slices/` and edge frames; purge hidden product versions. Mission `analysis/` deliverables have no age rule | [photogrammetry-processing](../architectures/photogrammetry-processing/architecture.md), [cog-map-serving](../architectures/cog-map-serving/architecture.md), [ai-inspection-detection](../architectures/ai-inspection-detection/architecture.md) |
| `lifecycle-ml.json` | ML bucket | Expire curation batches; purge hidden label versions | [inspection-training-data](../architectures/inspection-training-data/architecture.md) |
| `object-lock-evidence.json` | raw bucket (and products, if deliverables are locked) | Default governance retention on evidentiary captures and inspections | [flight-capture-offload](../architectures/flight-capture-offload/architecture.md), [ai-inspection-detection](../architectures/ai-inspection-detection/architecture.md) |
| `cors-field-portal.json` | raw bucket | Browser presigned PUT of stills from a field portal origin | [flight-capture-offload](../architectures/flight-capture-offload/architecture.md) |
| `cors-map-viewers.json` | products or public bucket | Browser range reads of COG, COPC and EPT from map and 3D viewer origins | [cog-map-serving](../architectures/cog-map-serving/architecture.md), [point-cloud-3d-streaming](../architectures/point-cloud-3d-streaming/architecture.md) |
| `cors-labeling.json` | ML bucket | Presigned media reads from a labeling tool origin | [inspection-training-data](../architectures/inspection-training-data/architecture.md) |

Retention periods and day counts are placeholders. Set them from your contracts, records policy and privacy obligations, because lifecycle rules delete data. B2 lifecycle rules only hide and then delete by age per prefix, and cancel unfinished large-file uploads. They do not tier storage and cannot keep the last K runs. Lifecycle never removes a file under active Object Lock retention or legal hold.

The CORS files allow only `s3_*` operations. That covers presigned S3 URLs. Add `b2_*` operations only if a client uses the B2 Native API.

```bash
# Buckets: names are globally unique. CLIENT is an internal identifier.
: "${ORG:?Set ORG to a globally unique prefix}"
: "${CLIENT:?Set CLIENT to the internal client identifier}"
b2 bucket create --file-lock-enabled "$ORG-drone-raw" allPrivate
b2 bucket create "$ORG-drone-products" allPrivate
b2 bucket create "$ORG-drone-nodeodm-$CLIENT" allPrivate
b2 bucket create --file-lock-enabled "$ORG-drone-ml" allPrivate   # Object Lock for released datasets/; no default retention
b2 bucket create "$ORG-drone-public" allPublic   # optional: cleared basemaps and tilesets only

# Default encryption, lifecycle, CORS, default retention
b2 bucket update --default-server-side-encryption SSE-B2 "$ORG-drone-raw"
b2 bucket update --lifecycle-rules "$(cat lifecycle-raw.json)" "$ORG-drone-raw"
b2 bucket update --lifecycle-rules "$(cat lifecycle-products.json)" "$ORG-drone-products"
b2 bucket update --lifecycle-rules "$(cat lifecycle-nodeodm.json)" "$ORG-drone-nodeodm-$CLIENT"
b2 bucket update --lifecycle-rules "$(cat lifecycle-ml.json)" "$ORG-drone-ml"
b2 bucket update --cors-rules "$(cat cors-field-portal.json)" "$ORG-drone-raw"
b2 bucket update --cors-rules "$(cat cors-map-viewers.json)" "$ORG-drone-public"
b2 bucket update --cors-rules "$(cat cors-labeling.json)" "$ORG-drone-ml"

# Event Notifications must first be enabled for the account by Backblaze Support. Then call the native API
# b2_set_bucket_notification_rules with event-notifications-*.json (the key needs writeBucketNotifications).
```

A bucket has one CORS rule set; merge rules when it serves several origins. The raw bucket has Object Lock enabled without default retention so ordinary captures remain deletable under policy. Apply retention or legal hold per evidentiary object. If every capture requires the same retention, opt in to a bucket default:

```bash
b2 bucket update --default-retention-mode governance --default-retention-period "365 days" "$ORG-drone-raw"
```

Publish and verify NodeODM outputs before the staging lifecycle expires them.

## Scoped application keys

Each key is restricted to its required bucket, capabilities, and optional name prefix. NodeODM uses its dedicated client bucket without a prefix restriction. Field devices and browsers should receive presigned URLs from a service that holds the key wherever possible.

`writeFiles` permits hiding objects and creating new versions; withholding `deleteFiles` prevents permanent version deletion. Presigned PUTs limit the method and key but remain reusable until expiry. Use a trusted upload relay that allocates fresh keys and refuses replacements when strict append-only access is required.

```bash
# Field offload: write and list, no object reads or permanent version deletion.
# rclone needs listFiles to skip existing files; drop it and use --no-check-dest
# to avoid listing. writeFiles still allows hiding objects and writing new versions.
b2 key create --bucket "$ORG-drone-raw" --name-prefix "raw/$CLIENT/" "crew-$CREW"     listFiles,writeFiles
b2 key create --bucket "$ORG-drone-raw" --name-prefix raw/           portal-signer     writeFiles

# Processing
b2 key create --bucket "$ORG-drone-raw"      --name-prefix "raw/$CLIENT/" "processing-reader-$CLIENT" listFiles,readFiles
b2 key create --bucket "$ORG-drone-nodeodm-$CLIENT" "nodeodm-writer-$CLIENT" listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-nodeodm-$CLIENT" "nodeodm-reader-$CLIENT" listFiles,readFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix products/    products-writer   listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix cog/         cog-writer        listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix pointcloud/  pdal-writer       listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix inspections/ inference-writer  listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix detections/  rollup-writer     listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix analysis/    analytics-writer  listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix query-slices/ slice-writer     listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix "edge/$DEVICE/"      "edge-$DEVICE"           writeFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix "summaries/$DEVICE/" "edge-summaries-$DEVICE" writeFiles

# Delivery and analysis (read-only)
b2 key create --bucket "$ORG-drone-products" --name-prefix cog/        tiles-reader      listFiles,readFiles
# One prefix per key, so analysts reading detections/ and summaries/ hold two keys.
b2 key create --bucket "$ORG-drone-products" --name-prefix detections/ analyst-detections listFiles,readFiles
b2 key create --bucket "$ORG-drone-products" --name-prefix summaries/  analyst-summaries  listFiles,readFiles

# Labeling and training
b2 key create --bucket "$ORG-drone-ml" --name-prefix curation/candidates/ labeling-source listBuckets,listFiles,readFiles
b2 key create --bucket "$ORG-drone-ml" --name-prefix labels/reviewed/     labeling-target listBuckets,listFiles,readFiles,writeFiles
b2 key create --bucket "$ORG-drone-ml" --name-prefix datasets/            dataset-publisher listFiles,readFiles,writeFiles,writeFileRetentions
```

`b2 key create` prints the secret once. Store it in a gitignored `0600` file, never in shell history or logs. Bucket, lifecycle, retention, CORS and notification changes need an administrative key (or the master key). Run them once from provisioning and keep that key out of field devices and runtime services. A curation or promotion job that copies between buckets (for example, `inspections/` frames into the ML bucket) needs read access on one bucket and write access on the other. Use two clients with two keys, rather than widening a runtime key.
