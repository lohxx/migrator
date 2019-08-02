#!/usr/bin/env python3
from abc import ABC, abstractmethod


class ServiceAuth(ABC):
    @abstractmethod
    def session(self):
        pass

    @abstractmethod
    def autorization_url(self):
        pass


class Playlist(ABC):
    @abstractmethod
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_tracks(self):
        pass

    @abstractmethod
    def get(self):
        pass

