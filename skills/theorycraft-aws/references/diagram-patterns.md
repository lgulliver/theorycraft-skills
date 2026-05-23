# AWS Architecture Diagram Patterns

## Mermaid Templates

### Three-tier VPC (public / private / isolated)
```mermaid
graph TD
    subgraph AWS["AWS Account (eu-west-2)"]
        subgraph VPC["VPC (10.0.0.0/16)"]
            subgraph AZA["Availability Zone A"]
                ALB_A[ALB Node]
                ECS_A[ECS Task]
                RDS_A[(RDS Primary)]
            end
            subgraph AZB["Availability Zone B"]
                ALB_B[ALB Node]
                ECS_B[ECS Task]
                RDS_B[(RDS Standby)]
            end
        end
        S3[(S3)]
        SM[Secrets Manager]
        CW[CloudWatch]
    end
    Internet --> ALB_A & ALB_B
    ALB_A --> ECS_A
    ALB_B --> ECS_B
    ECS_A & ECS_B --> RDS_A
    RDS_A -.->|sync replication| RDS_B
    ECS_A & ECS_B --> S3
    ECS_A & ECS_B --> SM
```

### Event-driven pipeline
```mermaid
flowchart LR
    Client --> APIGW[API Gateway]
    APIGW --> Lambda1[Lambda Ingest]
    Lambda1 -.->|async| SQS[SQS Queue]
    SQS --> Lambda2[Lambda Worker]
    SQS -.->|on failure| DLQ[Dead Letter Queue]
    Lambda2 --> DDB[(DynamoDB)]
    Lambda2 --> S3[(S3)]
    Lambda1 --> EB[EventBridge]
    EB --> Lambda3[Lambda Notify]
    Lambda3 --> SNS[SNS → Email/SMS]
```

### EKS with supporting services
```mermaid
graph TD
    subgraph AWS["AWS Account"]
        subgraph VPC["VPC"]
            subgraph Private["Private Subnets (multi-AZ)"]
                EKS[EKS Cluster]
            end
            subgraph Isolated["Isolated Subnets"]
                RDS[(Aurora PostgreSQL)]
                EC[ElastiCache Redis]
            end
        end
        ECR[ECR Registry]
        SM[Secrets Manager]
        CW[CloudWatch]
        GH[GitHub Actions]
    end
    Internet --> ALB[ALB Ingress]
    ALB --> EKS
    GH -->|push image| ECR
    GH -->|deploy via ArgoCD| EKS
    EKS -->|IRSA| SM
    EKS --> RDS
    EKS --> EC
    EKS --> CW
```

### Multi-account with Organizations
```mermaid
graph TD
    subgraph Org["AWS Organizations"]
        Mgmt[Management Account]
        subgraph Workloads["Workloads OU"]
            Prod[Production Account]
            Staging[Staging Account]
        end
        subgraph Shared["Shared Services OU"]
            Shared_Svcs[Shared Services Account]
        end
        Log[Log Archive Account]
        Security[Security Tooling Account]
    end
    Mgmt -->|SCPs| Workloads
    Security -->|GuardDuty aggregation| Prod & Staging
    Log -->|CloudTrail logs| Prod & Staging
    Shared_Svcs -->|ECR, Transit GW| Prod & Staging
```

---

## SVG Colour Reference

```
AWS Orange (compute):     #FF9900
AWS Purple (networking):  #8C4FFF
AWS Green (data):         #3F8624
AWS Red (security):       #DD344C
AWS Pink (messaging):     #E7157B
Neutral arrows:           #545B64
VPC background:           #F1F8FF
Public subnet:            #FFF8E1 (warm yellow)
Private subnet:           #E8F5E9 (light green)
Isolated subnet:          #FCE4EC (light pink)
```

## Common Layout Patterns

### Three-subnet tier layout (SVG)
- **Top row (public subnets):** Internet-facing — ALB, NAT Gateway, Bastion
- **Middle row (private subnets):** Application tier — ECS/EKS, Lambda in VPC
- **Bottom row (isolated subnets):** Data tier — RDS, ElastiCache, OpenSearch. No internet route.
- Repeat columns for each AZ (typically 2–3)
- VPC boundary: dashed blue border
- AZ boundaries: light grey dashed columns
- Internet cloud shape at top, on-prem shape at bottom-left if applicable

### Multi-account layout (SVG)
- Each account as a rounded rectangle with account name label
- AWS Organizations boundary as outer dashed rectangle
- VPC shown as nested rectangle within account
- Direct Connect / Transit Gateway connections shown as thick arrows between accounts
- Security tooling account has arrows pointing INTO all other accounts (monitoring direction)
