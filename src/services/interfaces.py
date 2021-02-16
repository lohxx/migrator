#!/usr/bin/env python3
import itertools
import json
import pdb
import re
import webbrowser

from abc import ABC, abstractmethod
from flask import request

#from src import read_pickle

from src.utils import PickleHandler

pickle_manager = PickleHandler('tokens.pickle')


class ServiceAuth(ABC):

    def __init__(self):
        self.oauth = None
        self.session = None

    @abstractmethod
    def authenticate(self):
        pass

    def _get_access_token(self, args):
        try:
            session = self.oauth.get_auth_session(
                data=args,
                decoder=json.loads,
            )
        except Exception:
            tokens = pickle_manager.read_pickle()
            session = self.oauth.get_auth_session(
                decoder=json.loads,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': tokens['spotify']['refresh_token']
                }
            )

        return session

    def autorization_url(self, args):
        autorization_url = self.oauth.get_authorize_url(**args)
        webbrowser.open(autorization_url)
        return self


class Playlist(ABC):
    @abstractmethod
    def clone(self, playlist):
        pass

    @abstractmethod
    def get_tracks(self, tracks_url):
        pass

    @abstractmethod
    def get(self, name):
        pass

    @abstractmethod
    def search_playlist(self, name):
        pass

    def match_track(self, track, match):
        normalized_track = re.sub("[^\w\s\.,']+", "", track).lower().replace(' ', '')
        normalized_match = re.sub("[^\w\s\.,']+", "", match).lower().replace(' ', '')
        track_regexp = re.compile(f'({normalized_match})', flags=re.IGNORECASE)
        print(f'{normalized_match}, {normalized_track}, {track_regexp.search(normalized_track)}')
        if track_regexp.search(normalized_track):
            return normalized_track, True

        return track, False

    def _diff_tracks(self, already_existents, new_tracks):
        tracks_to_be_copied = []

        dict_new, dict_existents = {}, {}

        if not already_existents:
            return new_tracks

        for existent, new in itertools.zip_longest(
                already_existents, new_tracks):
            if not all([existent, new]):
                continue

            dict_new[f'{new["name"]} - {new["artists"][0]}'.lower()] = new
            dict_existents[f'{existent["name"]} - {existent["artists"][0]}'.lower()] = existent

        for track_key in dict_new:
            if track_key not in dict_existents:
                tracks_to_be_copied.append(dict_new[track_key])

        return tracks_to_be_copied
