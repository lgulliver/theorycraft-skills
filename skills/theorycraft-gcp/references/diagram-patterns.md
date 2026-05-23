# GCP Architecture Diagram Patterns

## Mermaid Templates

### GKE with Shared VPC and data project
```mermaid
graph TD
    subgraph Org["GCP Organisation"]
        subgraph HostProj["Host Project"]
            VPC[Shared VPC\n10.0.0.0/16]
        end
        subgraph AppProj["Application Project"]
            GKE[GKE Autopilot]
            CR[Cloud Run]
        end
        subgraph DataProj["Data Project"]
            SQL[(Cloud SQL\nPostgreSQL)]
            GCS[(Cloud Storage)]
            SM[Secret Manager]
        end
    end
    Internet --> GLB[Global HTTPS LB\n+ Cloud Armor]
    GLB --> GKE & CR
    GKE -->|Workload Identity| SQL & GCS & SM
    CR -->|Workload Identity| SQL & GCS
    VPC -.->|Shared VPC| GKE
```

### Event-driven data pipeline
```mermaid
flowchart LR
    Sources[Cloud Storage\nEvent] --> EA[Eventarc]
    EA --> CF[Cloud Functions]
    CF -.->|publish| PS[Pub/Sub Topic]
    PS --> DF[Dataflow Job]
    DF --> BQ[(BigQuery)]
    PS -.->|on failure| DLQ[Dead Letter Topic]
    BQ --> LS[Looker Studio]
```

### Multi-region HA with Cloud Spanner
```mermaid
graph TD
    subgraph Global["Global"]
        GLB[Global HTTPS LB]
        Spanner[(Cloud Spanner\nnam-eur-asia1)]
    end
    subgraph EUW2["europe-west2 (London)"]
        CR1[Cloud Run\nInstances]
        GCS1[(Cloud Storage)]
    end
    subgraph USE1["us-east1"]
        CR2[Cloud Run\nInstances]
        GCS2[(Cloud Storage)]
    end
    Internet --> GLB
    GLB -->|latency routing| CR1 & CR2
    CR1 & CR2 --> Spanner
    CR1 --> GCS1
    CR2 --> GCS2
```

### CI/CD pipeline on GCP
```mermaid
flowchart LR
    Dev[Developer] --> GH[GitHub]
    GH --> CB[Cloud Build]
    CB --> Trivy[Trivy Scan]
    Trivy --> AR[Artifact Registry]
    AR --> CD[Cloud Deploy]
    CD --> Staging[GKE Staging]
    CD -->|manual approval| Prod[GKE Prod]
    Staging & Prod --> SM[Secret Manager]
    Staging & Prod --> SQL[(Cloud SQL)]
```

---

## SVG Colour Reference

```
GCP Blue (compute):      #4285F4
GCP Green (data/storage):#34A853
GCP Yellow (messaging):  #FBBC04
GCP Red (security/IAM):  #EA4335
GCP Dark Green (network):#0F9D58
Neutral arrows:           #5F6368
VPC/project background:   #E8F0FE (light blue)
Subnet background:        #F1F8E9 (light green)
Project border:           #DADCE0 (light grey, solid)
Region label text:        #5F6368
```

## Common Layout Patterns

### GCP project hierarchy layout
Draw from top to bottom:
1. **Organisation node** — outer dashed rectangle, org domain label
2. **Folders** — grouping box (e.g. Production, Non-Production, Shared)
3. **Projects** — solid rounded rectangles within folders
4. **VPC** — dashed blue border within host project
5. **Subnets** — labelled regions with CIDR, nested in VPC

### Shared VPC topology
- **Host project** on the left with VPC clearly labelled
- **Service projects** on the right, each with their workloads
- Dashed bidirectional arrows labelled "Shared VPC" connecting service project workloads to host VPC
- Private Service Connect shown as a small endpoint box inside VPC with arrow to GCP API icon

### Data pipeline layout (left to right)
- **Ingestion sources** on the far left (Cloud Storage, Pub/Sub, Datastream)
- **Processing** in the middle (Dataflow, Cloud Functions, Dataproc)
- **Storage/serving** on the right (BigQuery, Bigtable, Spanner)
- Dead letter paths as red dashed arrows going down/out from processing layer
