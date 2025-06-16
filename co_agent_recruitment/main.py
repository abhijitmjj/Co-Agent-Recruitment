"""Main entry point for the Co-Agent Recruitment system.

This module provides the main CLI interface for the resume parsing functionality.
"""

import asyncio
import sys
from .agent import parse_resume, sanitize_input


async def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) != 2:
        print("Usage: python -m co_agent_recruitment <resume_text_file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            resume_text = f.read()
        
        result = await parse_resume(resume_text)
        print(result)
    except Exception as e:
        print(f"Error processing resume: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())