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
- Generate JSON feeds/APIs
- Process data from external sources

Usage:
    python src/build.py           # Build with default settings
    python src/build.py --clean   # Clean build (remove dist first)
    python src/build.py --verbose # Verbose output

Environment Variables:
    BUILD_ENV: Set to 'development' or 'production' (default: production)
    CONTENT_DIR: Source content directory (default: content)
    DIST_DIR: Output directory (default: dist)
"""

import argparse
import json
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Configuration
class BuildConfig:
    """Build configuration management."""
    
    def __init__(self, args: argparse.Namespace):
        self.verbose = args.verbose
        self.clean = args.clean
        self.env = os.getenv('BUILD_ENV', 'production')
        self.content_dir = Path(os.getenv('CONTENT_DIR', 'content'))
        self.dist_dir = Path(os.getenv('DIST_DIR', 'dist'))
        self.is_development = self.env == 'development'
        
        # Setup logging
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)


def setup_directories(config: BuildConfig) -> None:
    """Setup build directories."""
    config.logger.info(f"Setting up directories: {config.content_dir} -> {config.dist_dir}")
    
    if not config.content_dir.exists():
        config.logger.error(f"Content directory '{config.content_dir}' not found!")
        sys.exit(1)
    
    if config.clean and config.dist_dir.exists():
        config.logger.info(f"Cleaning dist directory: {config.dist_dir}")
        shutil.rmtree(config.dist_dir)
    
    config.dist_dir.mkdir(parents=True, exist_ok=True)


def copy_static_files(config: BuildConfig) -> None:
    """Copy static files from content to dist directory."""
    config.logger.info(f"Copying content from {config.content_dir} to {config.dist_dir}")
    
    files_copied = 0
    dirs_copied = 0
    
    for item in config.content_dir.iterdir():
        if item.is_file():
            shutil.copy2(item, config.dist_dir / item.name)
            files_copied += 1
            config.logger.debug(f"  ✓ Copied file: {item.name}")
        elif item.is_dir():
            shutil.copytree(item, config.dist_dir / item.name, dirs_exist_ok=True)
            dirs_copied += 1
            config.logger.debug(f"  ✓ Copied directory: {item.name}")
    
    config.logger.info(f"Copied {files_copied} files and {dirs_copied} directories")


def generate_build_info(config: BuildConfig) -> None:
    """Generate build information file."""
    build_info = {
        'build_time': datetime.now().isoformat(),
        'build_env': config.env,
        'git_commit': get_git_commit(),
        'version': get_version(),
    }
    
    build_info_path = config.dist_dir / 'build-info.json'
    with open(build_info_path, 'w') as f:
        json.dump(build_info, f, indent=2)
    
    config.logger.info(f"Generated build info: {build_info_path}")


def get_git_commit() -> Optional[str]:
    """Get current git commit hash."""
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'rev-parse', '--short', 'HEAD'],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_version() -> str:
    """Get application version."""
    # Check for version file or environment variable
    version_file = Path('VERSION')
    if version_file.exists():
        return version_file.read_text().strip()
    return os.getenv('VERSION', '1.0.0')


def process_markdown_files(config: BuildConfig) -> None:
    """Process Markdown files to HTML (example implementation).
    
    To enable this, install markdown: pip install markdown
    """
    try:
        import markdown
    except ImportError:
        config.logger.warning("Markdown not available - skipping Markdown processing")
        return
    
    md = markdown.Markdown(extensions=['meta', 'toc', 'codehilite'])
    
    for md_file in config.content_dir.rglob('*.md'):
        config.logger.debug(f"Processing Markdown file: {md_file}")
        
        with open(md_file, 'r') as f:
            html = md.convert(f.read())
        
        # Create output path
        relative_path = md_file.relative_to(config.content_dir)
        output_path = config.dist_dir / relative_path.with_suffix('.html')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write HTML with basic template
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{md.Meta.get('title', [''])[0]}</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
    {html}
</body>
</html>
        """.strip()
        
        with open(output_path, 'w') as f:
            f.write(html_content)
        
        config.logger.debug(f"  ✓ Generated: {output_path}")


def optimize_images(config: BuildConfig) -> None:
    """Optimize images (example implementation).
    
    To enable this, install Pillow: pip install Pillow
    """
    if config.is_development:
        config.logger.info("Skipping image optimization in development mode")
        return
    
    try:
        from PIL import Image
    except ImportError:
        config.logger.warning("Pillow not available - skipping image optimization")
        return
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.webp'}
    
    for img_file in config.dist_dir.rglob('*'):
        if img_file.suffix.lower() in image_extensions:
            config.logger.debug(f"Optimizing image: {img_file}")
            
            try:
                with Image.open(img_file) as img:
                    # Optimize and save
                    img.save(img_file, optimize=True, quality=85)
                config.logger.debug(f"  ✓ Optimized: {img_file.name}")
            except Exception as e:
                config.logger.warning(f"Failed to optimize {img_file}: {e}")


def generate_sitemap(config: BuildConfig) -> None:
    """Generate XML sitemap."""
    html_files = list(config.dist_dir.rglob('*.html'))
    
    sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for html_file in html_files:
        relative_path = html_file.relative_to(config.dist_dir)
        url_path = str(relative_path).replace('\\', '/')
        if url_path == 'index.html':
            url_path = ''
        
        sitemap_content.append('  <url>')
        sitemap_content.append(f'    <loc>/{url_path}</loc>')
        sitemap_content.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
        sitemap_content.append('  </url>')
    
    sitemap_content.append('</urlset>')
    
    sitemap_path = config.dist_dir / 'sitemap.xml'
    with open(sitemap_path, 'w') as f:
        f.write('\n'.join(sitemap_content))
    
    config.logger.info(f"Generated sitemap with {len(html_files)} URLs: {sitemap_path}")


def build(config: BuildConfig) -> None:
    """Main build function."""
    config.logger.info(f"🔨 Starting build (env: {config.env})")
    start_time = datetime.now()
    
    try:
        # Setup
        setup_directories(config)
        
        # Core build steps
        copy_static_files(config)
        
        # Optional build steps (uncomment to enable)
        # process_markdown_files(config)
        # optimize_images(config)
        generate_sitemap(config)
        generate_build_info(config)
        
        # Calculate build time
        build_time = datetime.now() - start_time
        config.logger.info(f"✅ Build completed successfully in {build_time.total_seconds():.2f}s")
        
    except Exception as e:
        config.logger.error(f"❌ Build failed: {e}")
        if config.verbose:
            import traceback
            config.logger.error(traceback.format_exc())
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Build static site')
    parser.add_argument('--clean', action='store_true', help='Clean build (remove dist first)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config = BuildConfig(args)
    build(config)
