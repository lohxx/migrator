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

    def get_tracks(self):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError


class Service:
    def copy_playlist(self, playlist):
        raise NotImplementedError
