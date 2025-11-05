# Copilot Studio - SOR Document Retrieval Agent

An intelligent Microsoft Copilot Studio agent that helps users find and retrieve similar Statement of Requirements (SOR) documents from a historical library. The agent uses AI-powered semantic search to match new project details with existing SOR documents, providing grounded recommendations and detailed explanations.

## 🎯 Features

- **Semantic Similarity Search**: AI-powered matching of project details to historical SOR documents
- **Intelligent Recommendations**: Get top N most similar documents with similarity scores
- **Grounded Explanations**: AI-generated explanations of why each document is relevant
- **Comprehensive Summaries**: Auto-generated summaries of reference documents
- **Conversational Interface**: Natural language interaction through Copilot Studio
- **Multi-dimensional Matching**: Considers project type, industry, complexity, technologies, and requirements

## 📁 Repository Structure

```
├── topics/                          # Copilot Studio topic configurations
│   └── SORDocumentRetrieval.yaml   # Main conversational flow
├── actions/                         # API action definitions
│   └── SORDocumentActions.yaml     # OpenAPI spec for document operations
├── schemas/                         # Data schemas
│   └── SORDocumentSchema.json      # JSON schema for SOR documents
├── examples/                        # Example SOR documents
│   ├── SOR-2024-0001-Healthcare-Portal.json
│   ├── SOR-2024-0015-Banking-Cloud-Migration.json
│   └── SOR-2024-0032-Retail-Ecommerce.json
└── docs/                           # Documentation
    ├── README.md                   # Setup and usage guide
    └── AI-Integration-Guide.md     # AI/LLM integration guide
```

## 🚀 Quick Start

### Prerequisites

- Microsoft Copilot Studio account
- Azure OpenAI or OpenAI API access
- Document storage and search infrastructure (Azure Cognitive Search, Elasticsearch, etc.)

### Setup

1. **Import the Topic**
   - Open Copilot Studio
   - Navigate to Topics → Import
   - Select `topics/SORDocumentRetrieval.yaml`

2. **Configure Actions**
   - Navigate to Actions → Add from file
   - Import `actions/SORDocumentActions.yaml`
   - Configure API endpoint and authentication

3. **Set Up AI Integration**
   - Follow the [AI Integration Guide](docs/AI-Integration-Guide.md)
   - Configure embedding generation and LLM services

4. **Load Example Documents**
   - Use the example SOR documents in `examples/` for testing
   - Load them into your document search index

5. **Test the Agent**
   - Use Copilot Studio Test Chat
   - Trigger with: "Find similar SOR documents"

## 📖 Documentation

- **[Setup and Usage Guide](docs/README.md)**: Complete setup instructions, usage examples, and API reference
- **[AI Integration Guide](docs/AI-Integration-Guide.md)**: Detailed guide for integrating AI/LLM services

## 💡 How It Works

1. **User Input**: User provides details about their new project
2. **Embedding Generation**: Project details are converted to vector embeddings
3. **Similarity Search**: Search index finds most similar documents using vector similarity
4. **AI Enhancement**: LLM generates summaries and relevance explanations
5. **Results Presentation**: User receives ranked documents with actionable insights

## 🔧 Technology Stack

- **Conversational AI**: Microsoft Copilot Studio
- **Embeddings**: Azure OpenAI (text-embedding-ada-002) or equivalent
- **LLM**: GPT-4 or GPT-4-turbo for summaries and explanations
- **Search**: Azure Cognitive Search, Elasticsearch, or custom implementation
- **API**: REST APIs defined in OpenAPI 3.0 format

## 📊 Example Use Case

**User**: "I'm working on a healthcare patient portal with Epic EHR integration, HIPAA compliance, and appointment scheduling for 10,000 users."

**Agent Response**:
- Retrieves top 5 similar healthcare projects
- Shows similarity scores (e.g., 87%, 82%, 78%)
- Provides summaries of each project
- Explains why each is relevant (e.g., "Both require Epic integration and HIPAA compliance")
- Includes direct links to full documents

## 🔐 Security & Compliance

- All API communications use HTTPS
- Authentication via bearer tokens or API keys
- Role-based access control for documents
- Audit logging for compliance
- Supports HIPAA, PCI-DSS, and other regulatory requirements

## 🤝 Contributing

This is an internal project. For issues or enhancements:
1. Review the documentation
2. Test thoroughly in a development environment
3. Follow the existing code and configuration patterns

## 📝 License

[Specify your organization's license]

## 🆘 Support

- Check the [troubleshooting section](docs/README.md#troubleshooting) in the documentation
- Review API logs for error details
- Contact your IT support team

## 🔮 Future Enhancements

- Multi-language support
- Advanced filtering options
- Document comparison features
- Integration with document authoring tools
- Analytics dashboard
- Automated document tagging

---

**Version**: 1.0  
**Last Updated**: 2025-11-05