'''Resources used by SSH helpers scripts'''

from abc import abstractmethod

class Unauthorized(RuntimeError):
    '''An exception to reject unauthorized commands'''

class SshHelper:
    '''A base class for a SSH helper'''

    @abstractmethod
    def authorize(self, cmd_line: str):
        '''
        Check if the cmd_line is authorized by the plugin.
        :param cmd_line: The command to check the authorization.
        :raises hazelsync.ssh_helper.Unauthorized: Raised if the command is unauthorized.
        '''

    @abstractmethod
    def run(self, cmd_line: str):
        '''
        Check and run the cmd_line. Define this method instead of
        authorize if you need to modify the command before running it.
        :param cmd_line: The command to check the authorization and run.
        :raises hazelsync.ssh_helper.Unauthorized: Raised if the command is unauthorized.
        '''
