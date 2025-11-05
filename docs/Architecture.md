# Architecture Overview

This document describes the architecture of the SOR Document Retrieval Agent system.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                             USER                                     │
│                    (Project Manager, Analyst)                        │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ Natural Language Input
                             │ (Project Details)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    MICROSOFT COPILOT STUDIO                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Topic: SORDocumentRetrieval.yaml                            │   │
│  │  - Capture user input                                        │   │
│  │  - Orchestrate conversation flow                             │   │
│  │  - Present results to user                                   │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                         │
│                             │ REST API Calls                          │
│                             ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  Actions: SORDocumentActions.yaml                            │   │
│  │  - SearchSimilarDocuments                                    │   │
│  │  - GetDocumentDetails                                        │   │
│  │  - UploadNewDocument                                         │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
└─────────────────────────────┼────────────────────────────────────────┘
                              │
                              │ HTTPS
                              │
┌─────────────────────────────┼────────────────────────────────────────┐
│                    API LAYER (Flask/Azure Functions)                 │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │  Endpoints:                                                    │  │
│  │  POST /api/search/similar                                     │  │
│  │  GET  /api/documents/{id}/details                             │  │
│  │  POST /api/documents/upload                                   │  │
│  └───────────────────────────┬───────────────────────────────────┘  │
│                               │                                       │
│                  ┌────────────┴────────────┐                         │
│                  ▼                         ▼                         │
│  ┌──────────────────────────┐  ┌──────────────────────────┐        │
│  │  Request Processing       │  │  Response Formatting     │        │
│  │  - Validation            │  │  - JSON serialization    │        │
│  │  - Authentication        │  │  - Error handling        │        │
│  └──────────┬───────────────┘  └──────────────────────────┘        │
└─────────────┼──────────────────────────────────────────────────────┘
              │
              │
┌─────────────┼──────────────────────────────────────────────────────┐
│             │           AI/ML SERVICES                               │
│             │                                                        │
│  ┌──────────▼─────────────────────────────────────────────────┐    │
│  │               AZURE OPENAI SERVICE                          │    │
│  │  ┌──────────────────────────┐  ┌─────────────────────────┐ │    │
│  │  │  Embedding Model         │  │  Chat Model (GPT-4)     │ │    │
│  │  │  text-embedding-ada-002  │  │  - Summarization        │ │    │
│  │  │  - Convert text to       │  │  - Relevance            │ │    │
│  │  │    1536-dim vectors      │  │    explanation          │ │    │
│  │  │  - Semantic similarity   │  │  - Key insights         │ │    │
│  │  └──────────────────────────┘  └─────────────────────────┘ │    │
│  └─────────────────────────────────────────────────────────────┘    │
└──────────────────────────────┬──────────────────────────────────────┘
                               │
                               │ Embeddings & Responses
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT SEARCH & STORAGE                         │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │         AZURE COGNITIVE SEARCH / ELASTICSEARCH               │   │
│  │  ┌────────────────────┐  ┌────────────────────────────────┐ │   │
│  │  │  Vector Index      │  │  Metadata Index               │ │   │
│  │  │  - Embeddings      │  │  - Project type               │ │   │
│  │  │  - HNSW algorithm  │  │  - Industry                   │ │   │
│  │  │  - Cosine distance │  │  - Complexity                 │ │   │
│  │  │  - Top-N retrieval │  │  - Date filters               │ │   │
│  │  └────────────────────┘  └────────────────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              DOCUMENT STORAGE (Azure Blob/DB)                │   │
│  │  - Full SOR documents (JSON)                                 │   │
│  │  - Schemas and metadata                                      │   │
│  │  - Attachments and supporting files                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer

**Microsoft Copilot Studio**
- **Role**: Conversational interface and orchestration
- **Responsibilities**:
  - Capture user input in natural language
  - Manage conversation flow and context
  - Display formatted results
  - Handle follow-up questions
- **Technology**: Power Virtual Agents platform

### 2. Topic Configuration

