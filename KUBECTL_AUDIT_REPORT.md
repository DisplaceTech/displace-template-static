# Kubectl Audit Report - Displace Templates

**Date:** December 13, 2024
**Auditor:** Template Project Manager
**Templates Audited:** static, wordpress, laravel

## Executive Summary

All three Displace templates currently use raw `kubectl` commands as fallbacks when the `displace` CLI is not available. This audit identifies all kubectl commands that should be replaced with native `displace` commands to eliminate the kubectl dependency.

**Current State:**
- Templates use `displace project deploy` and `displace project info` when available
- All other operations fall back to raw kubectl commands
- Approximately 15+ unique kubectl operations need displace equivalents

---

## Commands Already Using Displace

| Operation | Displace Command | Status |
|-----------|------------------|--------|
| Deploy manifests | `displace project deploy` | ✅ Implemented |
| Show project info | `displace project info` | ✅ Implemented |
| Destroy project | `displace project destroy` | ✅ Implemented |

---

## kubectl Commands Requiring Displace Equivalents

### PRIORITY 1: Critical Operations (Daily Use)

| kubectl Command | Current Usage | Proposed Displace Command | Notes |
|-----------------|---------------|---------------------------|-------|
| `kubectl logs -f --tail=N` | View application logs | `displace project logs` | Stream logs from pods |
| `kubectl exec -it -- /bin/sh` | Access pod shell | `displace project shell` | Interactive shell access |
| `kubectl port-forward svc/` | Local access | `displace project port-forward` | Forward service port locally |

### PRIORITY 2: Content/Data Operations

| kubectl Command | Current Usage | Proposed Displace Command | Notes |
|-----------------|---------------|---------------------------|-------|
| `kubectl cp local/. pod:/path/` | Sync content to pods | `displace project sync` | Critical for static/wordpress |
| `kubectl cp pod:/path/ local/` | Backup content | `displace content backup` | Backup from running pods |
| `kubectl exec -- mysqldump` | Database backup | `displace project backup-db` | Dump database to local file |
| `kubectl exec -i -- mysql` | Database restore | `displace project restore-db` | Restore from backup file |

### PRIORITY 3: Monitoring & Status

| kubectl Command | Current Usage | Proposed Displace Command | Notes |
|-----------------|---------------|---------------------------|-------|
| `kubectl get pods/deployments/services` | Check resources | `displace project info` (enhance) | Already exists, needs expansion |
| `kubectl get events` | View events | `displace project events` | Namespace events |
| `kubectl wait --for=condition` | Wait for ready | `displace project wait` | Or integrate into deploy |

### PRIORITY 4: Management Operations

| kubectl Command | Current Usage | Proposed Displace Command | Notes |
|-----------------|---------------|---------------------------|-------|
| `kubectl scale deployment` | Scale replicas | `displace project scale` | Change replica count |
| `kubectl apply --dry-run` | Validate manifests | `displace project validate` | Dry-run validation |
| `kubectl get pvc` | Check storage | `displace project info` (enhance) | Include in project info |

---

## Detailed Usage by Template

### Static Template (`displace-template-static`)

**File:** `templates/Makefile.tmpl`

```makefile
# Identified kubectl commands:

# Line 75: Wait for deployment
kubectl wait --for=condition=available deployment/$(PROJECT_NAME) -n $(NAMESPACE) --timeout=60s

# Line 85: Check ingress existence
kubectl get ingress -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME)

# Lines 110-117: Content sync to pods
kubectl get pods -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME) -o jsonpath='{.items[*].metadata.name}'
kubectl cp content/. $(NAMESPACE)/$$pod:/srv/ -c caddy

# Line 125: Get pod for backup
kubectl get pod -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME) -o jsonpath='{.items[0].metadata.name}'
kubectl cp $(NAMESPACE)/$$POD:/srv/ backup/...

# Lines 141-149: Status fallback
kubectl get namespace $(NAMESPACE)
kubectl get deployments -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME)
kubectl get pods -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME)
kubectl get services -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME)
kubectl get ingress -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME)

# Line 155: Logs
kubectl logs -n $(NAMESPACE) -l app.kubernetes.io/name=$(PROJECT_NAME) -f --tail=100

# Line 160: Events
kubectl get events -n $(NAMESPACE) --sort-by='.lastTimestamp'

# Lines 166-168: Shell access
kubectl get pod ... -o jsonpath='{.items[0].metadata.name}'
kubectl exec -it -n $(NAMESPACE) $$POD -c caddy -- /bin/sh

# Line 177: Port forward
kubectl port-forward -n $(NAMESPACE) service/$(PROJECT_NAME) 8080:80

# Line 190: Validate manifests
kubectl apply --dry-run=client -f "$$file"
```

