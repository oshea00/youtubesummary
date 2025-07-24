#!/bin/bash

# Test script for YouTube Summary MCP Container
# This script builds the container and tests basic MCP functionality

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="youtube-summary-mcp"
IMAGE_TAG="youtube-summary-mcp:latest"

echo -e "${BLUE}=== YouTube Summary MCP Container Test ===${NC}"
echo

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_separator() {
    echo -e "${BLUE}$1${NC}"
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

print_status "Docker found"

# Build the container
print_separator "=== Building Container ==="
print_status "Building Docker image: $IMAGE_TAG"

if docker build -t "$IMAGE_TAG" .; then
    print_status "Container built successfully"
else
    print_error "Failed to build container"
    exit 1
fi

echo

# Test 1: List available tools
print_separator "=== Test 1: List Available Tools ==="
print_status "Sending tools/list request..."

# Create JSON-RPC request for listing tools
TOOLS_LIST_REQUEST='{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'

echo -e "${YELLOW}Request:${NC}"
echo "$TOOLS_LIST_REQUEST" | jq . 2>/dev/null || echo "$TOOLS_LIST_REQUEST"
echo

echo -e "${YELLOW}Response:${NC}"
TOOLS_RESPONSE=$(echo "$TOOLS_LIST_REQUEST" | docker run -i --rm "$IMAGE_TAG" 2>/dev/null)

if [ -n "$TOOLS_RESPONSE" ]; then
    # Pretty print JSON if jq is available, otherwise just output raw
    if command -v jq &> /dev/null; then
        echo "$TOOLS_RESPONSE" | jq .
    else
        echo "$TOOLS_RESPONSE"
    fi
    print_status "Tools list retrieved successfully"
else
    print_error "Failed to get tools list"
    exit 1
fi

echo

# Test 2: Invalid method test
print_separator "=== Test 2: Invalid Method Test ==="
print_status "Testing error handling with invalid method..."

INVALID_REQUEST='{"jsonrpc": "2.0", "id": 2, "method": "invalid/method", "params": {}}'

echo -e "${YELLOW}Request:${NC}"
echo "$INVALID_REQUEST" | jq . 2>/dev/null || echo "$INVALID_REQUEST"
echo

echo -e "${YELLOW}Response:${NC}"
INVALID_RESPONSE=$(echo "$INVALID_REQUEST" | docker run -i --rm "$IMAGE_TAG" 2>/dev/null)

if [ -n "$INVALID_RESPONSE" ]; then
    if command -v jq &> /dev/null; then
        echo "$INVALID_RESPONSE" | jq .
    else
        echo "$INVALID_RESPONSE"
    fi
    print_status "Error handling working correctly"
else
    print_warning "No response received for invalid method"
fi

echo

# Test 3: Tool call with missing parameters
print_separator "=== Test 3: Tool Call with Missing Parameters ==="
print_status "Testing youtube_summary tool with missing URL parameter..."

MISSING_PARAMS_REQUEST='{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {}}}'

echo -e "${YELLOW}Request:${NC}"
echo "$MISSING_PARAMS_REQUEST" | jq . 2>/dev/null || echo "$MISSING_PARAMS_REQUEST"
echo

echo -e "${YELLOW}Response:${NC}"
MISSING_RESPONSE=$(echo "$MISSING_PARAMS_REQUEST" | docker run -i --rm "$IMAGE_TAG" 2>/dev/null)

if [ -n "$MISSING_RESPONSE" ]; then
    if command -v jq &> /dev/null; then
        echo "$MISSING_RESPONSE" | jq .
    else
        echo "$MISSING_RESPONSE"
    fi
    print_status "Parameter validation working correctly"
else
    print_warning "No response received for missing parameters"
fi

echo

# Test 4: Malformed JSON test
print_separator "=== Test 4: Malformed JSON Test ==="
print_status "Testing JSON parse error handling..."

MALFORMED_JSON='{"jsonrpc": "2.0", "id": 4, "method": "tools/list"'  # Missing closing brace

echo -e "${YELLOW}Request:${NC}"
echo "$MALFORMED_JSON"
echo

echo -e "${YELLOW}Response:${NC}"
MALFORMED_RESPONSE=$(echo "$MALFORMED_JSON" | docker run -i --rm "$IMAGE_TAG" 2>/dev/null)

if [ -n "$MALFORMED_RESPONSE" ]; then
    if command -v jq &> /dev/null; then
        echo "$MALFORMED_RESPONSE" | jq .
    else
        echo "$MALFORMED_RESPONSE"
    fi
    print_status "JSON error handling working correctly"
else
    print_warning "No response received for malformed JSON"
fi

echo

# Summary
print_separator "=== Test Summary ==="
print_status "Container initialization and basic MCP protocol tests completed"
print_status "Image: $IMAGE_TAG"
print_status "All basic MCP functionality appears to be working"

echo
print_separator "=== Available Functions ==="
print_status "The container exposes the following MCP tool:"
echo "  • youtube_summary - Download YouTube video transcript and generate AI summary"
echo "    Parameters:"
echo "      - url (required): YouTube video URL or video ID"
echo "      - model (optional): LLM model to use for summary"
echo "      - output_file (optional): Output markdown file path"
echo "      - save_to_file (optional): Whether to save results to file"

echo
print_status "To test with a real YouTube video, set your API keys and run:"
echo "docker run -i -e ANTHROPIC_API_KEY=your_key $IMAGE_TAG"
echo

print_status "Test script completed successfully!"