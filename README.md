# Hazelsync

Backup/restore utilies that work in a plugin like manner.

## Installation

For now, no public package is available, but it's possible to build it and
host in a mirror (in a Nexus server internal pip repository for instance).

```bash
poetry build
pip3 install dist/hazelsync-1.3.0-py3-none-any.whl
```

## Configuration

General configuration is done in `/etc/hazelsync.yaml`.

Each cluster to backup should have its configuration in `/etc/hazelsync.d/<cluster_name>.yaml`.

More details:
* [General configuration](./docs/configuration.md)
* [Rsync job](./docs/jobs/rsync.md)

## Usage

The you can start the backup with:
```bash
sudo hazel backup mycluster
```
