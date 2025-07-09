# YouTube Summary

A Python command-line tool that downloads YouTube video transcripts and generates AI-powered summaries using LiteLLM.

## Features

- Download transcripts from YouTube videos
- Generate AI summaries using various LLM models (Claude, GPT, etc.)
- Save results to markdown files
- Interactive and command-line modes
- Configurable output files and models

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management. Make sure you have uv installed first.

### Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Setup the project
```bash
# Clone or navigate to the project directory
cd youtubesummary

# Install dependencies and create virtual environment
uv sync

# Install the package in development mode
uv pip install -e .
```

## Usage

### Option 1: Using the installed command (recommended)
```bash
# Basic usage
uv run youtube-summary https://www.youtube.com/watch?v=VIDEO_ID

# Interactive mode (prompts for URL)
uv run youtube-summary

# Custom output file and model
uv run youtube-summary -o my_summary.md -m gpt-4 https://youtu.be/VIDEO_ID

# Help
uv run youtube-summary --help
```

### Option 2: Running the module directly
```bash
# Run directly with uv
uv run python -m youtubesummary.youtube_summary https://www.youtube.com/watch?v=VIDEO_ID

# Or activate the virtual environment first
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m youtubesummary.youtube_summary https://www.youtube.com/watch?v=VIDEO_ID
```

## Command Line Options

```
usage: youtube-summary [-h] [-o OUTPUT] [-m MODEL] [url]

Download YouTube video transcripts and generate AI summaries

positional arguments:
  url                   YouTube video URL or video ID

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output markdown file (default: transcript.md)
  -m MODEL, --model MODEL
                        LLM model to use for summary (default: claude-3-5-sonnet-20241022)
```

## Examples

```bash
# Download and summarize a video
uv run youtube-summary https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Use a different model
uv run youtube-summary -m gpt-4 https://youtu.be/dQw4w9WgXcQ

# Save to a custom file
uv run youtube-summary -o my_video_summary.md https://www.youtube.com/watch?v=dQw4w9WgXcQ

# Interactive mode
uv run youtube-summary
```

## Configuration

The tool uses LiteLLM, which supports many model providers. You may need to set up API keys as environment variables:

```bash
# For Claude (Anthropic)
export ANTHROPIC_API_KEY=your_api_key

# For OpenAI
export OPENAI_API_KEY=your_api_key

# For other providers, check LiteLLM documentation
```

## Output Format

The tool creates a markdown file with:
1. Video URL
2. AI-generated summary at the top
3. Full transcript below

## Development

```bash
# Install development dependencies
uv sync

# Run tests (if any)
uv run python -m pytest

# Format code
uv run python -m black .

# Type checking
uv run python -m mypy .
```