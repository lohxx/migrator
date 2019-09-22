#!/usr/bin/env python3
import itertools
import json
import pdb
import re
import webbrowser

from abc import ABC, abstractmethod
from flask import request

from migrator.services.tokens import save_tokens, get_tokens


class ServiceAuth(ABC):
    SERVICE_CODE = None

    def __init__(self):
        self.oauth = None
       
    @abstractmethod
    def session(self):
        pass

    def _get_access_token(self, args):
        try:
            session = self.oauth.get_auth_session(
                data=args,
                decoder=json.loads,
            )
        except Exception as e:
            session = self.oauth.get_auth_session(
                decoder=json.loads,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': get_tokens(self.SERVICE_CODE).refresh_token
                }
            )

        return session

    def autorization_url(self, args):
        autorization_url = self.oauth.get_authorize_url(**args)
        webbrowser.open(autorization_url)

        return self


class Playlist(ABC):
    @abstractmethod
    def copy(self, playlist):
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
        normalized_track = re.sub("[^\w\s\.,']+", "", track)
        normalized_match = re.sub("[^\w\s\.,']+", "", match)
        track_regexp = re.compile(f'({normalized_track})', flags=re.IGNORECASE)
        if track_regexp.search(normalized_match):
            return normalized_track, True
        
        return normalized_track, False

    def _diff_tracks(self, already_existents, new_tracks):
        tracks_to_be_copied = []

        dict_new, dict_existents = {}, {}

        if not already_existents:
            return new_tracks

        for existent, new in itertools.zip_longest(already_existents, new_tracks):
            if not all([existent, new]):
                continue

            dict_new[f'{new["name"]} - {new["artists"][0]}'] = new
            dict_existents[f'{existent["name"]} - {existent["artists"][0]}'] = existent

        for track_key in dict_new:
            if track_key not in dict_existents:
                tracks_to_be_copied.append(dict_new[track_key])

        return tracks_to_be_copied
