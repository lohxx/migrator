import rauth

from migrator.services.auth import ServiceAuth


class DeezerService(ServiceAuth):
    def __init__(self):
        self.oauth = None
