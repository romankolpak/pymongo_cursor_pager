import base64
import json

import bson


def base64_encode(string):
    """
    base64's `urlsafe_b64encode` uses '=' as padding.
    These are not URL safe when used in URL parameters.

    Removes any `=` used as padding from the encoded string.
    """
    encoded = base64.urlsafe_b64encode(string)
    return encoded.rstrip(b"=")


def base64_decode(string):
    """
    base64's `urlsafe_b64encode` uses '=' as padding.
    These are not URL safe when used in URL parameters.

    Adds back in the required padding before decoding.
    """
    padding = 4 - (len(string) % 4)
    string = string + (b"=" * padding)
    return base64.urlsafe_b64decode(string)


def encode_cursor(cursor):
    return base64_encode(bson.encode(cursor))


def decode_cursor(cursor_str):
    return bson.decode(
        base64_decode(cursor_str)
    )
