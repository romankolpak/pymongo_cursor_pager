import pymongo
from dataclasses import dataclass
from typing import Optional, Iterable

from pymongo.collection import Collection

from pymongo_cursor_pager.encode import decode_cursor, encode_cursor


@dataclass
class PaginatedResult:
    data: list
    next: Optional[str]
    previous: Optional[str]
    has_next: bool


def get_pagination_query(next_cursor: Optional[str], previous_cursor: Optional[str]):
    if next_cursor:
        return decode_cursor(next_cursor)

    if previous_cursor:
        return decode_cursor(previous_cursor)

    return {}


def get_next_cursor(query_result: list, sorted_by: Optional[Iterable[tuple]]) -> Optional[dict]:
    if sorted_by is None:
        sorted_by = []

    try:
        last_item = query_result[-1]
    except IndexError:
        return None

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


def get_previous_cursor(query_result: list, sorted_by: Optional[Iterable[tuple]]) -> Optional[dict]:
    if sorted_by is None:
        sorted_by = []

    try:
        first_item = query_result[0]
    except IndexError:
        return None

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


def find(
    collection: Collection,
    query: dict,
    limit: int,
    next_cursor: Optional[str] = None,
    prev_cursor: Optional[str] = None,
    sort: Optional[Iterable[tuple]] = None,
    projection: Optional[dict] = None
) -> PaginatedResult:
    query = {
        '$and': [get_pagination_query(next_cursor, prev_cursor), query]
    }
    # query 1 more than we need just to see if there are more pages
    cursor = collection.find(query, projection).limit(limit + 1)

    items = list(cursor)
    has_next = len(items) > limit

    # remove the last item from the results list since we queried more than requested
    if has_next:
        items.pop()

    # create new set of cursors
    next_cursor = get_next_cursor(items, sort) if has_next else None
    prev_cursor = get_previous_cursor(items, sort)

    return PaginatedResult(
        data=items,
        next=encode_cursor(next_cursor) if next_cursor is not None else None,
        previous=encode_cursor(prev_cursor) if prev_cursor is not None else None,
        has_next=has_next
    )
