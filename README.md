# Displace Static Site Template

A production-ready static site deployment template for Kubernetes, designed for use with the [Displace CLI](https://displace.tech).

## Overview

This template provides everything you need to deploy modern static sites to Kubernetes with enterprise-grade features:

- 🐳 **Multi-stage Docker Build** - Python with uv for building, Caddy for serving
- ☸️ **Kubernetes Manifests** - Production-ready deployment without Helm complexity  
- ⚡ **Content Synchronization** - Update content without rebuilding containers
- 🔒 **Automatic HTTPS** - SSL certificates via cert-manager and Let's Encrypt
- 🛠️ **Cross-platform Tooling** - Makefile that works on Linux, macOS, and Windows
- 📊 **Built-in Monitoring** - Health checks, resource limits, and observability
- 🔐 **Security First** - Non-root containers, security contexts, and best practices

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

## Quick Start

### 1. Initialize Your Project

```bash
# Initialize a new static site project
displace project init static

# You'll be prompted for:
# - Project name (e.g., "my-blog")
# - Kubernetes namespace (defaults to project name)
# - Domain name (e.g., "blog.example.com")
```

### 2. Customize Your Content

```bash
cd my-blog

# Edit the homepage
vim content/index.html

# Modify styles
vim content/assets/style.css

# Add more pages, images, etc.
```

### 3. Deploy to Kubernetes

```bash
# Deploy everything with one command
make deploy

# Check status
make status

# View logs
make logs
```

### 4. Rapid Content Updates (Development)

```bash
# Edit content locally
vim content/index.html

# Sync to running pods instantly (no rebuild/restart)
make sync-content
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
# Deploy with Displace (handles build and deployment)
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
mkdir my-blog && cd my-blog
displace project init static
# Enter: my-blog, my-blog, blog.example.com
make deploy  # Uses displace project deploy
```

### With Custom Build Process
```bash
# Edit src/build.py to add custom logic
# Update pyproject.toml with dependencies
make deploy  # Displace handles build and deployment
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

## Available Commands

The generated Makefile includes comprehensive commands for development and operations:

### Development
- `make dev` - Start local development server
- `make build` - Build Docker image locally
- `make sync-content` - Sync content to running pods without rebuild

### Deployment
- `make deploy` - Deploy using Displace CLI (recommended)
- `make apply` - Apply Kubernetes manifests directly
- `make destroy` - Remove deployment from cluster

### Monitoring
- `make status` - Check deployment status
- `make logs` - View application logs
- `make events` - View recent cluster events

### Access
- `make shell` - Access running pod shell
- `make port-forward` - Forward local port to service
- `make open` - Open site in browser

### Utilities
- `make validate` - Validate Kubernetes manifests
- `make backup-content` - Backup content from pod
- `make info` - Display project information

## Troubleshooting

### Common Issues

#### 1. Pods Not Starting

```bash
# Check pod status
make status

# View detailed pod information
kubectl describe pods -n [namespace] -l app=[project-name]

# Check events
make events
```

**Common causes:**
- Image pull failures
- Resource constraints
- PVC mounting issues

#### 2. Content Sync Failing

```bash
# Verify pods are running
make status

# Check if PVC is mounted
kubectl exec -n [namespace] deployment/[project-name] -c caddy -- ls -la /srv

# Manual sync to single pod
POD=$(kubectl get pod -n [namespace] -l app=[project-name] -o jsonpath='{.items[0].metadata.name}')
kubectl cp content/. [namespace]/$POD:/srv/ -c caddy
```

#### 3. HTTPS Certificate Issues

```bash
# Check certificate status
kubectl get certificates -n [namespace]

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Check ingress configuration
kubectl describe ingress -n [namespace] [project-name]
```

#### 4. Site Not Accessible

```bash
# Check service endpoints
kubectl get endpoints -n [namespace] [project-name]

# Test internal connectivity
make port-forward
# Then visit http://localhost:8080

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

#### 5. Build Failures

```bash
# Test build locally
docker build -t test-build .

# Check build logs
docker build --no-cache -t test-build .

# Validate Python dependencies
uv pip check
```

### Performance Optimization

#### Resource Tuning

Edit `manifests/04-deployment.yaml` to adjust resources:

```yaml
resources:
  requests:
    memory: "128Mi"  # Increase for larger sites
    cpu: "100m"
  limits:
    memory: "256Mi"
    cpu: "200m"
```

#### Storage Performance

For better performance, use SSD storage classes:

```yaml
# In manifests/02-content-pvc.yaml
storageClassName: "ssd"  # or "gp2" on AWS
```

#### Scaling

Increase replicas for higher availability:

```yaml
# In manifests/04-deployment.yaml  
replicas: 3  # Default is 2
```

### Development Tips

#### Custom Build Process

Modify `src/build.py` to add custom build logic:

```python
# Example: Process Markdown files
import markdown

def build_markdown():
    # Convert .md files to .html
    pass
```

#### Content Structure

Organize content for better maintainability:

```
content/
├── index.html
├── about/
│   └── index.html
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
└── api/
    └── data.json
```

#### Environment-Specific Configuration

Use `.credentials` file for environment variables:

```bash
# .credentials (auto-ignored by git)
REGISTRY_URL=registry.example.com
CUSTOM_DOMAIN=staging.example.com
```


## License

Copyright © 2025 Displace Technologies

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

## About Displace Technologies

[Displace Technologies](https://displace.tech) - Making Kubernetes deployment simple and reliable.