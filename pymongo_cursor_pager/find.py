import pymongo
from dataclasses import dataclass
from typing import Optional, Iterable

from bson import ObjectId

from pymongo.collection import Collection

from pymongo_cursor_pager.encode import decode_cursor, encode_cursor


@dataclass
class PaginatedResult:
    data: list
    next: Optional[str]
    previous: Optional[str]
    has_next: bool


@dataclass
class PaginationOptions:
    limit: int
    next: Optional[str]
    previous: Optional[str]
    sort: Iterable[tuple]


def get_pagination_query(options):
    if options.next:
        return decode_cursor(options.next)

    if options.previous:
        return decode_cursor(options.previous)

    return {}


def get_next_cursor(query_result: list, options: PaginationOptions) -> dict:
    last_item = query_result[-1]
    sorted_by = options.sort

    if '_id' not in dict(sorted_by):
        sorted_by += [('_id', pymongo.ASCENDING)]

    next_query = {}

    for (field_name, sort_direction) in sorted_by:
        comparison_op = '$gt' if sort_direction == pymongo.ASCENDING else '$lt'
        last_value = last_item[field_name]
        next_query[field_name] = {
            comparison_op: last_value
        }

    return next_query


def get_previous_cursor(query_result: list, options: PaginationOptions):
    first_item = query_result[0]
    sorted_by = options.sort

    if '_id' not in dict(sorted_by):
        sorted_by += [('_id', pymongo.ASCENDING)]

    prev_query = {}

    for (field_name, sort_direction) in sorted_by:
        comparison_op = '$lt' if sort_direction == pymongo.ASCENDING else '$gt'
        first_value = first_item[field_name]
        prev_query[field_name] = {
            comparison_op: first_value
        }

    return prev_query


def find(collection: Collection, query: dict, options: PaginationOptions) -> PaginatedResult:
    cursor = collection.find({
        '$and': [get_pagination_query(options), query]
    }).limit(options.limit)

    items = list(cursor)

    return PaginatedResult(
        data=items,
        next=encode_cursor(get_next_cursor(items, options)),
        previous=encode_cursor(get_next_cursor(items, options)),
        has_next=True  # todo
    )




