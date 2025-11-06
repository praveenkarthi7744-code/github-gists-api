"""
Automated tests for the GitHub Gists API server.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from app import app, fetch_user_gists


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the health check endpoint."""
    
    def test_health_check(self, client):
        """Test that health check endpoint returns healthy status."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestRootEndpoint:
    """Tests for the root endpoint."""
    
    def test_root_endpoint(self, client):
        """Test that root endpoint returns API information."""
        response = client.get('/')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'usage' in data
        assert 'endpoints' in data


class TestUserGistsEndpoint:
    """Tests for the user gists endpoint."""
    
    @patch('app.requests.get')
    def test_successful_gists_fetch(self, mock_get, client):
        """Test successful fetching of user gists."""
        # Mock GitHub API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 'abc123',
                'description': 'Test gist',
                'public': True,
                'files': {
                    'test.py': {'filename': 'test.py'}
                },
                'html_url': 'https://gist.github.com/abc123',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-02T00:00:00Z'
            }
        ]
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/testuser')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert 'gists' in data
        assert len(data['gists']) == 1
        assert data['gists'][0]['id'] == 'abc123'
        assert data['gists'][0]['description'] == 'Test gist'
        assert data['count'] == 1
    
    @patch('app.requests.get')
    def test_user_not_found(self, mock_get, client):
        """Test handling of non-existent user."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/nonexistentuser123456')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()
    
    @patch('app.requests.get')
    def test_rate_limit_exceeded(self, mock_get, client):
        """Test handling of GitHub API rate limit."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/testuser')
        assert response.status_code == 429
        
        data = json.loads(response.data)
        assert 'error' in data
        assert 'rate limit' in data['error'].lower()
    
    @patch('app.requests.get')
    def test_octocat_user(self, mock_get, client):
        """Test with the example user 'octocat'."""
        # Mock response for octocat user
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 'gist1',
                'description': 'Octocat gist 1',
                'public': True,
                'files': {
                    'hello.rb': {'filename': 'hello.rb'}
                },
                'html_url': 'https://gist.github.com/gist1',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-02T00:00:00Z'
            },
            {
                'id': 'gist2',
                'description': 'Octocat gist 2',
                'public': True,
                'files': {
                    'test.py': {'filename': 'test.py'}
                },
                'html_url': 'https://gist.github.com/gist2',
                'created_at': '2023-02-01T00:00:00Z',
                'updated_at': '2023-02-02T00:00:00Z'
            }
        ]
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/octocat')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['username'] == 'octocat'
        assert len(data['gists']) == 2
        assert data['count'] == 2
    
    def test_invalid_pagination_parameters(self, client):
        """Test validation of pagination parameters."""
        # Test invalid per_page (too high)
        response = client.get('/testuser?per_page=101')
        assert response.status_code == 400
        
        # Test invalid per_page (negative)
        response = client.get('/testuser?per_page=-1')
        assert response.status_code == 400
        
        # Test invalid page (negative)
        response = client.get('/testuser?page=-1')
        assert response.status_code == 400
    
    @patch('app.requests.get')
    def test_pagination_query_parameters(self, mock_get, client):
        """Test that pagination parameters are passed correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/testuser?per_page=50&page=2')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['page'] == 2
        assert data['per_page'] == 50
    
    @patch('app.requests.get')
    def test_empty_gists_list(self, mock_get, client):
        """Test user with no gists."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/testuser')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['username'] == 'testuser'
        assert len(data['gists']) == 0
        assert data['count'] == 0
    
    @patch('app.requests.get')
    def test_gist_without_description(self, mock_get, client):
        """Test gist without description field."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 'abc123',
                'public': True,
                'files': {
                    'test.py': {'filename': 'test.py'}
                },
                'html_url': 'https://gist.github.com/abc123',
                'created_at': '2023-01-01T00:00:00Z',
                'updated_at': '2023-01-02T00:00:00Z'
            }
        ]
        mock_get.return_value = mock_response
        
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/testuser')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['gists'][0]['description'] == 'No description'


class TestIntegration:
    """Integration tests that make real API calls."""
    
    def test_real_octocat_user(self, client):
        """
        Integration test with real GitHub API call to octocat user.
        This test makes a real API call - may be slow or fail due to rate limits.
        """
        # Clear cache before test
        fetch_user_gists.cache_clear()
        
        response = client.get('/octocat')
        
        # Should succeed or hit rate limit
        assert response.status_code in [200, 429]
        
        data = json.loads(response.data)
        
        if response.status_code == 200:
            assert data['username'] == 'octocat'
            assert 'gists' in data
            assert 'count' in data
            # octocat typically has gists, but we can't guarantee the exact count
            assert isinstance(data['gists'], list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

