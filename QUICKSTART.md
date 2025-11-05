# Quick Start Guide

Get the SOR Document Retrieval Agent up and running in 15 minutes!

## Prerequisites

- Python 3.11 or higher
- Azure OpenAI account (or OpenAI API key)
- Microsoft Copilot Studio access

## Step 1: Clone and Setup (2 minutes)

```bash
# Clone the repository (if not already done)
git clone https://github.com/Severin-Shea/CopilotCWS.git
cd CopilotCWS

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Environment (3 minutes)

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

Update the following values in `.env`:

```bash
AZURE_OPENAI_ENDPOINT=https://YOUR-INSTANCE.openai.azure.com/
AZURE_OPENAI_API_KEY=your-actual-api-key
EMBEDDING_DEPLOYMENT=text-embedding-ada-002
CHAT_DEPLOYMENT=gpt-4
```

## Step 3: Test the API Locally (5 minutes)

```bash
# Start the API server
python api_example.py
```

You should see:
```
Starting SOR Document API...
Loaded document: SOR-2024-0001
Loaded document: SOR-2024-0015
Loaded document: SOR-2024-0032
Loaded 3 documents
 * Running on http://0.0.0.0:5000
```

## Step 4: Test with cURL (2 minutes)

Open a new terminal and test the API:

```bash
# Test health check
curl http://localhost:5000/health

# Test document search
curl -X POST http://localhost:5000/api/search/similar \
  -H "Content-Type: application/json" \
  -d '{
    "projectDetails": "Healthcare patient portal with EHR integration and HIPAA compliance",
    "topN": 3
  }'

# Test document details
curl "http://localhost:5000/api/documents/SOR-2024-0001/details?contextProjectDetails=Healthcare+project"
```

## Step 5: Import to Copilot Studio (3 minutes)

1. Log in to [Copilot Studio](https://copilotstudio.microsoft.com/)
2. Navigate to **Topics** → **+ New topic** → **From file**
3. Upload `topics/SORDocumentRetrieval.yaml`
4. Navigate to **Actions** → **+ Add action** → **From a file**
5. Upload `actions/SORDocumentActions.yaml`
6. Configure the action:
   - Base URL: `http://localhost:5000/api` (for testing) or your deployed URL
   - Authentication: Add if required

## Step 6: Test in Copilot Studio

1. Open **Test your copilot** panel
2. Type: "Find similar SOR documents"
3. When prompted, enter:
   ```
   I'm building a healthcare patient portal with Epic EHR integration,
   appointment scheduling, and secure messaging. Need HIPAA compliance,
   support for 10,000 users, budget around $3M, 12-month timeline.
   ```
4. Specify number of documents: `3`
5. Review the results!

## Expected Output

The agent will respond with:

```
I found 3 similar SOR documents that could be valuable references 
for your project. Let me provide you with detailed information about 
each one.

---

Document 1: Healthcare Patient Portal Implementation - Metro General Hospital

Similarity Score: 87.5%

Summary:
[AI-generated summary of the project...]

Why this is a good reference:
This document shares several key similarities with your project, 
particularly the Epic EHR integration requirement and HIPAA compliance 
focus. The reference project successfully implemented appointment 
scheduling and secure messaging features similar to your needs...

Document Link: [View Document](https://documents.example.com/SOR-2024-0001)

Key Properties:
- Project Type: Web Application
- Industry: Healthcare
- Complexity: high
- Date Created: 2024-01-15

[Additional documents follow...]
```

## Common Issues

### Issue: "Error generating embedding"

**Solution**: Check your Azure OpenAI credentials in `.env`

### Issue: "No documents loaded"

**Solution**: Ensure example documents are in the `examples/` directory

### Issue: "Connection refused"

**Solution**: Make sure the API server is running on port 5000

## Next Steps

Once everything is working locally:

1. **Deploy the API**: Follow [Deployment Guide](docs/Deployment-Guide.md)
2. **Load Real Documents**: Replace examples with your actual SOR documents
3. **Customize Topic**: Modify conversation flow in `topics/SORDocumentRetrieval.yaml`
4. **Set Up Monitoring**: Configure Application Insights for production

## Need Help?

- 📖 Full documentation: [docs/README.md](docs/README.md)
- 🚀 Deployment guide: [docs/Deployment-Guide.md](docs/Deployment-Guide.md)
- 🤖 AI integration: [docs/AI-Integration-Guide.md](docs/AI-Integration-Guide.md)

## Production Checklist

Before deploying to production:

- [ ] Test with 10+ diverse project queries
- [ ] Load your organization's actual SOR documents
- [ ] Set up proper authentication (not just API keys)
- [ ] Configure monitoring and alerting
- [ ] Set up backup and disaster recovery
- [ ] Document internal processes
- [ ] Train users on the system
- [ ] Establish feedback mechanism

## API Endpoints Summary

- `GET /health` - Health check
- `POST /api/search/similar` - Search for similar documents
- `GET /api/documents/{id}/details` - Get document details
- `POST /api/documents/upload` - Upload new document

## Example Queries to Try

1. **Healthcare**: "Medical device regulatory submission system with FDA compliance"
2. **Finance**: "Core banking system migration to cloud with PCI-DSS compliance"
3. **Retail**: "E-commerce platform with inventory management and mobile app"
4. **Government**: "Citizen portal with multi-factor authentication and accessibility"
5. **Education**: "Learning management system with video conferencing integration"

## Architecture Overview

```
User → Copilot Studio → API (api_example.py) → Azure OpenAI
                                              → Document Store
```

1. User provides project details via Copilot Studio
2. Copilot Studio calls API endpoints
3. API generates embeddings using Azure OpenAI
4. API searches document store for similar documents
5. API generates summaries and explanations using GPT-4
6. Results returned to user through Copilot Studio

## Performance Tips

- **Cache embeddings**: Don't regenerate for existing documents
- **Batch requests**: Process multiple documents at once
- **Use indexes**: Implement proper vector search index
- **Monitor costs**: Track OpenAI API usage
- **Optimize prompts**: Shorter prompts = lower costs

## Security Notes

⚠️ **Important**: The example API (`api_example.py`) is for development only!

For production:
- Add authentication (OAuth, JWT, API keys)
- Use HTTPS only
- Implement rate limiting
- Store secrets in Azure Key Vault
- Add input validation and sanitization
- Set up CORS properly
- Enable logging and monitoring

---

**Ready to go?** Start with Step 1 and you'll be up and running in 15 minutes! 🚀
