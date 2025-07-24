# Testing the YouTube Summary MCP Container

This document explains how to test the YouTube Summary MCP container using the MCP development tools.

## Prerequisites

1. **Docker**: Ensure Docker is installed and running
2. **MCP CLI**: Install the MCP development tools
   ```bash
   npm install -g @modelcontextprotocol/cli
   ```

## Building the Container

First, build the Docker container:

```bash
docker build -t youtube-summary-mcp .
```

## Testing with MCP Dev Tools

### 1. Test Tool Discovery

List available tools to verify the MCP server is working:

```bash
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | docker run -i youtube-summary-mcp
```

Expected response should include the `youtube_summary` tool with its parameters.

### 2. Test YouTube Summary Tool

Test the main functionality with a sample YouTube video:

```bash
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "model": "claude-sonnet-4-20250514", "save_to_file": false}}}' | docker run -i youtube-summary-mcp
```

### 3. Interactive Testing

For more interactive testing, you can use the MCP inspector:

```bash
# Run the container in the background
docker run -d --name mcp-test youtube-summary-mcp

# Use MCP inspector to connect and test
mcp-inspector docker exec -i mcp-test python mcp_wrapper.py
```

### 4. Testing with Different Parameters

Test various parameter combinations:

#### Basic URL test:
```bash
echo '{"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {"url": "https://youtu.be/dQw4w9WgXcQ"}}}' | docker run -i youtube-summary-mcp
```

#### With custom model:
```bash
echo '{"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "model": "gpt-4"}}}' | docker run -i youtube-summary-mcp
```

#### With file saving enabled:
```bash
echo '{"jsonrpc": "2.0", "id": 5, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ", "save_to_file": true, "output_file": "test_summary.md"}}}' | docker run -i youtube-summary-mcp
```

## Expected Responses

### Tool List Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "youtube_summary",
        "description": "Download YouTube video transcript and generate AI summary",
        "inputSchema": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "description": "YouTube video URL or video ID"
            },
            "model": {
              "type": "string",
              "description": "LLM model to use for summary",
              "default": "claude-sonnet-4-20250514"
            },
            "output_file": {
              "type": "string",
              "description": "Output markdown file path",
              "default": "transcript.md"
            },
            "save_to_file": {
              "type": "boolean",
              "description": "Whether to save results to file",
              "default": false
            }
          },
          "required": ["url"]
        }
      }
    ]
  }
}
```

### Successful Tool Call Response
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"video_id\": \"dQw4w9WgXcQ\",\n  \"video_url\": \"https://www.youtube.com/watch?v=dQw4w9WgXcQ\",\n  \"transcript\": \"[transcript content here]\",\n  \"summary\": \"[AI-generated summary here]\",\n  \"model_used\": \"claude-sonnet-4-20250514\"\n}"
      }
    ]
  }
}
```

## Testing Error Cases

### Invalid URL
```bash
echo '{"jsonrpc": "2.0", "id": 6, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {"url": "invalid-url"}}}' | docker run -i youtube-summary-mcp
```

### Missing Required Parameter
```bash
echo '{"jsonrpc": "2.0", "id": 7, "method": "tools/call", "params": {"name": "youtube_summary", "arguments": {}}}' | docker run -i youtube-summary-mcp
```

### Unknown Tool
```bash
echo '{"jsonrpc": "2.0", "id": 8, "method": "tools/call", "params": {"name": "unknown_tool", "arguments": {}}}' | docker run -i youtube-summary-mcp
```

## Environment Variables

The container may require API keys for LLM services. Set them when running:

```bash
docker run -i -e ANTHROPIC_API_KEY=your_key_here youtube-summary-mcp
```

## Debugging

To debug issues, run the container with verbose output:

```bash
docker run -i --rm youtube-summary-mcp 2>&1 | tee debug.log
```

Or enter the container for manual testing:

```bash
docker run -it --entrypoint /bin/bash youtube-summary-mcp
```

## Integration Testing

For full integration testing with an MCP client:

1. Create an MCP client configuration file
2. Point it to the Docker container as a server
3. Test the tool calls through the client interface

This ensures the container works properly in real MCP environments.