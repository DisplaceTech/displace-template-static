#!/usr/bin/env python3
"""
Static Site Build Script

This script demonstrates how to build static sites using Python.
You can customize this to use any static site generator or build process.

Examples:
- Process Markdown files with Python-Markdown
- Generate pages from templates with Jinja2
- Process YAML data files
- Optimize images
- Compile SCSS/LESS
"""

import shutil
import sys
from pathlib import Path


def build():
    """
    Build the static site.
    
    This example just copies content from the content/ directory to dist/,
    but you can customize this to do any build processing you need.
    """
    print("🔨 Building static site...")
    
    content_dir = Path("content")
    dist_dir = Path("dist")
    
    # Ensure directories exist
    if not content_dir.exists():
        print(f"❌ Content directory '{content_dir}' not found!")
        sys.exit(1)
    
    # Clean dist directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    dist_dir.mkdir(parents=True)
    
    # Copy all content to dist
    try:
        print(f"📁 Copying content from {content_dir} to {dist_dir}")
        
        # Copy all files and directories
        for item in content_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, dist_dir / item.name)
                print(f"  ✓ Copied file: {item.name}")
            elif item.is_dir():
                shutil.copytree(item, dist_dir / item.name)
                print(f"  ✓ Copied directory: {item.name}")
        
        print("✅ Build completed successfully!")
        
    except Exception as e:
        print(f"❌ Build failed: {e}")
        sys.exit(1)


def advanced_build_example():
    """
    Example of a more advanced build process.
    
    Uncomment and modify this function to implement custom build logic:
    - Markdown processing
    - Template rendering
    - Asset optimization
    - etc.
    """
    # Example with Jinja2 templates (uncomment if using)
    # from jinja2 import Environment, FileSystemLoader
    # 
    # env = Environment(loader=FileSystemLoader('templates'))
    # template = env.get_template('index.html.j2')
    # 
    # output = template.render(
    #     title="My Site",
    #     content="Generated content"
    # )
    # 
    # with open('dist/index.html', 'w') as f:
    #     f.write(output)
    
    pass


if __name__ == "__main__":
    build()
