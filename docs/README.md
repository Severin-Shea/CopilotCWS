# Copilot Studio SOR Document Retrieval Agent

## Overview

This Copilot Studio agent provides intelligent document retrieval and similarity matching for Statement of Requirements (SOR) documents. The agent helps users find the most relevant historical SOR documents based on their new project details, providing AI-grounded recommendations to inform their document creation process.

## Features

### 🔍 Intelligent Document Search
- **Semantic Similarity Matching**: Uses AI/ML to find documents similar to user's project description
- **Configurable Results**: Users can specify how many similar documents to retrieve (1-10)
- **Multi-dimensional Matching**: Considers project type, industry, complexity, requirements, technologies, and more

### 📊 Comprehensive Document Information
For each matched document, the agent provides:
- **Document Summary**: AI-generated overview of the project and requirements
- **Similarity Score**: Quantitative measure of how similar the document is to the user's project
- **Relevance Explanation**: AI-grounded explanation of why this document is a good reference
- **Direct Link**: Access to the full document
- **Key Properties**: Project type, industry, complexity, creation date, and more

### 🤖 AI-Grounded Responses
All recommendations and explanations are grounded in the actual content of historical SOR documents, ensuring:
- Accurate and relevant suggestions
- Context-aware explanations
- Evidence-based reference recommendations

### 💬 Conversational Interface
- Natural language interaction
- Follow-up questions supported
- Option to refine search with additional details

## Architecture

### Components

1. **Topic Configuration** (`topics/SORDocumentRetrieval.yaml`)
   - Main conversational flow
   - User interaction logic
   - Result presentation
   - Error handling

2. **Action Definitions** (`actions/SORDocumentActions.yaml`)
   - OpenAPI specification for document search and retrieval
   - API endpoints for similarity search
   - Document detail retrieval
   - Document upload functionality

3. **Document Schema** (`schemas/SORDocumentSchema.json`)
   - JSON Schema defining SOR document structure
   - Properties for semantic search
   - Metadata fields for categorization
   - Validation rules

4. **Example Documents** (`examples/`)
   - Sample SOR documents demonstrating the schema
   - Real-world project examples across different industries
   - Reference data for testing

## Setup Instructions

### Prerequisites

- Microsoft Copilot Studio account
- Access to organization's SOR document library
- API endpoint for document search (or Azure Cognitive Search, Elasticsearch, etc.)
- AI/LLM service for generating summaries and explanations (Azure OpenAI, OpenAI API, etc.)

### Step 1: Import the Topic

1. Open Copilot Studio
2. Navigate to **Topics** section
3. Click **Import** and select `topics/SORDocumentRetrieval.yaml`
4. Review and confirm the import

### Step 2: Configure Actions

1. Navigate to **Actions** section in Copilot Studio
2. Click **Add an action** > **From a file**
3. Select `actions/SORDocumentActions.yaml`
4. Configure the following:
   - **Base URL**: Your document API endpoint
   - **Authentication**: Add bearer token or API key
   - **Timeout**: Recommended 30 seconds for search operations

### Step 3: Set Up Document Library

#### Option A: Use Azure Cognitive Search

```bash
# Create Azure Cognitive Search instance
az search service create --name sor-docs-search \
  --resource-group your-rg \
  --sku standard

# Create index with vector search capabilities
az search index create --service-name sor-docs-search \
  --name sor-documents \
  --schema schemas/SORDocumentSchema.json
```

#### Option B: Use Elasticsearch

```bash
# Create Elasticsearch index
curl -X PUT "localhost:9200/sor_documents" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "title": { "type": "text" },
      "description": { "type": "text" },
      "projectType": { "type": "keyword" },
      "industry": { "type": "keyword" },
      "embedding": { "type": "dense_vector", "dims": 1536 }
    }
  }
}
'
```

#### Option C: Custom Implementation

Implement the API endpoints defined in `actions/SORDocumentActions.yaml`:

