# Multi-Repo Feature Ideation API

A FastAPI backend service that analyzes multiple GitHub repositories to generate feature ideas for your project. Simply provide a project description, and the API will search for similar repositories, extract their features and tech stacks, and suggest new features for your project.

## Features

- 🔍 **GitHub Repository Search**: Automatically finds similar repositories based on your project idea
- 📊 **Feature Extraction**: Uses LLM to analyze repository structure and extract key features
- 🛠️ **Tech Stack Analysis**: Identifies technologies used in similar projects
- 💡 **Feature Ideation**: Generates new feature suggestions based on analyzed repositories
- 🗄️ **Database Storage**: Stores all extracted data for future reference
- 🚀 **RESTful API**: Easy-to-use HTTP endpoints
- 🐳 **Docker Support**: Containerized deployment ready

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token
- LLM API access (Groq or similar)

### Environment Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd multi-repo-ideation-api
```

2. **Set up environment variables**
```bash
# Create a .env file
cat > .env << EOF
GITHUB_TOKEN=your_github_token_here
GROQ_API_KEY=your_groq_api_key_here
EOF
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the API**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Docker Deployment

```bash
# Using docker-compose (recommended)
docker-compose up --build

# Or using Docker directly
docker build -t multi-repo-ideation-api .
docker run -p 8000:8000 -e GITHUB_TOKEN=your_token multi-repo-ideation-api
```

## API Endpoints

### Health Check
```
GET /
```
Returns API status and health information.

### Generate Feature Ideas
```
POST /ideate
```

**Request Body:**
```json
{
  "project_idea": "expense tracker app",
  "max_repos": 3
}
```

**Response:**
```json
{
  "project_idea": "expense tracker app",
  "analyzed_repos": [
    {
      "name": "owner/repo-name",
      "url": "https://github.com/owner/repo-name",
      "features": ["Budget tracking", "Expense categorization", "..."],
      "tech_stack": ["React", "Node.js", "MongoDB", "..."]
    }
  ],
  "aggregated_features": ["Budget tracking", "Expense categorization", "..."],
  "aggregated_tech_stack": ["React", "Node.js", "MongoDB", "..."],
  "suggested_features": "Based on the analysis, here are some new feature ideas...",
  "total_repos_processed": 3
}
```

### API Status
```
GET /status
```
Returns configuration and system status information.

## Testing

Test the API using the provided example client:

```bash
python example_client.py
```

Or test manually with curl:

```bash
# Health check
curl http://localhost:8000/

# Test ideation
curl -X POST http://localhost:8000/ideate \
  -H "Content-Type: application/json" \
  -d '{"project_idea": "task management app", "max_repos": 2}'
```

## Project Structure

```
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── example_client.py      # Test client
├── extractor/             # Repository processing modules
│   ├── clone_repo.py      # Git repository cloning
│   ├── parse_repo.py      # Repository structure parsing
│   └── summarizer.py      # LLM-based feature extraction
├── database/              # Database operations
│   └── db.py             # SQLite database functions
├── utils/                 # Utility functions
│   └── helpers.py        # Text processing helpers
└── github_search.py      # GitHub API integration
```

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub Personal Access Token (required for API access)
- `GROQ_API_KEY`: Groq API key for LLM processing (or your preferred LLM provider)

### API Limits

- Maximum repositories per request: 10
- Request timeout: 5 minutes
- Project idea length: 3-500 characters

## Database Schema

The API uses SQLite with the following tables:

- `projects`: Stores project information
- `features`: Extracted features from repositories
- `tech_stack`: Technology stack items
- `ideated_features`: Generated feature suggestions

## Error Handling

The API provides comprehensive error handling:

- **400 Bad Request**: Invalid input parameters
- **404 Not Found**: No repositories found or no features extracted
- **500 Internal Server Error**: Processing errors or system issues

## Performance Considerations

- Repository cloning and analysis can be time-consuming
- Consider implementing caching for frequently requested project ideas
- Monitor disk space usage for cloned repositories
- The API processes repositories sequentially (can be optimized for parallel processing)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the API status endpoint: `GET /status`
- Review logs for detailed error information
- Ensure all environment variables are correctly set
- Verify GitHub token has proper permissions

## Roadmap

- [ ] Parallel repository processing
- [ ] Redis caching for improved performance
- [ ] Support for private repositories
- [ ] Advanced filtering and ranking of repositories
- [ ] Integration with additional LLM providers
- [ ] Real-time processing status updates
- [ ] Export functionality for generated ideas