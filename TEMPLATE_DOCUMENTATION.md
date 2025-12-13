# Displace Template Documentation

**For Wiki PM** - Complete documentation of all template Makefile targets and variables.

---

## Template Overview

| Template | Type | Description | Database |
|----------|------|-------------|----------|
| static | Static Site | Caddy web server with content sync | None |
| wordpress | CMS | WordPress + MariaDB | MariaDB |
| laravel | PHP Framework | PHP-FPM + Nginx + MySQL | MySQL |

---

## Makefile Targets Reference

### Common Targets (All Templates)

| Target | Description | Uses Displace |
|--------|-------------|---------------|
| `help` | Display available commands | No |
| `deploy` | Deploy to Kubernetes | Yes |
| `destroy` | Remove deployment | Yes |
| `status` | Check deployment status | Yes |
| `logs` | View application logs | No (needs displace) |
| `events` | View Kubernetes events | No (needs displace) |
| `shell` | Access pod shell | No (needs displace) |
| `port-forward` | Forward local port to service | No (needs displace) |
| `open` | Open in browser | No (local command) |
| `validate` | Validate K8s manifests | No (needs displace) |
| `info` | Display project information | No |

### Static Template Specific

| Target | Description |
|--------|-------------|
| `build` | Build Docker image locally |
| `dev` | Start local development server |
| `sync-content` | Sync local content to running pods |
| `backup-content` | Backup content from pods |
| `lint` | Lint Python code |
| `format` | Format Python code |
| `test` | Run tests |

### WordPress Template Specific

| Target | Description |
|--------|-------------|
| `logs-db` | View MariaDB logs |
| `shell-db` | Access MariaDB pod shell |
| `mysql` | Connect to MySQL CLI |
| `backup-db` | Backup database to local file |
| `restore-db` | Restore database from backup |
| `backup-content` | Backup wp-content directory |
| `scale` | Scale WordPress replicas |

### Laravel Template Specific

| Target | Description |
|--------|-------------|
| `build` | Build Docker image locally |
| `dev` | Start local dev with docker-compose |
| `dev-down` | Stop local development |
| `dev-logs` | View local dev logs |
| `logs-db` | View MySQL logs |
| `shell-db` | Access MySQL pod shell |
| `mysql` | Connect to MySQL CLI |
| `artisan` | Run artisan command (CMD=) |
| `migrate` | Run database migrations |
| `migrate-fresh` | Fresh migration with seeds |
| `tinker` | Open Laravel Tinker REPL |
| `cache-clear` | Clear all Laravel caches |
| `optimize` | Optimize for production |
| `backup-db` | Backup database |
| `restore-db` | Restore database |
| `scale` | Scale Laravel replicas |

---

## Template Variables Reference

### Static Template Variables

#### Required Variables

| Variable | Type | Description | Pattern | Example |
|----------|------|-------------|---------|---------|
| `ProjectName` | string | Project identifier | `^[a-z][a-z0-9-]*[a-z0-9]$` | `my-static-site` |
| `Namespace` | string | Kubernetes namespace | `^[a-z][a-z0-9-]*[a-z0-9]$` | `my-static-site` |
| `Domain` | string | Site domain name | `^[a-zA-Z0-9][a-zA-Z0-9.-]*[a-zA-Z0-9]$` | `example.com` |

#### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ImageTag` | string | `latest` | Docker image tag |
| `Replicas` | integer | `2` | Number of pod replicas (1-10) |
| `StorageClass` | string | `standard` | Kubernetes storage class |
| `StorageSize` | string | `1Gi` | Content PVC size |
| `IngressClass` | string | `nginx` | Ingress controller class |
| `CertIssuer` | string | `letsencrypt-prod` | Cert-manager issuer |
| `PythonVersion` | string | `3.13` | Python version for builds |
| `RegistryURL` | string | `""` | Container registry URL |
| `BuildCommand` | string | `""` | Custom build command |
| `MemoryLimit` | string | `128Mi` | Container memory limit |
| `CPULimit` | string | `100m` | Container CPU limit |

---

### WordPress Template Variables

#### Required Variables

| Variable | Type | Description | Sensitive |
|----------|------|-------------|-----------|
| `ProjectName` | string | Project identifier | No |
| `Namespace` | string | Kubernetes namespace | No |
| `DBRootPassword` | string | MariaDB root password | Yes |
| `DBPassword` | string | WordPress DB password | Yes |
| `WordPressPassword` | string | WordPress admin password | Yes |
| `DBRootPasswordB64` | string | Base64 encoded root password | Yes (computed) |
| `DBPasswordB64` | string | Base64 encoded DB password | Yes (computed) |

#### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ProjectDisplayName` | string | `{{.ProjectName}}` | Human-readable name |
| `WordPressReplicas` | integer | `1` | WordPress replicas (1-10) |
| `WordPressStorageSize` | string | `10Gi` | WordPress PVC size |
| `MariaDBStorageSize` | string | `8Gi` | MariaDB PVC size |
| `IngressClass` | string | `nginx` | Ingress controller |
| `CertIssuer` | string | `letsencrypt-prod` | Cert-manager issuer |