1. **POST /search/similar**: Semantic similarity search
   - Accept project details and topN parameter
   - Generate embeddings using Azure OpenAI or similar
   - Perform vector similarity search
   - Return top N matching documents

2. **GET /documents/{documentId}/details**: Document details retrieval
   - Fetch document from database
   - Generate AI summary using LLM
   - Create relevance explanation
   - Return formatted response

### Step 4: Integrate AI/LLM Service

Configure your backend to use an LLM for:

1. **Embedding Generation** (for similarity search)
   ```python
   # Example using Azure OpenAI
   import openai
   
   def generate_embedding(text):
       response = openai.Embedding.create(
           input=text,
           engine="text-embedding-ada-002"
       )
       return response['data'][0]['embedding']
   ```

2. **Summary Generation**
   ```python
   def generate_summary(document):
       prompt = f"""Summarize this SOR document in 200-300 words:
       
       Title: {document['title']}
       Description: {document['description']}
       Objectives: {document['objectives']}
       Requirements: {document['requirements']}
       """
       
       response = openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content
   ```

3. **Relevance Explanation**
   ```python
   def explain_relevance(document, user_query):
       prompt = f"""Explain why this SOR document is a good reference for the user's project:
       
       User's Project: {user_query}
       
       Reference Document:
       Title: {document['title']}
       Type: {document['projectType']}
       Industry: {document['industry']}
       Key Technologies: {document['technologies']}
       
       Provide a grounded explanation based on specific similarities.
       """
       
       response = openai.ChatCompletion.create(
           model="gpt-4",
           messages=[{"role": "user", "content": prompt}]
       )
       return response.choices[0].message.content
   ```

### Step 5: Load Example Documents

```bash
# Load example documents into your search index
for file in examples/*.json; do
    curl -X POST "your-api-endpoint/documents/upload" \
      -H "Content-Type: application/json" \
      -d @"$file"
done
```

### Step 6: Test the Agent

1. Open Copilot Studio Test Chat
2. Trigger the topic with: "Find similar SOR documents"
3. Provide project details when prompted
4. Verify that results are returned with summaries and explanations
5. Test edge cases:
   - Very specific project details
   - Generic project details
   - Different industries and project types

## Usage Guide

### Starting a Search

Users can trigger the document retrieval topic by saying:
- "Find similar SOR documents"
- "Search for similar project documents"
- "Show me related SOR documents"
- "Need reference documents for my project"

### Providing Project Details

When prompted, users should provide comprehensive project information:

**Good Example:**
```
I'm working on a telemedicine platform for a mid-size healthcare provider. 
The project needs to support video consultations, EHR integration with Epic, 
secure messaging, appointment scheduling, and e-prescriptions. We need HIPAA 
compliance, support for 10,000 concurrent users, and integration with existing 
billing systems. Budget is around $2-3M and timeline is 12 months.
```

**Less Optimal Example:**
```
Healthcare project
```

The more detailed the input, the better the similarity matching will be.

### Interpreting Results

Each returned document includes:

1. **Similarity Score (0-100)**: Higher scores indicate closer matches
   - 90-100: Extremely similar
   - 75-89: Very similar
   - 60-74: Moderately similar
   - Below 60: Somewhat similar

2. **Summary**: Quick overview of what the document covers

3. **Relevance Explanation**: Specific reasons why this document is useful, such as:
   - Similar technology stack
   - Same industry regulations
   - Comparable project scope
   - Related requirements

4. **Key Properties**: Quick-glance metadata

### Refining Searches

If initial results aren't satisfactory, users can:
- Provide more specific details
- Adjust the number of results (topN parameter)
- Focus on specific aspects (e.g., "focus on HIPAA compliance aspects")

## API Reference

### Search Similar Documents

**Endpoint**: `POST /search/similar`

