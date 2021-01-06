import pymongo
from dataclasses import dataclass
from typing import Optional, Iterable, Tuple, Sized, List

from pymongo.collection import Collection

from pymongo_cursor_pager.encode import decode_cursor, encode_cursor


@dataclass
class PaginatedResult:
    data: list
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    has_next: bool
    has_previous: bool


def get_pagination_query(
    next_cursor: Optional[str], previous_cursor: Optional[str]
) -> dict:
    if next_cursor:
        return decode_cursor(next_cursor)

    if previous_cursor:
        return decode_cursor(previous_cursor)

    return {}


def get_cursor(
    query_result: list, sorted_by: List[Tuple], is_moving_forward: bool = True
) -> Optional[dict]:
    try:
        reference_item = query_result[-1] if is_moving_forward else query_result[0]
    except IndexError:
        return None

    def comparison_op(sdir):
        if is_moving_forward:
            return "$gt" if sdir == pymongo.ASCENDING else "$lt"

        return "$lt" if sdir == pymongo.ASCENDING else "$gt"

    if len(sorted_by) == 1:
        _, sort_direction = sorted_by[0]
        return {"_id": {comparison_op(sort_direction): reference_item["_id"]}}

    if len(sorted_by) == 2:
        non_id_field_name, sort_dir = next(x for x in sorted_by if not x[0] == "_id")
        return {
            "$or": [
                {
                    non_id_field_name: {
                        comparison_op(sort_dir): reference_item[non_id_field_name]
                    }
                },
                {
                    non_id_field_name: reference_item[non_id_field_name],
                    "_id": {comparison_op(sort_dir): reference_item["_id"]},
                },
            ]
        }

    raise ValueError("Invalid sorted_by value.")


def get_next_cursor(query_result: list, sorted_by: List[Tuple]) -> Optional[dict]:
    return get_cursor(query_result, sorted_by, is_moving_forward=True)


def get_prev_cursor(query_result: list, sorted_by: List[Tuple]) -> Optional[dict]:
    return get_cursor(query_result, sorted_by, is_moving_forward=False)


def find(
    collection: Collection,
    query: dict,
    limit: int,
    next_cursor: Optional[str] = None,
    prev_cursor: Optional[str] = None,
    projection: Optional[dict] = None,
    sort: Optional[Tuple] = None,
) -> PaginatedResult:
    pagination_query = get_pagination_query(next_cursor, prev_cursor)
    query = {"$and": [pagination_query, query]}

    if sort is None:
        sort = ("_id", pymongo.ASCENDING)

    sort_field, sort_dir = sort

    if not sort_field == "_id":
        sorted_by = [(sort_field, sort_dir), ("_id", sort_dir)]
    else:
        sorted_by = [(sort_field, sort_dir)]

    # query 1 more than we need just to see if there are more pages
    cursor = collection.find(query, projection).limit(limit + 1).sort(sorted_by)

    items = list(cursor)
    has_next_page = len(items) > limit
    has_previous = has_next_page if prev_cursor else next_cursor is not None

    # remove the last item from the results list since we queried more than requested
    if has_next_page:
        items.pop()

    next_cursor = get_next_cursor(items, sorted_by) if has_next_page else None
    prev_cursor = get_prev_cursor(items, sorted_by) if has_previous else None

    return PaginatedResult(
        data=items,
        next_cursor=encode_cursor(next_cursor) if next_cursor is not None else None,
        prev_cursor=encode_cursor(prev_cursor) if prev_cursor is not None else None,
        has_next=has_next_page,
        has_previous=has_previous,
    )
