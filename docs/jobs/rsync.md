# Rsync

A plugin that backup data from remote hosts using rsync.

## Configuration

To use this plugin, a system user need to be configured on the server, and its `~/.ssh/authorized_keys` need to be configured appropriately.

The user need to have recursive read access to the list of paths configured to be backed up.

## Job options

* `hosts` (mandatory): An array of hostname to backup the data from. Note that each host will get
  its own snapshots.
* `paths` (mandatory): An array of absolute paths to backup data from.
* `user`: The user to SSH to the hosts as.
* `private_key`: The path to the private key to use to SSH.
* `pre_scripts`: An array of scripts to run on the remote servers before rsync. Will not rsync if
  one of the script return non-zero.
* `post_scripts`: An array of scripts to run on the remote servers after rsync. Will consider the
  backup as failed, and will not perform a snapshot if one of the script returns non-zero.

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
* `allowed_scripts` (List of strings): Allow the user to run one of the command specified in `allowed_scripts`. Note that arguments have to be precised separated by spaces, and wildcards are not supported. This is used to configure pre/post scripts.

Example usage:
```yaml
# /etc/hazelsync-ssh.yaml
---
plugin: rsync
options:
  allowed_paths: [ '/var/log', '/opt' ]
  allowed_scripts: [ '/usr/local/bin/custom-script' ]
```
