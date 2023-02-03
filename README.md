
### CRUD 
 - create 
 - read
 - update
 - delete

```python
@app.post()
@app.put()
@app.delete()
# communication options to the target
@app.options()
@app.head()
@app.patch()
# message loop-back
@app.trace()
# creates a tunnel to the server, based on target resource
@app.connect()
```
## Important Links

### HTTP Status Codes
https://en.wikipedia.org/wiki/List_of_HTTP_status_codes<br>

http://localhost:8000/openapi.json <br>
http://localhost:8000/docs


Recommended file structure
```bash
your_project
├── __init__.py
├── main.py
├── core
│   ├── models
│   │   ├── database.py
│   │   └── __init__.py
│   ├── schemas
│   │   ├── __init__.py
│   │   └── schema.py
│   └── settings.py
├── tests
│   ├── __init__.py
│   └── v1
│       ├── __init__.py
│       └── test_v1.py
└── v1
    ├── api.py
    ├── endpoints
    │   ├── endpoint.py
    │   └── __init__.py
    └── __init__.py 
```