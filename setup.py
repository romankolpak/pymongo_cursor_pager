#!/usr/bin/env python

from distutils.core import setup

setup(
    name="pymongo_cursor_pager",
    version="0.0.1",
    description="Cursor-based pagination for apps using PyMongo",
    author="Roman Kolpak",
    author_email="roman.kolpak@gmail.com",
    url="",
    install_requires=["pymongo>=3.0"],
    extras_require={
        "dev": [
            "pytest",
            "black",
        ]
    },
    packages=[
        "pymongo_cursor_pager",
    ],
)
