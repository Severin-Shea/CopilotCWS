# Deployment Guide

This guide provides step-by-step instructions for deploying the SOR Document Retrieval Agent to production.

## Deployment Checklist

- [ ] Azure/Cloud infrastructure provisioned
- [ ] Document search index created
- [ ] AI/LLM services configured
- [ ] SOR documents loaded into search index
- [ ] API endpoints deployed and tested
- [ ] Copilot Studio topic imported
- [ ] Actions configured with production endpoints
- [ ] Authentication and security configured
- [ ] Monitoring and logging set up
- [ ] User training completed
- [ ] Documentation shared with team

## Prerequisites

### Required Azure Resources

1. **Azure OpenAI Service**
   - Deployment name for embeddings (text-embedding-ada-002)
   - Deployment name for chat (gpt-4 or gpt-4-turbo)

2. **Azure Cognitive Search** (or alternative)
   - Standard tier or higher
   - Vector search enabled
   - Sufficient capacity for document library

3. **Azure App Service** or **Azure Functions**
   - For hosting API backend
   - Appropriate tier for expected load

4. **Azure Key Vault** (recommended)
   - For secure storage of API keys and secrets

5. **Azure Monitor** (recommended)
   - For logging and monitoring

### Required Accounts

- Microsoft Copilot Studio license
- Azure subscription with appropriate permissions
- OpenAI API key (if not using Azure OpenAI)

## Step-by-Step Deployment

### 1. Provision Azure Resources

#### Create Resource Group

```bash
az group create \
  --name rg-sor-documents-prod \
  --location eastus
```

#### Create Azure OpenAI Service

```bash
# Create OpenAI resource
az cognitiveservices account create \
  --name openai-sor-prod \
  --resource-group rg-sor-documents-prod \
  --kind OpenAI \
  --sku S0 \
  --location eastus \
  --yes

# Deploy embedding model
az cognitiveservices account deployment create \
  --name openai-sor-prod \
  --resource-group rg-sor-documents-prod \
  --deployment-name embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --sku-capacity 120 \
  --sku-name "Standard"

# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --name openai-sor-prod \
  --resource-group rg-sor-documents-prod \
  --deployment-name gpt-4-turbo \
  --model-name gpt-4 \
  --model-version "turbo-2024-04-09" \
  --model-format OpenAI \
  --sku-capacity 50 \
  --sku-name "Standard"
```

#### Create Azure Cognitive Search

```bash
az search service create \
  --name search-sor-prod \
  --resource-group rg-sor-documents-prod \
  --sku standard \
  --location eastus \
  --partition-count 1 \
  --replica-count 2
```

#### Create Search Index

```bash
# Get admin key
SEARCH_KEY=$(az search admin-key show \
  --service-name search-sor-prod \
  --resource-group rg-sor-documents-prod \
  --query primaryKey -o tsv)

# Create index (using schema)
curl -X PUT \
  "https://search-sor-prod.search.windows.net/indexes/sor-documents?api-version=2023-11-01" \
  -H "Content-Type: application/json" \
  -H "api-key: $SEARCH_KEY" \
  -d @search-index-schema.json
```

Create `search-index-schema.json`:

```json
{
  "name": "sor-documents",
  "fields": [
    {"name": "id", "type": "Edm.String", "key": true, "searchable": false},
    {"name": "title", "type": "Edm.String", "searchable": true},
    {"name": "description", "type": "Edm.String", "searchable": true},
    {"name": "projectType", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "industry", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "complexity", "type": "Edm.String", "filterable": true},
    {"name": "dateCreated", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
    {"name": "embedding", "type": "Collection(Edm.Single)", "searchable": true, "dimensions": 1536, "vectorSearchProfile": "vector-profile"},
    {"name": "content", "type": "Edm.String", "searchable": true}
  ],
  "vectorSearch": {
    "profiles": [
      {
        "name": "vector-profile",
        "algorithm": "hnsw-config"
      }
    ],
    "algorithms": [
      {
        "name": "hnsw-config",
        "kind": "hnsw",
        "hnswParameters": {
          "m": 4,
          "efConstruction": 400,
          "efSearch": 500,
          "metric": "cosine"
        }
      }
    ]
  }
}
```

#### Create Key Vault