**File**: `topics/SORDocumentRetrieval.yaml`
- **Format**: Adaptive Dialog YAML
- **Functions**:
  - Define conversation triggers
  - Specify questions to ask users
  - Orchestrate action calls
  - Format and display results
  - Handle error scenarios

### 3. API Layer

**Implementation**: Flask (example) or Azure Functions (production)
- **Responsibilities**:
  - Receive requests from Copilot Studio
  - Validate input
  - Authenticate and authorize
  - Process business logic
  - Call AI services
  - Query document store
  - Format responses

**Key Endpoints**:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/search/similar` | POST | Find similar documents |
| `/api/documents/{id}/details` | GET | Get document details |
| `/api/documents/upload` | POST | Upload new document |
| `/health` | GET | Health check |

### 4. AI/ML Services

**Azure OpenAI Service**

**Embedding Model** (text-embedding-ada-002):
- Converts text to 1536-dimensional vectors
- Enables semantic similarity search
- Input: Project description
- Output: Vector embedding

**Chat Model** (GPT-4):
- Generates document summaries
- Creates relevance explanations
- Extracts key insights
- Input: Structured prompts with document data
- Output: Natural language text

### 5. Search & Storage Layer

**Azure Cognitive Search** (or Elasticsearch)
- **Vector Search**:
  - HNSW (Hierarchical Navigable Small World) algorithm
  - Cosine similarity metric
  - Fast approximate nearest neighbor search
- **Metadata Filtering**:
  - Project type
  - Industry
  - Complexity level
  - Date ranges
- **Full-Text Search**:
  - Title and description search
  - Keyword matching

**Document Storage**:
- Azure Blob Storage or Database
- JSON format following schema
- Attachments and supporting files
- Version control

## Data Flow

### Scenario 1: Search for Similar Documents

```
1. User provides project details
   ↓
2. Copilot Studio captures input via topic
   ↓
3. Topic calls SearchSimilarDocuments action
   ↓
4. API receives request
   ↓
5. API generates embedding (Azure OpenAI)
   ↓
6. API queries search index with embedding
   ↓
7. Search index returns top N matches
   ↓
8. API formats results
   ↓
9. Copilot Studio displays results to user
```

### Scenario 2: Get Document Details

```
1. User selects a document (or auto-selected)
   ↓
2. Topic calls GetDocumentDetails action
   ↓
3. API receives document ID
   ↓
4. API fetches document from storage
   ↓
5. API generates summary (GPT-4)
   ↓
6. API generates relevance explanation (GPT-4)
   ↓
7. API extracts key insights (GPT-4)
   ↓
8. API formats comprehensive response
   ↓
9. Copilot Studio displays formatted details
```

## Deployment Architectures

### Development Environment

```
Local Machine
├── Python API (Flask)
├── In-memory document store
└── Direct Azure OpenAI calls

Testing via:
- cURL
- Postman
- Copilot Studio (pointing to localhost)
```

### Production Environment (Azure)

```
Azure Cloud
├── Azure Functions (API)
│   ├── Consumption plan (serverless)
│   └── Managed identity for auth
├── Azure Cognitive Search
│   ├── Standard tier
│   └── Vector search enabled
├── Azure OpenAI Service
│   ├── Embedding deployment
│   └── GPT-4 deployment
├── Azure Blob Storage
│   └── Document files
├── Azure SQL Database
│   └── Document metadata
├── Azure Key Vault
│   └── Secrets management
└── Application Insights
    └── Monitoring & logging
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Security Layers                                             │
├─────────────────────────────────────────────────────────────┤
│  1. Authentication                                           │
│     - Azure AD integration                                   │
│     - Bearer tokens                                          │
│     - API keys (development only)                            │
├─────────────────────────────────────────────────────────────┤
│  2. Authorization                                            │
│     - Role-based access control (RBAC)                       │
│     - Document-level permissions                             │
├─────────────────────────────────────────────────────────────┤
│  3. Data Protection                                          │
│     - Encryption at rest (Azure Storage encryption)          │
│     - Encryption in transit (TLS 1.3)                        │
│     - PII detection and masking                              │
├─────────────────────────────────────────────────────────────┤
│  4. Network Security                                         │
│     - Private endpoints (production)                         │
│     - Virtual network integration                            │
│     - Azure Firewall                                         │
├─────────────────────────────────────────────────────────────┤
│  5. Secrets Management                                       │
│     - Azure Key Vault                                        │
│     - Managed identities                                     │
│     - No secrets in code                                     │
├─────────────────────────────────────────────────────────────┤
│  6. Monitoring & Auditing                                    │
│     - Application Insights                                   │
│     - Azure Monitor                                          │
│     - Audit logs for all document access                     │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Considerations

