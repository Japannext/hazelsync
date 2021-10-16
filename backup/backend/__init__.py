'''Define the interface for backends storage'''

class Interface:
    pass

class FsInterface(Interface):
    pass

class StreamInterface(Interface):
    pass

class Snapshot:
    pass

class Slot:
    def __init__(self):
        pass
    def bootstrap(self):
        pass
    def snapshot(self):
        pass

class Backend:
    def __init__(self):
        self.supported_interfaces = []
        self.concurrent_backups = False
    def lock_backend(self):
        pass
    def lock(self, slot_name):
        pass
