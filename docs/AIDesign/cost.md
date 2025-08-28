# Cost breakdown 

This total assumes:
- 1 full request pipeline per page (CSV/PDF to internal format)
- Includes compute, inference, vector search, and frontend delivery


# CSV request 

This section outlines the estimated cost per single-CSV (consisting 18 products) quotation request, broken down by component and service.

| **Component**              | **Service / Endpoint**                   | **Cost (USD)** | **Notes**                                       |
| -------------------------- | ---------------------------------------- | -------------- | ----------------------------------------------- |
| **API Gateway**            | Manages API endpoints                    | \$0.00000700   | \$0.0000035 × 2 calls                           |
| **Lambda (Normalize)**     | `/raw_order`, `/normalize_csv`           | \$0.00012520   | 15 sec execution (includes compute + invoke)    |
| **Bedrock (Nova Lite)**    | `/raw_order`, `/normalize_csv`           | \$0.00030000   | 1 page; input: 1200 tokens, output: 1000 tokens |
| **Lambda (Convert)**       | `/normalized_order`, `/convert_internal` | \$0.00025620   | 30 sec execution (includes compute + invoke)    |
| **Pinecone Query**         | `/normalized_order`, `/convert_internal` | \$0.00250000   | 512 MB, 30 sec search time                      |
| **Bedrock (Nova Lite)**    | `/normalized_order`, `/convert_internal` | \$0.00024720   | 1 page; input: 1000 tokens, output: 780 tokens  |
| **S3 (Static Frontend)**   | JS/CSS load + 2 API calls                | \$0.00001000   | 2 API calls, frontend bundle \~0.0023 GB        |
| **CloudFront (Data Out)**  | CDN transfer to user                     | —              | 0.0023 GB (billed separately by AWS rate)       |
| **CloudFront (HTTPS Req)** | HTTPS request cost                       | \$0.00007500   |                                                 |

# PDF request  

This section outlines the estimated cost per single-page PDF quotation request, broken down by component and service.


| Component              | Service                                  | Cost (USD)     | Notes                                                                 |
|------------------------|-------------------------------------------|----------------|-----------------------------------------------------------------------|
| **API Gateway**        | Manage endpoint                           | $0.00000700    | Per API call: $0.0000035 × 2 calls                                   |
| **Lambda**             | `/raw_order`, `/normalize_pdf`            | $0.00025620    | Execution time: 30 sec (compute + invoke included)                   |
| **Bedrock**            | `/raw_order`, `/normalize_pdf`            | $0.00030000    | Amazon Nova Lite — Input: 1200 tokens, Output: 1000 tokens           |
| **Lambda (convert)**   | `/normalized_order/convert_internal`      | $0.00025620    | Execution time: 30 sec (compute + invoke included)                   |
| **Pinecone**           | `/normalized_order/convert_internal`      | $0.00250000    | Query cost (512 MB namespace)                                        |
| **Bedrock (2nd call)** | `/normalized_order/convert_internal`      | $0.00024720    | Amazon Nova Lite — Input: 1000 tokens, Output: 780 tokens            |
| **S3 (static frontend)**| Request API (frontend bundle 0.0023 GB)   | $0.00001000    | 2 API calls from frontend                                            |
| **CloudFront**         | HTTPS request                             | $0.00007500    | Data transfer out (static file + API)                                |

---

# Monhtly fix cost 
These are recurring infrastructure costs independent of usage volume.

| Component             | Description                | Monthly Cost (USD) |
|----------------------|----------------------------|--------------------|
| **S3 Bucket**         | Static file storage (~2.3MB) | $0.0000529          |
| **Pinecone (Standard Plan)** | Base subscription (includes storage + query RU minimum) | $50.00              |

---
 