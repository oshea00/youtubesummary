#!/usr/bin/env python3
"""
MCP wrapper for YouTube Summary functionality.
"""

import json
import sys
from typing import Dict, Any, List, Optional
from src.youtubesummary.youtube_summary import (
    extract_video_id,
    get_transcript,
    generate_summary,
    save_to_markdown
)


class MCPWrapper:
    """MCP wrapper for YouTube summary functions."""
    
    def __init__(self):
        self.tools = {
            "youtube_summary": {
                "description": "Download YouTube video transcript and generate AI summary",
                "parameters": {
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
                            "default": False
                        }
                    },
                    "required": ["url"]
                }
            }
        }
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools."""
        return [
            {
                "name": name,
                "description": tool["description"],
                "inputSchema": tool["parameters"]
            }
            for name, tool in self.tools.items()
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool with given arguments."""
        if name not in self.tools:
            return {
                "error": f"Unknown tool: {name}",
                "isError": True
            }
        
        try:
            if name == "youtube_summary":
                return self._youtube_summary(arguments)
            else:
                return {
                    "error": f"Tool {name} not implemented",
                    "isError": True
                }
        except Exception as e:
            return {
                "error": f"Error calling tool {name}: {str(e)}",
                "isError": True
            }
    
    def _youtube_summary(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Generate YouTube video summary."""
        url = args.get("url")
        model = args.get("model", "claude-sonnet-4-20250514")
        output_file = args.get("output_file", "transcript.md")
        save_to_file = args.get("save_to_file", False)
        
        if not url:
            return {
                "error": "URL is required",
                "isError": True
            }
        
        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            return {
                "error": "Invalid YouTube URL or video ID",
                "isError": True
            }
        
        # Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            return {
                "error": "Failed to download transcript",
                "isError": True
            }
        
        # Generate summary
        summary = generate_summary(transcript, model)
        if not summary:
            return {
                "error": "Failed to generate summary",
                "isError": True
            }
        
        result = {
            "video_id": video_id,
            "video_url": url,
            "transcript": transcript,
            "summary": summary,
            "model_used": model
        }
        
        # Save to file if requested
        if save_to_file:
            success = save_to_markdown(transcript, summary, output_file, url, model)
            result["saved_to_file"] = success
            if success:
                result["output_file"] = output_file
        
        return {
            "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
        }


def main():
    """Main MCP server loop.""" 
    wrapper = MCPWrapper()
    
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            
            if request.get("method") == "tools/list":
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "tools": wrapper.list_tools()
                    }
                }
            
            elif request.get("method") == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                result = wrapper.call_tool(tool_name, arguments)
                
                response = {
                    "jsonrpc": "2.0", 
                    "id": request.get("id"),
                    "result": result
                }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    }
                }
            
            print(json.dumps(response))
            sys.stdout.flush()
            
        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()
        
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
            print(json.dumps(error_response))
            sys.stdout.flush()


if __name__ == "__main__":
    main()