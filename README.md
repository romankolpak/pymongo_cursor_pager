# pymongo_cursor_pager

This package implements cursor-based pagination for Python apps using PyMongo. Inspired a similar tool [mixmaxhq/mongo-cursor-pagination](https://github.com/mixmaxhq/mongo-cursor-pagination) for JavaScript.

## What is cursor-based pagination

A more classical offset-based pagination approach where offset/limit parameters are passed in the HTTP 
request has a pretty big downside -- it may skip over records which are being added to the list in-between HTTP requests.
One way to solve this is to paginate using "cursors",

## Installation

```
pip install pymongo_cursor_pager
```

## API

The API is pretty simple:

```

>>> import pymongo
>>> from pymongo_cursor_pager import find
>>> client = pymongo.MongoClient()


>>> result = find(client.my_db.my_collection, query={}, limit=2)
PaginatedResult(data=[{'_id': ObjectId('..'), 'name': 'foo'}, {'_id': ObjectId('..'), 'name': 'bar'}], next_cursor='IAAAAANfaWQAFgAAAAckZ3QAX5a1_Cq0RUg2wvYkAAA', prev_cursor=None, has_next=True, has_previous=False)


>>> result = find(client.my_db.my_collection, query={}, limit=2, next_cursor=result.next_cursor)
PaginatedResult(data=[{'_id': ObjectId('..'), 'name': 'baz'}, {'_id': ObjectId('..'), 'name': 'quux'}], next_cursor=None, prev_cursor='IAAAAANfaWQAFgAAAAckZ3QAX5a1_Bq0RUg2wvYkAAA', has_next=False, has_previous=False)
```