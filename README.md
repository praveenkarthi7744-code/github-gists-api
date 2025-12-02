# GitHub Gists API

A simple HTTP web server API that fetches and returns a user's publicly available GitHub Gists.

## Features

- ✅ Fetch public gists for any GitHub user
- ✅ RESTful API with JSON responses
- ✅ Pagination support
- ✅ LRU caching for improved performance
- ✅ Comprehensive automated tests
- ✅ Docker containerization
- ✅ Health check endpoint
- ✅ Error handling and validation

## API Endpoints

### `GET /<username>`

Retrieve public gists for a GitHub user.

**Query Parameters:**
- `per_page` (optional): Number of results per page (default: 30, max: 100)
- `page` (optional): Page number (default: 1)

**Example Request:**
```bash
curl http://localhost:8080/octocat
curl http://localhost:8080/octocat?per_page=50&page=2
```

**Example Response:**
```json
{
  "username": "octocat",
  "gists": [
    {
      "id": "abc123",
      "description": "Example gist",
      "public": true,
      "files": ["hello.rb"],
      "url": "https://gist.github.com/abc123",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  ],
  "count": 1,
  "page": 1,
  "per_page": 30
}
```

### `GET /health`

Health check endpoint.

**Example Response:**
```json
{
  "status": "healthy"
}
```

### `GET /`

API information and usage instructions.

## Running Locally

### Prerequisites

- Python 3.11 or higher
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The API will be available at `http://localhost:8080`

## Running Tests

Run the automated test suite:

```bash
pytest test_app.py -v
```

Run with coverage:

```bash
pytest test_app.py -v --cov=app --cov-report=html
```

## Docker Usage

### Building the Docker Image

```bash
docker build -t github-gists-api .
```

### Running the Container

```bash
docker run -p 8080:8080 github-gists-api
```

The API will be available at `http://localhost:8080`

### Testing the Docker Container

```bash
# Check health
curl http://localhost:8080/health

# Fetch gists for octocat user
curl http://localhost:8080/octocat
```

### Docker Compose (Optional)

You can also use Docker Compose for easier management:

```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8080:8080"
    restart: unless-stopped
```

Run with:
```bash
docker-compose up
```

## Architecture

### Technology Stack

- **Python 3.11**: Programming language
- **Flask**: Web framework
- **Requests**: HTTP library for GitHub API calls
- **Pytest**: Testing framework

### Design Decisions

1. **Caching**: Implements LRU cache to reduce GitHub API calls and improve response times
2. **Error Handling**: Comprehensive error handling for network issues, rate limits, and invalid inputs
3. **Pagination**: Supports GitHub's pagination for users with many gists
4. **Data Simplification**: Returns only relevant gist information in a clean format
5. **Security**: Docker container runs as non-root user
6. **Health Checks**: Built-in health check endpoint for monitoring

## Error Responses

### User Not Found (404)
```json
{
  "error": "User 'username' not found"
}
```

### Rate Limit Exceeded (429)
```json
{
  "error": "GitHub API rate limit exceeded"
}
```

### Invalid Parameters (400)
```json
{
  "error": "per_page must be between 1 and 100"
}
```

## Testing with Example User

The `octocat` user is GitHub's mascot and has public gists that can be used for testing:

```bash
curl http://localhost:8080/octocat
```

## Performance Considerations

- **Caching**: LRU cache reduces redundant API calls
- **Timeout**: 10-second timeout for GitHub API requests
- **Pagination**: Supports efficient data retrieval for users with many gists

## Rate Limiting

The GitHub API has rate limits:
- **Unauthenticated requests**: 60 per hour per IP
- **Authenticated requests**: 5,000 per hour (not implemented in this version)

To add authentication, you can extend the code to accept a GitHub token.

## Future Enhancements

Possible improvements for production use:

- [ ] GitHub authentication for higher rate limits
- [ ] Redis caching for distributed systems
- [ ] Request rate limiting on the API side
- [ ] Metrics and logging integration
- [ ] CORS support for browser clients
- [ ] API versioning
- [ ] OpenAPI/Swagger documentation

## License

This project is provided as-is for educational purposes.

## Author

Built as a technical exercise to demonstrate API development, testing, and containerization skills.

