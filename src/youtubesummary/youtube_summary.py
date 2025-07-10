#!/usr/bin/env python3
"""
YouTube Transcript Summary Tool

Downloads YouTube video transcripts and generates AI-powered summaries.
"""

import argparse
import os
import sys
import re
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import litellm
from litellm import completion


def extract_video_id(url):
    """Extract YouTube video ID from various URL formats with enhanced validation."""
    if not url or not isinstance(url, str):
        return None

    # Sanitize input
    url = url.strip()

    # Check for valid YouTube domains
    valid_domains = ["youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com"]

    try:
        parsed_url = urlparse(url)
        if parsed_url.netloc and parsed_url.netloc not in valid_domains:
            # If it has a domain but not YouTube, reject it
            if "." in parsed_url.netloc:
                return None
    except Exception:
        pass

    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/v/([a-zA-Z0-9_-]{11})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            # Additional validation for video ID format
            if re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
                return video_id

    # If it's already just a video ID, validate it strictly
    if re.match(r"^[a-zA-Z0-9_-]{11}$", url):
        return url

    return None


def get_transcript(video_id):
    """Download transcript for a YouTube video."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item["text"] for item in transcript_list])
        return transcript_text
    except Exception:
        print(
            "Error: Unable to download transcript. Please check the video ID and try again."
        )
        return None


def generate_summary(transcript, model="claude-sonnet-4-20250514"):
    """Generate summary using LiteLLM."""
    try:
        # Truncate transcript if too long to prevent token limit issues
        max_transcript_length = 8000  # Conservative limit
        if len(transcript) > max_transcript_length:
            transcript = transcript[:max_transcript_length] + "..."

        prompt = f"""Please provide a summary of this YouTube video transcript. 
        Focus on the main points, key insights, and actionable takeaways.
        
        Transcript:
        {transcript}
        
        Please format your response as a clear, well-structured summary."""

        response = completion(
            model=model, messages=[{"role": "user", "content": prompt}], max_tokens=1000
        )

        return response.choices[0].message.content
    except Exception:
        print(
            "Error: Unable to generate summary. Please check your API configuration and try again."
        )
        return None


def sanitize_filename(filename):
    """Sanitize filename to prevent directory traversal and other attacks."""
    if not filename:
        return "transcript.md"

    # Remove any directory traversal attempts
    filename = os.path.basename(filename)

    # Remove or replace dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*", "\x00"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    # Ensure it ends with .md
    if not filename.endswith(".md"):
        filename += ".md"

    # Limit filename length
    if len(filename) > 255:
        name_part = filename[:-3][:250]  # Keep .md extension
        filename = name_part + ".md"

    return filename


def save_to_markdown(transcript, summary, output_file, video_url, model_name=None):
    """Save transcript and summary to markdown file."""
    # Sanitize the output filename
    safe_filename = sanitize_filename(output_file)

    # Ensure we're writing to current directory or subdirectory only
    safe_path = Path(safe_filename).resolve()
    current_dir = Path.cwd().resolve()

    try:
        # Check if the resolved path is within current directory
        safe_path.relative_to(current_dir)
    except ValueError:
        print("Error: Output file must be in current directory")
        return False

    content = f"""# YouTube Video Summary

**Video URL:** {video_url}

## Summary

{summary}

*Generated using: {model_name or 'AI model'}*

## Full Transcript

{transcript}
"""

    try:
        with open(safe_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Summary and transcript saved to: {safe_path}")
        return True
    except Exception:
        print("Error: Unable to save file. Please check permissions and try again.")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube video transcripts and generate AI summaries",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://www.youtube.com/watch?v=dQw4w9WgXcQ
  %(prog)s -o summary.md -m gpt-4 https://youtu.be/dQw4w9WgXcQ
  %(prog)s --model claude-3-opus-20240229 https://www.youtube.com/watch?v=dQw4w9WgXcQ
        """,
    )

    parser.add_argument("url", nargs="?", help="YouTube video URL or video ID")

    parser.add_argument(
        "-o",
        "--output",
        default="transcript.md",
        help="Output markdown file (default: transcript.md)",
    )

    parser.add_argument(
        "-m",
        "--model",
        default="claude-sonnet-4-20250514",
        help="LLM model to use for summary (default: claude-sonnet-4-20250514)",
    )

    args = parser.parse_args()

    # Get URL from command line or prompt user
    url = args.url
    if not url:
        url = input("Enter YouTube video URL: ").strip()

    if not url:
        print("Error: No YouTube URL provided")
        sys.exit(1)

    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print("Error: Invalid YouTube URL or video ID")
        sys.exit(1)

    print(f"Video ID: {video_id}")

    # Download transcript
    print("Downloading transcript...")
    transcript = get_transcript(video_id)
    if not transcript:
        print("Failed to download transcript")
        sys.exit(1)

    print("Transcript downloaded successfully")

    # Generate summary
    print(f"Generating summary using {args.model}...")
    summary = generate_summary(transcript, args.model)
    if not summary:
        print("Failed to generate summary")
        sys.exit(1)

    print("Summary generated successfully")

    # Save to markdown
    if not save_to_markdown(transcript, summary, args.output, url, args.model):
        sys.exit(1)


if __name__ == "__main__":
    main()
