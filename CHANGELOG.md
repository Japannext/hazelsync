## v1.3.0

### Features

* Metrics for backup and stream actions using Prometheus PushGateway
* Experimental metrics for backup and stream actions using InfluxDB v2 API

### Changes

* Centralizing log management and making it configurable from the main config file

## v1.2.0

### Features

* Support for PostgreSQL backups by doing rsync with WAL "streaming" (more frequent cronjobs)
* Better handling of plugins for hazel-ssh script: now any plugin can define a behavior for hazel-ssh

## v1.1.0

### Features

* Rsync-based backup support
  * Support for pre/post scripts
* Hashicorp Vault backup support
* A client SSH helper to help with authorization on the host
  * Support for integration with the rsync plugin
* Support for locking during backup
* Plugin system for backup/restore methods (job plugin) and the
  storage backend (backend plugin)
* Support for ZFS backend
