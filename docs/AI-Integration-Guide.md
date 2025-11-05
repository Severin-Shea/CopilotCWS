# AI/LLM Integration Configuration Guide

This guide provides detailed instructions for integrating AI and Large Language Models (LLMs) with the SOR Document Retrieval Agent to enable semantic search, document summarization, and grounded explanations.

## Overview

The agent uses AI/LLM services for three primary functions:

1. **Embedding Generation**: Convert text into vector representations for similarity search
2. **Document Summarization**: Generate concise, informative summaries of SOR documents
3. **Relevance Explanation**: Create contextual explanations of why documents are relevant

## Supported AI Services

### Azure OpenAI Service (Recommended)

**Benefits**:
- Enterprise-grade security and compliance
- Data residency options
- SLA guarantees
- Microsoft ecosystem integration

**Models**:
- `text-embedding-ada-002` for embeddings
- `gpt-4` or `gpt-4-turbo` for summaries and explanations

**Setup**:

1. **Create Azure OpenAI Resource**:
```bash
az cognitiveservices account create \
  --name sor-openai-service \
  --resource-group your-resource-group \
  --kind OpenAI \
  --sku S0 \
  --location eastus
```

2. **Deploy Models**:
```bash
# Deploy embedding model
az cognitiveservices account deployment create \
  --name sor-openai-service \
  --resource-group your-resource-group \
  --deployment-name text-embedding-ada-002 \
  --model-name text-embedding-ada-002 \
  --model-version "2" \
  --model-format OpenAI \
  --scale-settings-scale-type "Standard"

# Deploy GPT-4 model
az cognitiveservices account deployment create \
  --name sor-openai-service \
  --resource-group your-resource-group \
  --deployment-name gpt-4 \
  --model-name gpt-4 \
  --model-version "0613" \
  --model-format OpenAI \
  --scale-settings-scale-type "Standard"
```

3. **Configuration**:
```json
{
  "azureOpenAI": {
    "endpoint": "https://sor-openai-service.openai.azure.com/",
    "apiKey": "YOUR_API_KEY",
    "apiVersion": "2024-02-15-preview",
    "deployments": {
      "embedding": "text-embedding-ada-002",
      "chat": "gpt-4"
    }
  }
}
```

### OpenAI API

**Setup**:

1. **Get API Key**: Sign up at https://platform.openai.com/
2. **Configuration**:
```json
{
  "openai": {
    "apiKey": "sk-...",
    "organization": "org-...",
    "models": {
      "embedding": "text-embedding-ada-002",
      "chat": "gpt-4-turbo-preview"
    }
  }
}
```

### Alternative Services

- **Google Vertex AI**: PaLM embeddings and Gemini models
- **AWS Bedrock**: Titan embeddings and Claude models
- **Cohere**: Embed and Command models
- **Hugging Face**: Open-source models (self-hosted)

## Implementation Examples

### Python Backend Implementation

#### Setup

```bash
pip install openai azure-identity python-dotenv
```

Create `.env` file:
```env
AZURE_OPENAI_ENDPOINT=https://your-instance.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-02-15-preview
EMBEDDING_DEPLOYMENT=text-embedding-ada-002
CHAT_DEPLOYMENT=gpt-4
```

#### Code Implementation

