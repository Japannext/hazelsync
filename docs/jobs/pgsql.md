# PgSQL

A plugin that backup data from remote PostgreSQL server using rsync.
The datadir of the PostgreSQL server will be backed up, and a helper script
will be provided to backup WAL.

## Configuration

To use this plugin, a system user need to be configured on the server, and its `~/.ssh/authorized_keys` need to be configured appropriately.

The user need to have recursive read access to the list of paths configured to be backed up.

## Job options

* `hosts` (mandatory): An array of hostname to backup the data from. Note that each host will get
  its own snapshots.
* `datadir` (mandatory): The PostgreSQL datadir.
* `waldir` (mandatory): The PostgreSQL directory where Write Ahead Logs (WAL) are written.
* `delete_wal` (default to `true`): A boolean to indicate that the WAL will be removed from the target server when using stream.
* `user`: The user to SSH to the hosts as.
* `private_key`: The path to the private key to use to SSH.

## Authorization helper script

In order to improve security, it is possible to install `hazelsync` on the remote server, then use
the dedicated helper script to limit the possible actions of the remote user.

Example `~/.ssh/authorized_keys`:
```
command="/usr/local/bin/hazel-ssh" ssh-rsa AAAAB...==
```

The `hazel-ssh` script will read the `/etc/hazelsync-ssh.yaml` configuration if present.

Hazelsync SSH options:
* `allowed_paths` (List of strings): When the command the remove user execute is `rsync`, it will ensure the source path is a children of one of the `allowed_paths`.

Example usage:
```yaml
# /etc/hazelsync-ssh.yaml
---
plugin: pgsql
options:
  allowed_paths: [ '/var/lib/pgsql' ]
```

## Usage

It is recommended to use a fast cronjob (every 2 minutes for instance) for pulling WAL.
To backup WAL, use the following command:
```bash
sudo hazel stream <backup_name>
```
Note that by default, the WAL will be removed from the source server.

The full backup of the datadir is handled by this command:
```bash
sudo hazel backup <backup_name>
```