### WordPress Template (`displace-template-wordpress`)

**File:** `templates/Makefile.tmpl`

Same patterns as static template, plus:

```makefile
# Database-specific operations:

# MySQL CLI access
kubectl exec -it -n $(NAMESPACE) $$POD -- mysql -u wordpress -p$$DB_PASSWORD wordpress

# Database backup
kubectl exec -n $(NAMESPACE) $$POD -- mysqldump -u wordpress -p$$DB_PASSWORD wordpress > backup.sql

# Database restore
cat backup.sql | kubectl exec -i -n $(NAMESPACE) $$POD -- mysql -u wordpress -p$$DB_PASSWORD wordpress

# WordPress content backup
kubectl cp $(NAMESPACE)/$$POD:/bitnami/wordpress/wp-content backups/...
```

### Laravel Template (`displace-template-laravel`)

**File:** `templates/Makefile.tmpl`

Same patterns as WordPress, plus:

```makefile
# Artisan commands
kubectl exec -n $(NAMESPACE) $$POD -- php artisan $(CMD)

# Tinker REPL (interactive)
kubectl exec -it -n $(NAMESPACE) $$POD -- php artisan tinker
```

---

## Recommended Implementation Order

### Phase 1: Core Operations
1. `displace project logs` - High usage, simple implementation
2. `displace project shell` - Common debugging need
3. `displace project port-forward` - Local development essential

### Phase 2: Content Management
4. `displace project sync` - Critical for static/wordpress workflows
5. `displace content backup` - Data safety

### Phase 3: Database Operations
6. `displace project backup-db` - Database safety
7. `displace project restore-db` - Disaster recovery

### Phase 4: Management
8. `displace project events` - Troubleshooting
9. `displace project scale` - Production management
10. `displace project validate` - CI/CD integration

---

## API Specification Suggestions

### `displace project logs`
```
displace project logs [--follow|-f] [--tail=N] [--component=app|db]

Options:
  -f, --follow     Stream logs continuously
  --tail=N         Show last N lines (default: 100)
  --component      Filter by component (app, database, etc.)
```

### `displace project shell`
```
displace project shell [--component=app|db] [--command="/bin/sh"]

Options:
  --component      Select component to access
  --command        Shell command to execute (default: /bin/sh)
```

### `displace project port-forward`
```
displace project port-forward [--port=8080] [--service=NAME]

Options:
  --port           Local port (default: 8080)
  --service        Service to forward (auto-detected from project)
```

### `displace project sync`
```
displace project sync [SOURCE] [DEST]

Arguments:
  SOURCE           Local path (default: ./content or ./src)
  DEST             Remote path (auto-detected from template type)

Options:
  --watch          Watch for changes and sync continuously
```

---

## Impact Assessment

### If All Commands Implemented:

| Metric | Before | After |
|--------|--------|-------|
| kubectl commands in Makefiles | ~20 per template | 0 |
| External tool dependencies | kubectl required | kubectl optional |
| User experience | Mixed commands | Consistent `displace` CLI |
| Learning curve | High (k8s knowledge) | Low (displace abstracts k8s) |

---

## Notes for CLI PM

1. **Label Selectors:** All templates now use `app.kubernetes.io/name=$(PROJECT_NAME)` consistently
2. **Component Labels:** Templates use `app.kubernetes.io/component=app|database|storage|config`
3. **Namespace:** Always passed as `-n $(NAMESPACE)` or `--namespace`
4. **Container Names:** May need `-c` flag for multi-container pods (caddy, wordpress, mysql)

---

*Report generated by Template PM for CLI PM coordination*
