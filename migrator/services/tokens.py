import json
import os

# Salvar os tokens no filesystem é a melhor opção???


class TokensManager:
    def __init__(self, service):
        self.service = service
        self.code = None
        self.refresh_token = None
        self.access_token = None

    def save_tokens(self, response):
        with open(f'{self.service}.json', 'w') as f:
            json.dumps(response, f)

    def retrieve_tokens(self):
        access_token, refresh_token = None, None
        with open(f'{self.service}.json', 'r') as f:
            response = json.load(f)
            self.access_token = response.get('access_token')
            self.refresh_token = response.get('refresh_token')

        return self.access_token, self.refresh_token

    def is_first_auth(self):
        return f'{service}.json' in os.listdir(os.getcwd())