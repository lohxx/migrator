from migrator.services.auth import ServiceAuth


class YoutubeService(ServiceAuth):
    def __init__(self):
        self.oauth = None