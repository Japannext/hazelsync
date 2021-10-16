'''Utils for the different backup types'''

from enum import Enum

from .rsync import Rsync

class BackupType(Enum):
    '''An enum to select the correct backup type'''
    RSYNC = 'rsync'

def get_backup_job(backup_type: BackupType):
    '''Return the backup class associated with string representing the backup type
    :param backup_type: The type of the backup.
    '''
    mapping = {
        'rsync': Rsync,
    }
    backup_job = mapping.get(backup_type)
    if backup_job is None:
        raise Exception(f"Backup type {backup_type} is invalid")
    return backup_job