```bash
az keyvault create \
  --name kv-sor-prod \
  --resource-group rg-sor-documents-prod \
  --location eastus

# Store secrets
az keyvault secret set \
  --vault-name kv-sor-prod \
  --name "OpenAI-ApiKey" \
  --value "YOUR_OPENAI_API_KEY"

az keyvault secret set \
  --vault-name kv-sor-prod \
  --name "Search-ApiKey" \
  --value "$SEARCH_KEY"
```

### 2. Deploy API Backend

#### Option A: Azure Functions

1. Create Function App:

```bash
# Create storage account
az storage account create \
  --name stsorprod \
  --resource-group rg-sor-documents-prod \
  --location eastus \
  --sku Standard_LRS

# Create Function App
az functionapp create \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --storage-account stsorprod \
  --consumption-plan-location eastus \
  --runtime python \
  --runtime-version 3.11 \
  --functions-version 4 \
  --os-type Linux
```

2. Configure App Settings:

```bash
az functionapp config appsettings set \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --settings \
    "AZURE_OPENAI_ENDPOINT=https://openai-sor-prod.openai.azure.com/" \
    "AZURE_OPENAI_KEY=@Microsoft.KeyVault(SecretUri=https://kv-sor-prod.vault.azure.net/secrets/OpenAI-ApiKey/)" \
    "SEARCH_ENDPOINT=https://search-sor-prod.search.windows.net" \
    "SEARCH_KEY=@Microsoft.KeyVault(SecretUri=https://kv-sor-prod.vault.azure.net/secrets/Search-ApiKey/)" \
    "EMBEDDING_DEPLOYMENT=embedding-ada-002" \
    "CHAT_DEPLOYMENT=gpt-4-turbo"
```

3. Deploy Functions (example structure):

```
api/
├── requirements.txt
├── host.json
├── SearchSimilarDocuments/
│   ├── __init__.py
│   └── function.json
├── GetDocumentDetails/
│   ├── __init__.py
│   └── function.json
└── shared/
    └── ai_service.py
```

#### Option B: Azure App Service

```bash
# Create App Service Plan
az appservice plan create \
  --name plan-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --sku B2 \
  --is-linux

# Create Web App
az webapp create \
  --name app-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --plan plan-sor-api-prod \
  --runtime "PYTHON:3.11"

# Configure app settings (same as Function App)
```

### 3. Load Documents into Search Index

Create a script to load existing SOR documents:

```python
# load_documents.py
import json
import os
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from document_ai_service import DocumentAIService

def load_documents(documents_dir: str):
    """Load documents into Azure Cognitive Search."""
    
    # Initialize clients
    search_client = SearchClient(
        endpoint=os.getenv("SEARCH_ENDPOINT"),
        index_name="sor-documents",
        credential=AzureKeyCredential(os.getenv("SEARCH_KEY"))
    )
    
    ai_service = DocumentAIService()
    
    # Load and process each document
    for filename in os.listdir(documents_dir):
        if filename.endswith('.json'):
            with open(os.path.join(documents_dir, filename), 'r') as f:
                doc = json.load(f)
                
                # Generate embedding
                text = f"{doc['title']} {doc['description']}"
                embedding = ai_service.generate_embedding(text)
                
                # Prepare document for indexing
                search_doc = {
                    "id": doc["id"],
                    "title": doc["title"],
                    "description": doc["description"],
                    "projectType": doc["projectType"],
                    "industry": doc["industry"],
                    "complexity": doc["complexity"],
                    "dateCreated": doc["dateCreated"],
                    "embedding": embedding,
                    "content": json.dumps(doc)
                }
                
                # Upload to search index
                result = search_client.upload_documents([search_doc])
                print(f"Uploaded {doc['id']}: {result[0].succeeded}")

if __name__ == "__main__":
    load_documents("./examples")
```

Run the script:

```bash
python load_documents.py
```

### 4. Configure Copilot Studio

#### Import Topic