### Horizontal Scaling

- **API Layer**: Azure Functions auto-scale based on load
- **Search**: Multiple replicas and partitions
- **OpenAI**: Rate limiting and request queuing

### Performance Optimization

- **Caching**: Redis cache for frequently accessed documents
- **CDN**: Static content delivery
- **Async Processing**: Background jobs for batch operations
- **Connection Pooling**: Database connection optimization

### Cost Optimization

- **Serverless Functions**: Pay per execution
- **Reserved Capacity**: OpenAI reserved instances
- **Tiered Storage**: Hot/Cool/Archive tiers
- **Query Optimization**: Efficient search queries

## Monitoring & Observability

### Metrics to Track

1. **API Performance**:
   - Request latency (p50, p95, p99)
   - Error rate
   - Request volume

2. **AI Service Usage**:
   - Token consumption
   - API call count
   - Cost per request

3. **Search Performance**:
   - Query latency
   - Result relevance (user feedback)
   - Index size

4. **User Behavior**:
   - Query patterns
   - Document access frequency
   - User satisfaction scores

### Alerting

- API error rate > 5%
- Average latency > 3 seconds
- OpenAI rate limit approaching
- Search index capacity > 80%

## Disaster Recovery

### Backup Strategy

- **Documents**: Daily backups to geo-redundant storage
- **Search Index**: Snapshot before major changes
- **Configuration**: Version controlled in Git

### Recovery Plan

- **RTO** (Recovery Time Objective): 4 hours
- **RPO** (Recovery Point Objective): 24 hours
- **Failover**: Multi-region deployment for critical workloads

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| UI | Microsoft Copilot Studio | Conversational interface |
| API | Azure Functions / Flask | REST API backend |
| AI | Azure OpenAI | Embeddings & text generation |
| Search | Azure Cognitive Search | Vector similarity search |
| Storage | Azure Blob Storage | Document storage |
| Database | Azure SQL / Cosmos DB | Metadata storage |
| Secrets | Azure Key Vault | Secret management |
| Monitoring | Application Insights | Observability |
| Authentication | Azure AD | Identity management |

## Integration Points

### External Systems

1. **Document Management Systems**: SharePoint, OneDrive
2. **Project Management Tools**: Azure DevOps, Jira
3. **Authentication**: Azure Active Directory
4. **Notification**: Microsoft Teams, Email

### APIs

- **Microsoft Graph API**: For document access
- **Azure Management API**: For resource management
- **Custom webhooks**: For real-time updates

## Future Architecture Enhancements

1. **Multi-language Support**: Additional language models
2. **Advanced Analytics**: Power BI integration
3. **Collaborative Features**: Real-time collaboration on documents
4. **ML Pipeline**: Continuous learning from user feedback
5. **Edge Deployment**: Offline capabilities
6. **GraphRAG**: Enhanced retrieval with knowledge graphs

---

This architecture is designed to be:
- ✅ **Scalable**: Handle growing document libraries and user base
- ✅ **Secure**: Enterprise-grade security and compliance
- ✅ **Reliable**: High availability and disaster recovery
- ✅ **Maintainable**: Clear separation of concerns
- ✅ **Cost-effective**: Serverless and pay-per-use models
