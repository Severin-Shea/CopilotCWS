"""
Example API Implementation for SOR Document Retrieval

⚠️  IMPORTANT: This is a REFERENCE IMPLEMENTATION for development and testing only!
    
    For production use:
    - Remove debug mode (FLASK_DEBUG=False)
    - Implement proper authentication and authorization
    - Use a real database instead of in-memory storage
    - Add rate limiting and input validation
    - Use a production WSGI server (gunicorn, uwsgi)
    - Follow security best practices in docs/Deployment-Guide.md
    
This example shows how to implement the API endpoints defined in 
actions/SORDocumentActions.yaml with Azure OpenAI integration.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from typing import List, Dict, Any
import json
from datetime import datetime
import numpy as np
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure Azure OpenAI
openai.api_type = "azure"
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

EMBEDDING_DEPLOYMENT = os.getenv("EMBEDDING_DEPLOYMENT", "text-embedding-ada-002")
CHAT_DEPLOYMENT = os.getenv("CHAT_DEPLOYMENT", "gpt-4")

# In-memory document store (replace with actual database/search index)
DOCUMENTS_STORE = []


class DocumentAIService:
    """Service for AI-powered document operations."""
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generate vector embedding for text."""
        try:
            response = openai.Embedding.create(
                input=text,
                deployment_id=EMBEDDING_DEPLOYMENT
            )
            return response['data'][0]['embedding']
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    @staticmethod
    def generate_summary(document: Dict[str, Any]) -> str:
        """Generate document summary."""
        prompt = f"""Generate a concise 200-300 word summary of this Statement of Requirements document.

Title: {document.get('title', '')}
Project Type: {document.get('projectType', '')}
Industry: {document.get('industry', '')}
Description: {document.get('description', '')}

Objectives:
{chr(10).join(f'- {obj}' for obj in document.get('objectives', [])[:5])}

The summary should cover:
1. Project purpose and goals
2. Key requirements
3. Critical constraints (budget, timeline)
4. Unique aspects
"""
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a technical writer specializing in project requirements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating summary: {e}")
            return f"Summary: {document.get('description', '')[:300]}"
    
    @staticmethod
    def explain_relevance(doc: Dict[str, Any], query: str, score: float) -> str:
        """Generate relevance explanation."""
        prompt = f"""Explain why this SOR document is a valuable reference for the user's project.

USER'S PROJECT:
{query}

REFERENCE DOCUMENT:
Title: {doc.get('title', '')}
Type: {doc.get('projectType', '')}
Industry: {doc.get('industry', '')}
Complexity: {doc.get('complexity', '')}
Similarity: {score:.1f}%

Provide a 3-4 sentence explanation that:
1. Identifies specific similarities
2. Explains valuable lessons or insights
3. Mentions unique aspects that make it a good reference

Be specific and actionable."""
        
        try:
            response = openai.ChatCompletion.create(
                deployment_id=CHAT_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a project consultant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=250
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating explanation: {e}")
            return f"This document is relevant due to its {score:.1f}% similarity score."


def load_example_documents():
    """Load example documents into the store."""
    global DOCUMENTS_STORE
    examples_dir = os.path.join(os.path.dirname(__file__), 'examples')
    
    if not os.path.exists(examples_dir):
        print(f"Examples directory not found: {examples_dir}")
        return
    
    ai_service = DocumentAIService()
    
    for filename in os.listdir(examples_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(examples_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    doc = json.load(f)
                    
                    # Generate embedding
                    text = f"{doc['title']} {doc['description']}"
                    embedding = ai_service.generate_embedding(text)
                    
                    # Add to store with embedding
                    doc['embedding'] = embedding
                    DOCUMENTS_STORE.append(doc)
                    print(f"Loaded document: {doc['id']}")
            except Exception as e:
                print(f"Error loading {filename}: {e}")
    
    print(f"Loaded {len(DOCUMENTS_STORE)} documents")


@app.route('/api/search/similar', methods=['POST'])
def search_similar_documents():
    """
    Search for similar SOR documents.
    
    POST /api/search/similar
    Body: {
        "projectDetails": "string",
        "topN": integer (1-10),
        "filters": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'projectDetails' not in data:
            return jsonify({"error": "projectDetails is required"}), 400
        
        project_details = data['projectDetails']
        top_n = min(max(int(data.get('topN', 5)), 1), 10)
        filters = data.get('filters', {})
        
        # Generate embedding for query
        ai_service = DocumentAIService()
        query_embedding = ai_service.generate_embedding(project_details)
        
        # Calculate similarities
        results = []
        for doc in DOCUMENTS_STORE:
            # Apply filters
            if filters.get('projectType') and doc.get('projectType') not in filters['projectType']:
                continue
            if filters.get('industry') and doc.get('industry') not in filters['industry']:
                continue
            if filters.get('complexity') and doc.get('complexity') != filters['complexity']:
                continue
            
            # Calculate similarity
            similarity = ai_service.cosine_similarity(query_embedding, doc['embedding'])
            similarity_score = similarity * 100  # Convert to percentage
            
            results.append({
                "id": doc['id'],
                "title": doc['title'],
                "projectType": doc['projectType'],
                "industry": doc['industry'],
                "complexity": doc['complexity'],
                "dateCreated": doc['dateCreated'],
                "similarityScore": round(similarity_score, 2),
                "keyTerms": doc.get('searchMetadata', {}).get('keyTerms', [])
            })
        
        # Sort by similarity and get top N
        results.sort(key=lambda x: x['similarityScore'], reverse=True)
        top_results = results[:top_n]
        
        return jsonify({
            "documents": top_results,
            "totalResults": len(results),
            "searchMetadata": {
                "searchTime": 0.5,  # Mock value
                "algorithm": "cosine-similarity"
            }
        })
    
    except Exception as e:
        # Log the full error for debugging
        print(f"Error in search: {e}")
        import traceback
        traceback.print_exc()
        
        # Return generic error message to user (don't expose stack traces)
        return jsonify({"error": "An error occurred while searching for documents. Please try again."}), 500


@app.route('/api/documents/<document_id>/details', methods=['GET'])
def get_document_details(document_id):
    """
    Get detailed information about a specific document.
    
    GET /api/documents/{documentId}/details?contextProjectDetails=...
    """
    try:
        # Find document
        doc = next((d for d in DOCUMENTS_STORE if d['id'] == document_id), None)
        
        if not doc:
            return jsonify({"error": "Document not found"}), 404
        
        context_details = request.args.get('contextProjectDetails', '')
        
        # Generate AI-powered content
        ai_service = DocumentAIService()
        summary = ai_service.generate_summary(doc)
        
        # Calculate similarity if context provided
        similarity_score = 0.0
        if context_details:
            query_embedding = ai_service.generate_embedding(context_details)
            similarity = ai_service.cosine_similarity(query_embedding, doc['embedding'])
            similarity_score = similarity * 100
        
        relevance_explanation = ai_service.explain_relevance(
            doc, 
            context_details or "General reference",
            similarity_score
        )
        
        # Build response
        response = {
            "id": doc['id'],
            "title": doc['title'],
            "summary": summary,
            "link": f"https://documents.example.com/{doc['id']}",  # Mock URL
            "similarityScore": round(similarity_score, 2),
            "relevanceExplanation": relevance_explanation,
            "metadata": {
                "projectType": doc.get('projectType'),
                "industry": doc.get('industry'),
                "complexity": doc.get('complexity'),
                "dateCreated": doc.get('dateCreated'),
                "author": doc.get('author', {}).get('name'),
                "version": doc.get('version'),
                "status": doc.get('status'),
                "tags": doc.get('tags', [])
            },
            "keyInsights": [
                {
                    "category": "Requirements",
                    "insight": f"Contains {len(doc.get('requirements', {}).get('functional', []))} functional requirements"
                },
                {
                    "category": "Technologies",
                    "insight": f"Uses {len(doc.get('technologies', []))} different technologies"
                }
            ],
            "relatedDocuments": [
                {"id": rel_id, "title": f"Related Document {rel_id}", "relationship": "Similar project"}
                for rel_id in doc.get('relatedDocuments', [])[:3]
            ]
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Log the full error for debugging
        print(f"Error getting document details: {e}")
        import traceback
        traceback.print_exc()
        
        # Return generic error message to user (don't expose stack traces)
        return jsonify({"error": "An error occurred while retrieving document details. Please try again."}), 500


@app.route('/api/documents/upload', methods=['POST'])
def upload_document():
    """
    Upload a new SOR document to the library.
    
    POST /api/documents/upload
    Body: multipart/form-data with 'file' and 'metadata'
    """
    try:
        # This is a simplified implementation
        # In production, handle file uploads properly
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        metadata = json.loads(request.form.get('metadata', '{}'))
        
        if not metadata.get('title') or not metadata.get('projectType'):
            return jsonify({"error": "title and projectType are required"}), 400
        
        # Generate document ID
        doc_id = f"SOR-{datetime.now().year}-{len(DOCUMENTS_STORE) + 1:04d}"
        
        # Create document record
        new_doc = {
            "id": doc_id,
            "title": metadata['title'],
            "projectType": metadata['projectType'],
            "industry": metadata.get('industry', 'Other'),
            "complexity": metadata.get('complexity', 'medium'),
            "description": metadata.get('description', ''),
            "tags": metadata.get('tags', []),
            "dateCreated": datetime.utcnow().isoformat() + 'Z',
            "status": "draft"
        }
        
        # Generate embedding
        ai_service = DocumentAIService()
        text = f"{new_doc['title']} {new_doc['description']}"
        new_doc['embedding'] = ai_service.generate_embedding(text)
        
        # Add to store
        DOCUMENTS_STORE.append(new_doc)
        
        return jsonify({
            "documentId": doc_id,
            "message": "Document uploaded successfully"
        }), 201
    
    except Exception as e:
        # Log the full error for debugging
        print(f"Error uploading document: {e}")
        import traceback
        traceback.print_exc()
        
        # Return generic error message to user (don't expose stack traces)
        return jsonify({"error": "An error occurred while uploading the document. Please try again."}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "documents_loaded": len(DOCUMENTS_STORE),
        "timestamp": datetime.utcnow().isoformat()
    })


if __name__ == '__main__':
    print("Starting SOR Document API...")
    
    # Load example documents on startup
    load_example_documents()
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # WARNING: Never set FLASK_DEBUG=True in production!
    # Debug mode allows arbitrary code execution and should only be used in development
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