```python
import os
import openai
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")

EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT")
CHAT_DEPLOYMENT = os.getenv("CHAT_DEPLOYMENT")


class DocumentAIService:
    """Service for AI-powered document operations."""
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate vector embedding for text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = openai.Embedding.create(
                input=text,
                deployment_id=EMBEDDING_DEPLOYMENT
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def generate_document_summary(self, document: Dict[str, Any]) -> str:
        """
        Generate a comprehensive summary of an SOR document.
        
        Args:
            document: Dictionary containing document fields
            
        Returns:
            AI-generated summary (200-300 words)
        """
        # Extract key information
        title = document.get('title', '')
        description = document.get('description', '')
        objectives = document.get('objectives', [])
        project_type = document.get('projectType', '')
        industry = document.get('industry', '')
        complexity = document.get('complexity', '')
        
        # Build comprehensive prompt
        prompt = f"""Generate a comprehensive 200-300 word summary of this Statement of Requirements document.

Title: {title}

Project Type: {project_type}
Industry: {industry}
Complexity: {complexity}

Description:
{description}

Key Objectives:
{chr(10).join(f'- {obj}' for obj in objectives[:5])}

Requirements Summary:
- Functional Requirements: {len(document.get('requirements', {}).get('functional', []))} items
- Non-Functional Requirements: {len(document.get('requirements', {}).get('nonFunctional', []))} items
- Technical Requirements: {len(document.get('requirements', {}).get('technical', []))} items

Budget: {document.get('budget', {}).get('currency', 'USD')} {document.get('budget', {}).get('estimatedTotal', 'Not specified')}
Timeline: {document.get('timeline', {}).get('duration', {}).get('value', '')} {document.get('timeline', {}).get('duration', {}).get('unit', '')}

The summary should:
1. Describe the project's purpose and goals
2. Highlight key technical and business requirements
3. Mention critical constraints (budget, timeline, compliance)
4. Note any unique or complex aspects
5. Be written in a professional, informative tone
"""
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a technical writer specializing in summarizing project requirements documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent summaries
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            raise
    
    def explain_relevance(self, 
                         reference_document: Dict[str, Any],
                         user_project_details: str,
                         similarity_score: float) -> str:
        """
        Generate explanation of why a reference document is relevant.
        
        Args:
            reference_document: The reference SOR document
            user_project_details: User's project description
            similarity_score: Computed similarity score (0-100)
            
        Returns:
            AI-generated explanation grounded in document content
        """
        # Extract relevant fields
        title = reference_document.get('title', '')
        project_type = reference_document.get('projectType', '')
        industry = reference_document.get('industry', '')
        complexity = reference_document.get('complexity', '')
        technologies = reference_document.get('technologies', [])
        compliance = reference_document.get('complianceRequirements', [])
        
        tech_summary = ', '.join([
            f"{t.get('name')} ({t.get('category')})" 
            for t in technologies[:5]
        ])
        
        prompt = f"""You are helping a user find reference documents for their new project. Explain why this historical SOR document is a valuable reference, being specific about similarities and lessons learned.

USER'S NEW PROJECT:
{user_project_details}

REFERENCE DOCUMENT:
Title: {title}
Project Type: {project_type}
Industry: {industry}
Complexity Level: {complexity}
Technologies Used: {tech_summary}
Compliance Requirements: {', '.join(compliance)}
Similarity Score: {similarity_score}%

Provide a 3-4 sentence explanation that:
1. Identifies 2-3 specific similarities (e.g., same industry regulations, similar technology stack, comparable scope)
2. Explains what lessons or insights from this document would be valuable
3. Mentions any unique aspects that make it a particularly good reference
4. Uses a helpful, consultative tone

Ground your explanation in the specific details above. Be concrete and actionable.
"""
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable project consultant helping users find relevant reference materials."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=250
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating explanation: {e}")
            raise
    
    def extract_key_insights(self, document: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract key insights from a document for quick reference.
        
        Args:
            document: SOR document
            
        Returns:
            List of categorized insights
        """
        prompt = f"""Analyze this SOR document and extract 5 key insights that would be most valuable for someone creating a similar project. Categorize each insight.

Document: {document.get('title')}
Description: {document.get('description', '')[:500]}

Return insights in this format:
Category: <Requirements|Architecture|Budget|Timeline|Risks>
Insight: <specific, actionable insight>

Provide exactly 5 insights, one per line.
"""
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are analyzing project documents to extract key learnings."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=400
            )
            
            # Parse response into structured format
            insights = []
            lines = response.choices[0].message.content.strip().split('\n')
            
            for line in lines:
                if ':' in line:
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        insights.append({
                            "category": parts[0].replace("Category", "").strip(),
                            "insight": parts[1].replace("Insight", "").strip()
                        })
            
            return insights[:5]  # Ensure max 5 insights
        except Exception as e:
            print(f"Error extracting insights: {e}")
            return []


# Example usage
if __name__ == "__main__":
    service = DocumentAIService()
    
    # Test embedding generation
    text = "Healthcare patient portal with Epic EHR integration"
    embedding = service.generate_embedding(text)
    print(f"Generated embedding with {len(embedding)} dimensions")
    
    # Test with example document
    sample_doc = {
        "title": "Healthcare Patient Portal Implementation",
        "projectType": "Web Application",
        "industry": "Healthcare",
        "complexity": "high",
        "description": "Implementation of a patient portal with EHR integration",
        "objectives": ["Enable online health records access", "Appointment scheduling"],
        "technologies": [
            {"name": "React", "category": "Framework"},
            {"name": "Azure", "category": "Cloud Platform"}
        ],
        "complianceRequirements": ["HIPAA", "HITECH"],
        "budget": {"currency": "USD", "estimatedTotal": 3500000},
        "timeline": {"duration": {"value": 12, "unit": "months"}}
    }
    
    summary = service.generate_document_summary(sample_doc)
    print(f"\nGenerated Summary:\n{summary}")
    
    user_query = "I need to build a patient portal for a hospital with Epic integration"
    explanation = service.explain_relevance(sample_doc, user_query, 87.5)
    print(f"\nRelevance Explanation:\n{explanation}")
```

### Node.js Backend Implementation

```javascript
const { OpenAIClient, AzureKeyCredential } = require("@azure/openai");
require('dotenv').config();

const endpoint = process.env.AZURE_OPENAI_ENDPOINT;
const apiKey = process.env.AZURE_OPENAI_API_KEY;
const embeddingDeployment = process.env.EMBEDDING_DEPLOYMENT;
const chatDeployment = process.env.CHAT_DEPLOYMENT;

const client = new OpenAIClient(endpoint, new AzureKeyCredential(apiKey));

class DocumentAIService {
    async generateEmbedding(text) {
        const embeddings = await client.getEmbeddings(embeddingDeployment, [text]);
        return embeddings.data[0].embedding;
    }
    
    async generateDocumentSummary(document) {
        const prompt = `Generate a 200-300 word summary of this SOR document...
        
