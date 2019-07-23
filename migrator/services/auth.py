#!/usr/bin/env python3
from flask import request


class ServiceAuth:
    def autorization_url(self):
        raise NotImplementedError

    def get_access_token(self):
        raise NotImplementedError