1. Log in to [Copilot Studio](https://copilotstudio.microsoft.com/)
2. Select your environment
3. Navigate to **Topics**
4. Click **+ New topic** → **From file**
5. Upload `topics/SORDocumentRetrieval.yaml`
6. Review and save

#### Configure Actions

1. Navigate to **Actions**
2. Click **+ Add an action** → **From a file**
3. Upload `actions/SORDocumentActions.yaml`
4. Configure connection:
   - Base URL: `https://func-sor-api-prod.azurewebsites.net/api` (or your endpoint)
   - Authentication: Bearer token or API key
   - Add authentication header if required

#### Test Integration

1. Open **Test your copilot** panel
2. Type: "Find similar SOR documents"
3. Provide sample project details
4. Verify results are returned correctly

### 5. Security Configuration

#### Enable Managed Identity

```bash
# Enable system-assigned identity for Function App
az functionapp identity assign \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod

# Grant access to Key Vault
FUNCTION_IDENTITY=$(az functionapp identity show \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --query principalId -o tsv)

az keyvault set-policy \
  --name kv-sor-prod \
  --object-id $FUNCTION_IDENTITY \
  --secret-permissions get list
```

#### Configure CORS (if needed)

```bash
az functionapp cors add \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --allowed-origins "https://copilotstudio.microsoft.com"
```

#### Enable HTTPS Only

```bash
az functionapp update \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --set httpsOnly=true
```

### 6. Monitoring and Logging

#### Configure Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app insights-sor-prod \
  --resource-group rg-sor-documents-prod \
  --location eastus

# Link to Function App
INSIGHTS_KEY=$(az monitor app-insights component show \
  --app insights-sor-prod \
  --resource-group rg-sor-documents-prod \
  --query instrumentationKey -o tsv)

az functionapp config appsettings set \
  --name func-sor-api-prod \
  --resource-group rg-sor-documents-prod \
  --settings "APPINSIGHTS_INSTRUMENTATIONKEY=$INSIGHTS_KEY"
```

#### Set Up Alerts

```bash
# Alert for high error rate
az monitor metrics alert create \
  --name alert-high-errors \
  --resource-group rg-sor-documents-prod \
  --scopes /subscriptions/{sub-id}/resourceGroups/rg-sor-documents-prod/providers/Microsoft.Web/sites/func-sor-api-prod \
  --condition "count requests where resultCode >= 500 > 10" \
  --window-size 5m \
  --evaluation-frequency 1m
```

### 7. User Training and Rollout

1. **Create User Guide**: Provide examples and best practices
2. **Conduct Training Sessions**: Walk through features with users
3. **Pilot Phase**: Start with a small group of users
4. **Gather Feedback**: Iterate based on user experience
5. **Full Rollout**: Deploy to all users

### 8. Post-Deployment Tasks

- [ ] Verify all endpoints are accessible
- [ ] Test end-to-end flow
- [ ] Monitor initial usage patterns
- [ ] Review logs for errors
- [ ] Collect user feedback
- [ ] Document any issues and resolutions
- [ ] Schedule regular maintenance windows

## Rollback Procedure

If issues occur:

1. **Disable Topic**: Temporarily disable in Copilot Studio
2. **Check Logs**: Review Application Insights and Function logs
3. **Revert API**: Roll back to previous stable version
4. **Notify Users**: Communicate status and timeline
5. **Fix Issues**: Address problems in development environment
6. **Re-deploy**: Deploy fixed version following standard process

## Maintenance

### Regular Tasks

- **Weekly**: Review error logs and performance metrics
- **Monthly**: Update example documents and retrain if needed
- **Quarterly**: Review and optimize costs
- **Annually**: Security audit and compliance review

### Updating Documents

```bash
# Generate embeddings for new documents
python generate_embeddings.py --input new_documents/ --output embeddings/

# Upload to search index
python upload_to_search.py --embeddings embeddings/
```

## Cost Estimation

Approximate monthly costs (USD):

- Azure OpenAI (Standard S0): $1,000-$3,000 (depends on usage)
- Azure Cognitive Search (Standard): $250-$500
- Azure Functions/App Service: $100-$500
- Application Insights: $50-$200
- Storage: $10-$50

**Total**: ~$1,500-$4,500/month (varies with usage)

## Support Contacts

- **Technical Issues**: it-support@yourorg.com
- **Copilot Studio**: copilot-admin@yourorg.com
- **Azure Resources**: cloud-ops@yourorg.com

## Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [Azure Cognitive Search](https://learn.microsoft.com/en-us/azure/search/)
- [Copilot Studio Documentation](https://learn.microsoft.com/en-us/microsoft-copilot-studio/)