**Request Body**:
```json
{
  "projectDetails": "string (required)",
  "topN": integer (1-10, default: 5),
  "filters": {
    "projectType": ["string"],
    "industry": ["string"],
    "complexity": "string",
    "dateRange": {
      "startDate": "date",
      "endDate": "date"
    }
  }
}
```

**Response**:
```json
{
  "documents": [
    {
      "id": "string",
      "title": "string",
      "projectType": "string",
      "industry": "string",
      "complexity": "string",
      "dateCreated": "date",
      "similarityScore": number,
      "keyTerms": ["string"]
    }
  ],
  "totalResults": integer,
  "searchMetadata": {
    "searchTime": number,
    "algorithm": "string"
  }
}
```

### Get Document Details

**Endpoint**: `GET /documents/{documentId}/details`

**Parameters**:
- `documentId` (path, required): Document identifier
- `contextProjectDetails` (query, optional): For contextual relevance explanation

**Response**:
```json
{
  "id": "string",
  "title": "string",
  "summary": "string",
  "link": "uri",
  "similarityScore": number,
  "relevanceExplanation": "string",
  "metadata": { /* document metadata */ },
  "keyInsights": [
    {
      "category": "string",
      "insight": "string"
    }
  ],
  "relatedDocuments": [
    {
      "id": "string",
      "title": "string",
      "relationship": "string"
    }
  ]
}
```

## Best Practices

### For Users

1. **Be Specific**: Provide detailed project information including:
   - Project type and objectives
   - Technical requirements
   - Industry and compliance needs
   - Budget and timeline constraints
   - Key stakeholders

2. **Iterate**: If results aren't perfect, refine your search with additional details

3. **Review Multiple Documents**: Check several results to get a comprehensive view

4. **Note Similarities and Differences**: Understand how reference documents align with and differ from your project

### For Administrators

1. **Keep Documents Updated**: Regularly add new SOR documents to the library

2. **Maintain Quality**: Ensure all documents follow the schema and include comprehensive metadata

3. **Monitor Performance**: Track search quality and user satisfaction

4. **Update Embeddings**: Periodically regenerate embeddings for improved search accuracy

5. **Curate Examples**: Maintain a diverse set of example documents across industries and project types

## Troubleshooting

### No Results Returned

**Causes**:
- Document library is empty
- Query is too specific
- API endpoint is unreachable

**Solutions**:
- Verify documents are loaded in the search index
- Broaden search criteria
- Check API connectivity and authentication

### Poor Result Quality

**Causes**:
- Insufficient project details provided
- Embedding model mismatch
- Limited document library

**Solutions**:
- Encourage users to provide more details
- Retrain or update embedding model
- Add more diverse documents to library

### Slow Response Times

**Causes**:
- Large document library
- Complex AI processing
- API timeout issues

**Solutions**:
- Optimize search index
- Implement caching
- Increase API timeout values
- Use faster embedding models

## Security Considerations

1. **Access Control**: Implement role-based access to documents
2. **Data Privacy**: Ensure PII is not included in search logs
3. **Audit Trail**: Log all document access for compliance
4. **Secure Transmission**: Use HTTPS for all API calls
5. **Token Management**: Rotate API keys regularly

## Future Enhancements

Potential improvements to consider:

- [ ] Multi-language support for international projects
- [ ] Advanced filtering by budget ranges, timelines, team sizes
- [ ] Document comparison features
- [ ] Export functionality for search results
- [ ] Integration with document authoring tools
- [ ] Feedback mechanism to improve search quality
- [ ] Analytics dashboard for search patterns
- [ ] Automated document tagging and categorization
- [ ] Version control integration
- [ ] Collaborative features for team review

## Support

For issues or questions:
- Check troubleshooting section above
- Review API logs for error details
- Consult Microsoft Copilot Studio documentation
- Contact your IT support team

## License

[Specify your organization's license here]

## Version History

- **v1.0** (2025-11-05): Initial release
  - Core search and retrieval functionality
  - AI-grounded recommendations
  - Example documents for healthcare, finance, and retail
