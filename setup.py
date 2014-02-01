"""Distutils module for csrv package."""

from distutils.core import setup

PACKAGE_NAME = 'csrv'

setup(
    name=PACKAGE_NAME,
    packages=[
        'csrv',
        'csrv.controller',
        'csrv.model',
        'csrv.model.actions',
        'csrv.model.actions.subroutines',
        'csrv.model.cards',
        'csrv.model.cards.corp',
        'csrv.model.cards.runner',
    ],
    url='http://makearun.net',
    version='0.3',
)
