# Configuration

## Global configuration

Location: `/etc/hazelsync.yaml`

Options:
* `default_backend` (`zfs`, `localfs`, `dummy`): The default backend to use for jobs.
  More info in backend documentation.
* `backend_options`: A key-value of options for the backend, organized per backend type.

Example of configuration:
```yaml
---
default_backend: zfs
job_options:
    rsync:
        private_key: /root/backup.key
backend_options:
    zfs:
        basedir: /backup
    localfs:
        basedir: /local_backup
```

## Job configuration

Each job need to be configured in `/etc/hazelsync.d/<job_name>.yaml`.

Settings:
* `name` (mandatory): The display name of the job.
* `job` (mandatory): The job plugin to use to backup the cluster.
  Supported job plugins (natively):
  * [`rsync`](./docs/jobs/rsync.md): A plugin that uses rsync to backup data on remote hosts.
  * [`vault`](./docs/jobs/vault.md): A plugin to backup Hashicorp Vault over its API.
* `options` (usually mandatory): The options to pass to the job plugin. See job plugin documentation
  to see the specific options that can be passed to the plugin.
* `backend_type`: Override the `default_backend` provided in the global configuration.
* `backend_options`: Override the backend options provided in the global configuration.

Example configuration:
```yaml
name: My Job
job: rsync
options:
    hosts: ['host01', 'host02', 'host03']
    paths: ['/var/log', '/etc']
```

## SSH configuration

Example:
```yaml
# /etc/hazelsync-ssh.yaml
---
plugin: rsync
options:
  allowed_paths: [ '/var/log', '/opt' ]
```
