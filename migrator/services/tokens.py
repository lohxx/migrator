import json
import os

import click
import sqlalchemy.orm.exc as sq_exceptions

from migrator import db


def save_tokens(service, tokens):
    args = {}
    for key, value in tokens.items():
        if hasattr(TokensManager, key):
            args.update({key: value})

    args.update({'service': service})
    obj = update_or_create(service, args)

    try:
        db.session.add(obj)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        click.echo(e)


def update_or_create(service, kwargs):

    try:
        obj = TokensManager.query.filter_by(
            service=service).one()

        for attr, value in kwargs.items():
            # atualiza os valores já existentes
            setattr(obj, attr, value)

        return obj
    except sq_exceptions.NoResultFound:
        return TokensManager(**kwargs)


def get_tokens(service):
    return TokensManager.query.filter_by(
        service=service,
    ).order_by(
        TokensManager.id.desc()
    ).one()


def delete_tokens(**params):
    TokensManager.query.filter_by(**params).delete()
    try:
        db.session.commit()
    except Exception as e:
        click.echo(e)
        db.session.rollback()


class TokensManager(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=True)
    access_token = db.Column(db.String, nullable=True)
    refresh_token = db.Column(db.String, nullable=True)
    service = db.Column(db.Integer)