---

### Laravel Template Variables

#### Required Variables

| Variable | Type | Description | Sensitive |
|----------|------|-------------|-----------|
| `ProjectName` | string | Project identifier | No |
| `Namespace` | string | Kubernetes namespace | No |
| `Domain` | string | Application domain | No |
| `AppKey` | string | Laravel APP_KEY | Yes (computed) |
| `DBPassword` | string | MySQL password | Yes |
| `DBPasswordB64` | string | Base64 encoded password | Yes (computed) |

#### Optional Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ProjectDisplayName` | string | `{{.ProjectName}}` | Human-readable name |
| `PHPVersion` | string | `8.3` | PHP version (8.x) |
| `LaravelReplicas` | integer | `2` | Laravel replicas (1-10) |
| `AppStorageSize` | string | `5Gi` | Storage PVC size |
| `DBStorageSize` | string | `10Gi` | MySQL PVC size |
| `IngressClass` | string | `nginx` | Ingress controller |
| `CertIssuer` | string | `letsencrypt-prod` | Cert-manager issuer |
| `MemoryLimit` | string | `512Mi` | Container memory limit |
| `CPULimit` | string | `500m` | Container CPU limit |

---

## Generated Project Structure

### Static Template Output

```
project-name/
├── .credentials          # Project credentials (0600)
├── .gitignore
├── Dockerfile            # Multi-stage build
├── Makefile              # Project commands
├── pyproject.toml        # Python dependencies
├── README.md
├── content/              # Static site content
│   └── index.html
├── src/                  # Build scripts (optional)
│   └── build.py
└── manifests/
    ├── 01-namespace.yaml
    ├── 02-content-pvc.yaml
    ├── 03-caddy-config.yaml
    ├── 04-deployment.yaml
    ├── 05-service.yaml
    └── 06-ingress.yaml
```

### WordPress Template Output

```
project-name/
├── .credentials          # All passwords (0600)
├── .gitignore
├── Makefile              # Project commands
├── README.md
├── backups/              # Database backups
└── manifests/
    ├── 01-namespace.yaml
    ├── 02-database-secret.yaml
    ├── 03-mariadb.yaml
    ├── 04-wordpress.yaml
    ├── 05-ingress.yaml
    └── secrets/
        └── database-secret-override.yaml
```

### Laravel Template Output

```
project-name/
├── .credentials          # APP_KEY and passwords (0600)
├── .gitignore
├── Dockerfile            # Multi-stage PHP build
├── Makefile              # Project commands
├── docker-compose.yaml   # Local development
├── README.md
├── docker/
│   ├── nginx.conf
│   ├── php.ini
│   └── supervisord.conf
├── src/                  # Laravel application (user copies here)
├── backups/              # Database backups
└── manifests/
    ├── 01-namespace.yaml
    ├── 02-database-secret.yaml
    ├── 03-mysql.yaml
    ├── 04-laravel.yaml
    ├── 05-service.yaml
    └── 06-ingress.yaml
```

---

## Kubernetes Labels Standard

All templates use standard Kubernetes labels:

```yaml
labels:
  app.kubernetes.io/name: <project-name>
  app.kubernetes.io/instance: <project-name>
  app.kubernetes.io/component: app|database|storage|config
  app.kubernetes.io/managed-by: displace
```

---

## Template Features Comparison

| Feature | Static | WordPress | Laravel |
|---------|--------|-----------|---------|
| Docker build | ✅ | ❌ (uses Bitnami) | ✅ |
| Local dev server | ✅ | ❌ | ✅ (docker-compose) |
| Content sync | ✅ | ✅ | ❌ |
| Database | ❌ | MariaDB | MySQL |
| Database backup | ❌ | ✅ | ✅ |
| Shell access | ✅ | ✅ | ✅ |
| Scaling | ❌ | ✅ | ✅ |
| Artisan CLI | ❌ | ❌ | ✅ |
| TLS/HTTPS | ✅ | ✅ | ✅ |
| Health checks | ✅ | ✅ | ✅ |

---

## Common Workflows

### Deploy New Project

```bash
# Initialize from template
displace project init <template> --name my-project

# Build (if applicable)
make build

# Deploy
make deploy

# Access locally
make port-forward
```

### Update Content (Static/WordPress)

```bash
# Edit content locally
vim content/index.html

# Sync to running pods
make sync-content
```

### Database Operations (WordPress/Laravel)

```bash
# Backup database
make backup-db

# Restore database
make restore-db FILE=backups/backup-file.sql
```

### Laravel Artisan

```bash
# Run migrations
make migrate

# Run any artisan command
make artisan CMD='queue:work'

# Clear caches
make cache-clear
```

---

*Documentation maintained by Template PM for Wiki PM reference*
