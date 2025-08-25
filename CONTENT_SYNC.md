# Content Synchronization Strategy

This document outlines the recommended approaches for updating content in your static site deployment without requiring container rebuilds.

> ⚠️ **IMPORTANT**: Content sync is designed for **development environments only**. For production deployments, always use the full rebuild approach to ensure consistency, auditability, and security.

## Overview

The template provides two main approaches for content updates:

1. 📝 **Content Sync** - Direct synchronization to running pods (**development only**)
2. 🚀 **Full Rebuild** - Container rebuild and redeployment (**production recommended**)

## 🚨 Production vs Development Guidelines

| Aspect | Content Sync (Dev) | Full Rebuild (Prod) |
|--------|-------------------|--------------------|
| **Use Case** | Rapid iteration, testing | Production deployments |
| **Persistence** | Changes lost on pod restart | Permanent in image |
| **Version Control** | Manual commit required | Automatic with CI/CD |
| **Rollback** | Manual/complex | Standard K8s rollback |
| **Security** | Lower (direct pod access) | Higher (image-based) |
| **Auditability** | Limited | Full Git history |
| **Multi-env** | Manual sync required | Consistent across envs |

## Method 1: Content Sync (Recommended for Development)

### How It Works

The deployment uses a Persistent Volume Claim (PVC) to store site content separately from the container. This allows content updates without rebuilding or restarting containers.

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Content │───▶│   kubectl cp    │───▶│   Pod PVC /srv  │
│   content/      │    │   command       │    │   ↓             │
└─────────────────┘    └─────────────────┘    │   Caddy server  │
                                              └─────────────────┘
```

### Usage

1. **Edit content locally**:
   ```bash
   # Edit your files
   vim content/index.html
   vim content/assets/style.css
   ```

2. **Sync to all running pods**:
   ```bash
   make sync-content
   ```

3. **View changes immediately** - No restart required!

### Technical Details

- Uses `kubectl cp` to copy files from local `content/` directory to `/srv/` in pods
- Syncs to all pods with label `app={{.ProjectName}}`
- Targets the `caddy` container specifically
- Content is persisted in the PVC across pod restarts

### 🚨 Critical Limitations

> ⚠️ **WARNING: DO NOT USE IN PRODUCTION**
>
> Content sync has significant limitations that make it unsuitable for production environments:

- **📊 No Persistence**: Changes are lost when pods restart or scale
- **🔄 No Version Control**: Changes exist only in running pods unless manually committed
- **🔐 Security Risk**: Requires direct pod access with `kubectl cp` permissions
- **📝 No Audit Trail**: No record of what changed, when, or by whom
- **⚙️ Inconsistent State**: Different pods may have different content versions
- **🚑 No Rollback**: Cannot easily revert problematic changes
- **🌐 Environment Drift**: Production and staging environments become inconsistent

**For production, always use the full rebuild method described below.**

## Method 2: Full Rebuild (Recommended for Production)

### How It Works

Content changes are built into a new container image and deployed through the normal Kubernetes deployment process.

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Content │───▶│   Docker build  │───▶│  New container  │
│   content/      │    │   + image push  │    │  ↓             │
└─────────────────┘    └─────────────────┘    │  Kubernetes     │
                                              │  rollout        │
                                              └─────────────────┘
```

### Usage

1. **Edit content locally**:
   ```bash
   vim content/index.html
   ```

2. **Build and deploy**:
   ```bash
   make deploy  # Builds image and applies manifests
   ```

3. **Or separate steps**:
   ```bash
   make build   # Build new container image
   make push    # Push to registry (if using remote registry)
   make apply   # Apply manifests (triggers rollout)
   ```

### Benefits

- Version controlled and auditable
- Suitable for production environments
- Consistent across environments
- Leverages Kubernetes rollout capabilities
- Immutable deployments

## Advanced Synchronization Options

### Option 1: Init Container Strategy (Current Implementation)

The deployment includes an init container that copies content from the built image to the PVC on first run:

```yaml
initContainers:
- name: content-init
  image: {{.ProjectName}}:{{.ImageTag}}
  command: ["/bin/sh", "-c"]
  args:
  - |
    if [ ! -f /srv/index.html ]; then
      echo "Copying initial content..."
      cp -r /app/dist/* /srv/
    else
      echo "Content already exists, skipping initialization"
    fi
```

### Option 2: Git Sync Sidecar (Advanced)

For more sophisticated content management, consider adding a git-sync sidecar:

```yaml
# Add to deployment spec
containers:
- name: git-sync
  image: registry.k8s.io/git-sync/git-sync:v3.6.5
  args:
  - --repo={{.GitRepo}}
  - --branch={{.GitBranch}}
  - --wait=60
  - --root=/srv
  env:
  - name: GIT_SYNC_USERNAME
    valueFrom:
      secretKeyRef:
        name: git-credentials
        key: username
  - name: GIT_SYNC_PASSWORD
    valueFrom:
      secretKeyRef:
        name: git-credentials
        key: password
  volumeMounts:
  - name: content-storage
    mountPath: /srv
```

### Option 3: ConfigMap for Small Sites (Alternative)

For very small static sites, you could use ConfigMaps instead of PVCs:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: site-content
data:
  index.html: |
    <!DOCTYPE html>
    <html>...
```

## Content Backup and Recovery

### Backup Content from Running Pods

```bash
# Backup content to local directory
make backup-content

# Manual backup
kubectl cp namespace/pod-name:/srv ./backup/
```

### Restore Content

```bash
# Restore from backup
kubectl cp ./backup/ namespace/pod-name:/srv -c caddy
```

## Monitoring and Troubleshooting

### Check Content Sync Status

```bash
# View pod content
kubectl exec -n {{.Namespace}} deployment/{{.ProjectName}} -c caddy -- ls -la /srv

# Check PVC usage
kubectl describe pvc {{.ProjectName}}-content -n {{.Namespace}}

# View sync logs
kubectl logs -n {{.Namespace}} -l app={{.ProjectName}} -c caddy --tail=100
```

### Common Issues

1. **Permission Denied**
   ```bash
   # Fix: Ensure proper PVC permissions
   kubectl exec -n {{.Namespace}} deployment/{{.ProjectName}} -c caddy -- chown -R caddy:caddy /srv
   ```

2. **PVC Not Mounting**
   ```bash
   # Check PVC status
   kubectl get pvc -n {{.Namespace}}
   kubectl describe pvc {{.ProjectName}}-content -n {{.Namespace}}
   ```

3. **Content Not Updating**
   ```bash
   # Force pod restart to pick up changes
   kubectl rollout restart deployment/{{.ProjectName}} -n {{.Namespace}}
   ```

## Security Considerations

### Content Sync Security

- Content sync requires `kubectl` exec and cp permissions
- Limit access to content directories
- Validate content before syncing
- Consider using separate namespaces for different environments

### Production Recommendations

1. Use full rebuild method for production
2. Implement proper CI/CD pipelines
3. Use image signing and validation
4. Regular security scanning of content and containers
5. Backup strategies for content and configuration

## Performance Optimization

### PVC Performance

- Use SSD-backed storage classes for better performance
- Consider ReadWriteMany PVCs for multi-pod scaling
- Monitor PVC utilization and resize as needed

### Content Delivery

- Enable gzip compression in Caddy (already configured)
- Use CDN for static assets in production
- Implement proper caching headers
- Consider serving assets from object storage for large sites

---

This strategy provides both rapid development iteration and production-ready deployment options while maintaining security and reliability.
