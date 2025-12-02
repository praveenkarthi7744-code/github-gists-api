#!/bin/bash

# Quick test script for the GitHub Gists API
# This script assumes the API is running on localhost:8080

API_URL="${API_URL:-http://localhost:8080}"

echo "==================================="
echo "GitHub Gists API Test Script"
echo "==================================="
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "-----------------------------------"
curl -s "$API_URL/health" | python -m json.tool
echo ""
echo ""

# Test 2: Root endpoint
echo "Test 2: Root Endpoint (API Info)"
echo "-----------------------------------"
curl -s "$API_URL/" | python -m json.tool
echo ""
echo ""

# Test 3: Fetch gists for octocat user
echo "Test 3: Fetch Gists for 'octocat'"
echo "-----------------------------------"
curl -s "$API_URL/octocat" | python -m json.tool
echo ""
echo ""

# Test 4: Test with pagination
echo "Test 4: Fetch Gists with Pagination (per_page=5)"
echo "-----------------------------------"
curl -s "$API_URL/octocat?per_page=5" | python -m json.tool
echo ""
echo ""

# Test 5: Test with non-existent user
echo "Test 5: Non-existent User (should return 404)"
echo "-----------------------------------"
curl -s -w "\nHTTP Status: %{http_code}\n" "$API_URL/thisisnotarealuser12345678"
echo ""
echo ""

echo "==================================="
echo "Tests Complete!"
echo "==================================="

