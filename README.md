# Displace Static Site Template

A production-ready static site deployment template for Kubernetes, designed for use with the [Displace CLI](https://displace.tech).

## Overview

This template provides a complete static site deployment including:

- **Multi-stage Docker Build** - Python with uv for building, Caddy for serving
- **Kubernetes Manifests** - Production-ready deployment without Helm complexity  
- **Content Synchronization** - Update content without rebuilding containers
- **Automatic HTTPS** - SSL certificates via cert-manager and Let's Encrypt
- **Cross-platform Tooling** - Makefile that works on Linux and macOS

## Features

### 🚀 **Rapid Development**
- Content sync to running pods without container rebuilds
- `make sync-content` for instant updates during development
- Local development server with `make dev`

### 🐳 **Modern Build Process**
- Multi-stage Docker builds with Python/uv and Caddy
- Optional Python build scripts for static site generation
- Support for any build tool or static site generator

### ☸️ **Kubernetes-Native**
- Simple manifests without Helm complexity
- Persistent Volume Claims for content storage
- Resource limits, health checks, and security best practices
- Automatic HTTPS with cert-manager integration

### 🔒 **Security First**
- Non-root containers and security headers
- Credential isolation with git-ignored files  
- Automatic SSL certificate management
- Production-ready security configurations

### 🛠️ **Developer Experience**
- Comprehensive Makefile with cross-platform support
- Color-coded terminal output and help system
- Standardized around `displace` commands with `kubectl` fallbacks
- Detailed documentation and troubleshooting guides

## Template Structure

```
templates/
├── .gitignore.tmpl              # Git ignore file template
├── .credentials.tmpl            # Credential file template (git-ignored)
├── Dockerfile.tmpl              # Multi-stage build definition
├── Makefile.tmpl                # Cross-platform commands
├── pyproject.toml.tmpl          # Python project configuration
├── README.md.tmpl               # Project documentation template
└── manifests/                   # Kubernetes manifests
    ├── 01-namespace.yaml.tmpl   # Namespace definition
    ├── 02-content-pvc.yaml.tmpl # Persistent Volume Claim
    ├── 03-caddy-config.yaml.tmpl # Caddy web server config
    ├── 04-deployment.yaml.tmpl   # Multi-container deployment
    ├── 05-service.yaml.tmpl      # Service definition
    └── 06-ingress.yaml.tmpl      # Ingress with SSL
content/                         # Example static site content
├── index.html                   # Modern, responsive landing page
└── assets/
    ├── style.css               # Professional CSS styling
    └── favicon.svg             # Simple SVG icon
src/                            # Python build scripts
└── build.py                    # Example build script
```

## Usage

This template is automatically downloaded and used by the Displace CLI when initializing static site projects:

```bash
displace project init static
```

The CLI will:
- Download the latest template release
- Prompt for required variables (project name, domain, etc.)
- Process templates with project-specific values  
- Create all necessary files with proper security settings

## Template Variables

The following variables are available in templates:

### Required Variables
- `{{.ProjectName}}` - The project name
- `{{.Namespace}}` - Kubernetes namespace  
- `{{.Domain}}` - Domain name for the static site

### Optional Variables  
- `{{.ImageTag}}` - Docker image tag (default: "latest")
- `{{.Replicas}}` - Number of pod replicas (default: 2)
- `{{.StorageClass}}` - Kubernetes storage class (default: "standard")
- `{{.IngressClass}}` - Ingress controller class (default: "nginx")
- `{{.CertIssuer}}` - Cert-manager cluster issuer (default: "letsencrypt-prod")
- `{{.PythonVersion}}` - Python version for builds (default: "3.13")
- `{{.RegistryURL}}` - Container registry URL
- `{{.BuildCommand}}` - Custom build command

## Content Management Strategies

### Development: Content Sync
Update content without rebuilding containers:

```bash
# Edit your content locally
vim content/index.html

# Sync to all running pods instantly
make sync-content
```

This uses `kubectl cp` to copy files directly to the Persistent Volume Claim, allowing instant updates without downtime.

### Production: Full Rebuild
For production deployments:

```bash
# Build new image with updated content
make build

# Deploy with rolling update
make deploy
```

## Architecture

### Multi-Stage Docker Build
1. **Build Stage**: Uses `ghcr.io/astral-sh/uv:debian` to install Python dependencies and run build scripts
2. **Runtime Stage**: Uses `caddy:alpine` for high-performance serving with automatic HTTPS

### Kubernetes Deployment
- **Init Container**: Copies initial content from image to PVC
- **Main Container**: Caddy server serving content from PVC
- **Persistent Storage**: PVC for content that persists across deployments
- **ConfigMap**: Caddy configuration with security headers and optimizations

### Content Synchronization
- PVC separates content from container lifecycle
- `kubectl cp` enables rapid content updates
- Init container ensures content availability on first deployment

## Security Features

### Git Safety
- Automatic `.gitignore` generation protects sensitive files
- Separate credential files (`.credentials`) automatically excluded from version control
- Kubernetes secrets use placeholder values in main templates

### Container Security
- Non-root containers with explicit user creation
- Resource limits and security contexts
- Read-only root filesystems where possible
- Health checks and liveness probes

### Network Security
- Automatic HTTPS with cert-manager integration
- Security headers (HSTS, XSS protection, etc.)
- Ingress-level SSL termination
- Internal cluster communication only

## Requirements

- **Kubernetes**: 1.20+
- **Docker**: 20.10+
- **kubectl**: For cluster access
- **Optional**: uv, python3 for custom builds

## Examples

### Basic Static Site
```bash
displace project init static
# Enter: my-blog, my-blog, blog.example.com
cd my-blog
make deploy
```

### With Custom Build Process
```bash
# Edit src/build.py to add custom logic
# Update pyproject.toml with dependencies
make build  # Builds with custom Python script
make deploy
```

### Development Workflow
```bash
# Edit content locally
vim content/index.html
vim content/assets/style.css

# Sync changes instantly (no rebuild)
make sync-content

# View logs
make logs

# Access running pod
make shell
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with a local Displace CLI installation
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [Displace CLI Docs](https://displace.tech/docs)
- **Issues**: [GitHub Issues](https://github.com/DisplaceTech/displace-template-static/issues)
- **Community**: [Discord](https://discord.gg/displace)

---

**Generated with Displace CLI** - Visit [displace.tech](https://displace.tech) for more templates and tools.
