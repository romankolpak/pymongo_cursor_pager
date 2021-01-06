#!/usr/bin/env python

from distutils.core import setup

setup(
    name="PyMongo Cursor Pager",
    version="0.0.1",
    description="Cursor-based pagination for PyMongo",
    author="Roman K.",
    author_email="roman.kolpak@gmail.com",
    url="",
    install_requires=["pymongo"],
    packages=[
        "pymongo_cursor_pager",
    ],
)
