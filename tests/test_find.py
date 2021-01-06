from uuid import uuid4

import pytest
import pymongo
import os

from bson import ObjectId

from pymongo_cursor_pager.find import find, PaginatedResult


class match_any:
    def __init__(self, type):
        self.type = type

    def __eq__(self, other):
        return isinstance(other, self.type)


@pytest.fixture
def mongo_client():
    return pymongo.MongoClient(host=os.getenv("MONGO_HOST") or "localhost")


@pytest.yield_fixture()
def collection(mongo_client):
    db_name = "pymongo_cursor_pager_tests_{}".format(uuid4())

    mongo_client[db_name].records.insert_many(
        [
            {"name": "John", "age": 23},
            {"name": "John", "age": 24},
            {"name": "Jane", "age": 25},
            {"name": "Alice", "age": 26},
            {"name": "Peter", "age": 24},
        ]
    )

    yield mongo_client[db_name].records

    mongo_client.drop_database(db_name)


def test_cursor(collection):
    result = find(collection, {}, limit=3)
    assert isinstance(result, PaginatedResult)

    assert result.data == [
        {"_id": match_any(ObjectId), "name": "John", "age": 23},
        {"_id": match_any(ObjectId), "name": "John", "age": 24},
        {"_id": match_any(ObjectId), "name": "Jane", "age": 25},
    ]
    assert result.has_previous is False
    assert result.has_next is True
    assert result.prev_cursor is None
    assert result.next_cursor is not None

    result = find(collection, {}, limit=3, next_cursor=result.next_cursor)
    assert isinstance(result, PaginatedResult)

    assert result.data == [
        {"_id": match_any(ObjectId), "name": "Alice", "age": 26},
        {"_id": match_any(ObjectId), "name": "Peter", "age": 24},
    ]
    assert result.has_previous is True
    assert result.has_next is False
    assert result.prev_cursor is not None
    assert result.next_cursor is None

    result = find(collection, {}, limit=3, prev_cursor=result.prev_cursor)
    assert isinstance(result, PaginatedResult)

    assert result.data == [
        {"_id": match_any(ObjectId), "name": "John", "age": 23},
        {"_id": match_any(ObjectId), "name": "John", "age": 24},
        {"_id": match_any(ObjectId), "name": "Jane", "age": 25},
    ]
    assert result.has_previous is False
    assert result.has_next is False
    assert result.prev_cursor is None
    assert result.next_cursor is None
