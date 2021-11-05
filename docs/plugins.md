# Plugin

## Installing third party plugins

## Plugin creation

Plugins can be created in a different pip package.
We're using an entry point system, so the main class of your
plugin should be exposed to at least one of the following namespace:
* `hazelsync.job` for job plugins
* `hazelsync.backend` for backend plugins
* `hazelsync.ssh` for SSH helper plugins (`hazel-ssh`)

### Job plugin

Jobs are plugin type to handle the backup and restore functions.
It also have access to the backend API, which is crucial for managing
the available storage slots.

#### Slots

Slots are directories inside your backup backend. Depending on your backup
job, they might represent different hosts, different databases, different
disks, etc. They should be separated by failure potential, which mean that
a failure of one slot should not affect the backup of the other slots.
Slots are also snapshotted independently in the backend plugin, so that there
will be no snapshot of partially successful backup.

There are several quirks with slots:
* You can use `backend.ensure_slot(name)` to ensure the creation of a slot by name. It will returns a
  `pathlib.Path` representing the directory absolute path of the slot. The slot boostrapping will be
  handled in the backend appropriately (directory creation, zfs dataset, etc).
* The `backup()` method should return the list of slots that succeeded. These slots will then
  later be snapshot by the backend.

#### Example

Here is an example of a custom job plugin:
```python
class CustomJob:
    def __init__(self, backend, *args):
        self.slot = backend.ensure_slot('myslot')
    def backup(self):
        '''
        Execute the backup.
        Returns the list of slots that were successfully backed up.
        '''
        myfile = self.slot / 'myfile.txt'
        myfile.write_text('dummy data')
        return [self.slot]

    def restore(self, snapshot):
        '''
        Restore the data to its original location.
        The snapshot argument is a pathlib.Path of a mounted directory containing the snapshot to
        restore.
        '''
```

### Backend plugin

#### Example

```python
```


### SSH plugin

#### Example

Example of a SSH helper that authorize a command:
```python
from hazelsync.ssh import SshHelper, Unauthorized

class CustomSsh(SshHelper):
    def authorize(self, cmd_line: str):
        cmd = cmd_line.split(' ')
        if cmd[0] == '/usr/local/bin/custom-script':
            pass
        else:
            raise Unauthorized(f"Unauthorized script: `{cmd_line}`")
```

Example of a SSH helper that wraps a command:
```python
import subprocess
from hazelsync.ssh import SshHelper, Unauthorized

class CustomSsh(SshHelper):
    def run(self, cmd_line: str):
        cmd = cmd_line.split(' ')
        if cmd[0] == '/usr/local/bin/custom-script':
            cmd_line += ' arg1 arg2'
            subprocess.run(cmd_line, shell=True)
        else:
            raise Unauthorized(f"Unauthorized script: `{cmd_line}`")
```