Title: ${document.title}
Description: ${document.description}
...`;
        
        const messages = [
            { role: "system", content: "You are a technical writer specializing in summarizing project requirements documents." },
            { role: "user", content: prompt }
        ];
        
        const result = await client.getChatCompletions(chatDeployment, messages, {
            temperature: 0.3,
            maxTokens: 500
        });
        
        return result.choices[0].message.content;
    }
    
    async explainRelevance(referenceDoc, userQuery, similarityScore) {
        const prompt = `Explain why this document is relevant...`;
        
        const messages = [
            { role: "system", content: "You are a project consultant." },
            { role: "user", content: prompt }
        ];
        
        const result = await client.getChatCompletions(chatDeployment, messages, {
            temperature: 0.5,
            maxTokens: 250
        });
        
        return result.choices[0].message.content;
    }
}

module.exports = DocumentAIService;
```

## Search Index Configuration

### Azure Cognitive Search with Vector Search

```json
{
  "name": "sor-documents",
  "fields": [
    {
      "name": "id",
      "type": "Edm.String",
      "key": true,
      "searchable": false
    },
    {
      "name": "title",
      "type": "Edm.String",
      "searchable": true,
      "filterable": false
    },
    {
      "name": "description",
      "type": "Edm.String",
      "searchable": true
    },
    {
      "name": "projectType",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "industry",
      "type": "Edm.String",
      "filterable": true,
      "facetable": true
    },
    {
      "name": "embedding",
      "type": "Collection(Edm.Single)",
      "searchable": true,
      "dimensions": 1536,
      "vectorSearchConfiguration": "vector-config"
    }
  ],
  "vectorSearch": {
    "algorithmConfigurations": [
      {
        "name": "vector-config",
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

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache
import hashlib

class CachedDocumentAIService(DocumentAIService):
    """AI service with caching for improved performance."""
    
    @lru_cache(maxsize=1000)
    def generate_embedding_cached(self, text: str) -> tuple:
        """Cached version of embedding generation."""
        embedding = self.generate_embedding(text)
        return tuple(embedding)  # Convert to tuple for caching
    
    def _get_doc_hash(self, document: Dict) -> str:
        """Generate hash for document caching."""
        doc_str = f"{document['id']}{document.get('dateModified', '')}"
        return hashlib.md5(doc_str.encode()).hexdigest()
    
    @lru_cache(maxsize=500)
    def generate_document_summary_cached(self, doc_hash: str, doc_json: str) -> str:
        """Cached version of summary generation."""
        import json
        document = json.loads(doc_json)
        return self.generate_document_summary(document)
```

### Batch Processing

```python
def generate_embeddings_batch(texts: List[str], batch_size: int = 100) -> List[List[float]]:
    """Generate embeddings in batches for efficiency."""
    embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = openai.Embedding.create(
            input=batch,
            deployment_id=EMBEDDING_DEPLOYMENT
        )
        embeddings.extend([item['embedding'] for item in response['data']])
    
    return embeddings
```

## Cost Optimization

### Token Management

```python
def estimate_cost(operation: str, input_text: str) -> float:
    """Estimate API call cost."""
    # Rough token estimation (1 token ≈ 4 characters)
    tokens = len(input_text) / 4
    
    costs = {
        'embedding': 0.0001 / 1000,  # per 1K tokens
        'gpt4': 0.03 / 1000,  # per 1K tokens (input)
    }
    
    return tokens * costs.get(operation, 0)
```

### Rate Limiting

```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=3500, period=60)  # Azure OpenAI default: 3500 RPM
def rate_limited_api_call(func, *args, **kwargs):
    """Rate-limited API call wrapper."""
    return func(*args, **kwargs)
```

## Monitoring and Logging

```python
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def log_ai_operation(operation: str, input_size: int, latency: float, success: bool):
    """Log AI operation for monitoring."""
    logger.info({
        "timestamp": datetime.utcnow().isoformat(),
        "operation": operation,
        "input_size": input_size,
        "latency_ms": latency * 1000,
        "success": success
    })
```

## Testing

```python
import unittest

class TestDocumentAIService(unittest.TestCase):
    def setUp(self):
        self.service = DocumentAIService()
    
    def test_embedding_generation(self):
        text = "Healthcare patient portal"
        embedding = self.service.generate_embedding(text)
        
        self.assertEqual(len(embedding), 1536)  # Ada-002 dimension
        self.assertTrue(all(isinstance(x, float) for x in embedding))
    
    def test_summary_generation(self):
        sample_doc = {...}  # Sample document
        summary = self.service.generate_document_summary(sample_doc)
        
        self.assertIsInstance(summary, str)
        self.assertGreater(len(summary), 100)
        self.assertLess(len(summary), 2000)
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**: Implement exponential backoff
2. **Token Limits**: Chunk large documents
3. **Latency**: Use caching and async processing
4. **Cost Overruns**: Monitor usage and set budgets

## Additional Resources

- [Azure OpenAI Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/openai/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Semantic Search Best Practices](https://learn.microsoft.com/en-us/azure/search/semantic-search-overview)
