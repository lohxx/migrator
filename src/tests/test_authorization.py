from migrator.services.spotify import SpotifyAuth
from migrator.services.deezer import DeezerAuth
from migrator.services import tokens

import requests

import sqlalchemy.orm.exc as sq_exceptions


class TestDeezerAuth:

    def test_authorization(self, monkeypatch):
        # O servidor precisa estar rodando para receber os tokens de volta
        deezerAuth = DeezerAuth()

        def get_tokens_mock(service_code):
            raise sq_exceptions.NoResultFound

        def save_tokens_mock(service_code, tokens):
            import pdb; pdb.set_trace()

        def authorization_url_mock(url_args):
            # url_args.update({'dispatch_path': 'auth'})
            t = deezerAuth.oauth.get_authorize_url(**url_args)
            import pdb; pdb.set_trace()
            assert True

        monkeypatch.setattr(
            tokens,
            'get_tokens',
            get_tokens_mock)

        monkeypatch.setattr(
            tokens,
            'save_tokens',
            save_tokens_mock)

        monkeypatch.setattr(
            deezerAuth,
            'autorization_url',
            authorization_url_mock   
        )

        deezerAuth.authenticate()



class TestSpotifyAuth:
    pass