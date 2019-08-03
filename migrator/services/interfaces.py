#!/usr/bin/env python3
import json
import webbrowser

from abc import ABC, abstractmethod

from migrator.services.tokens import save_tokens, get_tokens


class ServiceAuth(ABC):
    SERVICE_CODE = None

    def __init__(self):
        self.oauth = None

    def _get_access_token(self, args):
        return
        try:
            session = self.oauth.get_auth_session(
                data=args,
                decoder=json.loads,
                method='GET'
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

    @abstractmethod
    def session(self):
        pass


class Playlist(ABC):
    @abstractmethod
    def get_tracks(self):
        pass

    @abstractmethod
    def get(self):
        pass

    def request(self, endpoint, page=0, limit=30):
        response = self.oauth.session.get(endpoint)

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()
