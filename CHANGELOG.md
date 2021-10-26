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
