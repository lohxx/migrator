#!/usr/bin/env python3
from flask import request


class ServiceAuth:
    def session(self):
        raise NotImplementedError

    def autorization_url(self):
        raise NotImplementedError

    def get_access_token(self):
        raise NotImplementedError


class Playlist:
    def __init__(self, name):
        self.name = name

    def __call__(self):
        return self.get_playlist_tracks()

    def get_playlist_tracks(self):
        raise NotImplementedError

    def get_playlist(self):
        raise NotImplementedError
