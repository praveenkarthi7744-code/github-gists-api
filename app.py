"""
GitHub Gists API Server
A simple Flask web server that fetches and returns a user's public GitHub Gists.
"""

import requests
from flask import Flask, jsonify, request
from functools import lru_cache
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# GitHub API configuration
GITHUB_API_BASE_URL = "https://api.github.com"
GITHUB_API_TIMEOUT = 10  # seconds


@lru_cache(maxsize=128)
def fetch_user_gists(username, per_page=30, page=1):
    """
    Fetch public gists for a given GitHub user.
    
    Args:
        username: GitHub username
        per_page: Number of results per page (max 100)
        page: Page number for pagination
    
    Returns:
        Tuple of (gists_list, error_message)
    """
    try:
        url = f"{GITHUB_API_BASE_URL}/users/{username}/gists"
        params = {
            'per_page': min(per_page, 100),
            'page': page
        }
        
        logger.info(f"Fetching gists for user: {username}, page: {page}")
        
        response = requests.get(url, params=params, timeout=GITHUB_API_TIMEOUT)
        
        if response.status_code == 404:
            return None, f"User '{username}' not found"
        elif response.status_code == 403:
            return None, "GitHub API rate limit exceeded"
        elif response.status_code != 200:
            return None, f"GitHub API error: {response.status_code}"
        
        gists = response.json()
        
        # Transform gists data to a simpler format
        simplified_gists = []
        for gist in gists:
            simplified_gists.append({
                'id': gist.get('id'),
                'description': gist.get('description', 'No description'),
                'public': gist.get('public', True),
                'files': list(gist.get('files', {}).keys()),
                'url': gist.get('html_url'),
                'created_at': gist.get('created_at'),
                'updated_at': gist.get('updated_at')
            })
        
        return simplified_gists, None
        
    except requests.exceptions.Timeout:
        return None, "Request to GitHub API timed out"
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching gists: {str(e)}")
        return None, f"Error connecting to GitHub API: {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None, f"Internal server error: {str(e)}"


@app.route('/<username>', methods=['GET'])
def get_user_gists(username):
    """
    API endpoint to get a user's public gists.
    
    Query parameters:
        - per_page: Number of results per page (default: 30, max: 100)
        - page: Page number (default: 1)
    """
    # Get pagination parameters from query string
    per_page = request.args.get('per_page', default=30, type=int)
    page = request.args.get('page', default=1, type=int)
    
    # Validate parameters
    if per_page < 1 or per_page > 100:
        return jsonify({'error': 'per_page must be between 1 and 100'}), 400
    if page < 1:
        return jsonify({'error': 'page must be greater than 0'}), 400
    
    # Fetch gists
    gists, error = fetch_user_gists(username, per_page, page)
    
    if error:
        status_code = 404 if "not found" in error.lower() else 500
        if "rate limit" in error.lower():
            status_code = 429
        return jsonify({'error': error}), status_code
    
    return jsonify({
        'username': username,
        'gists': gists,
        'count': len(gists),
        'page': page,
        'per_page': per_page
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy'}), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint with API information."""
    return jsonify({
        'message': 'GitHub Gists API',
        'usage': 'GET /<username> to retrieve public gists for a user',
        'example': '/octocat',
        'query_parameters': {
            'per_page': 'Number of results per page (default: 30, max: 100)',
            'page': 'Page number (default: 1)'
        },
        'endpoints': {
            '/': 'API information',
            '/<username>': 'Get user gists',
            '/health': 'Health check'
        }
    })


if __name__ == '__main__':
    # Run the server on port 8080
    app.run(host='0.0.0.0', port=8080, debug=False)

