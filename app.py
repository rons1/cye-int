from time import sleep

from flask import Flask, request, Response
from requests import get, post, put, patch, delete
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache


app = Flask('__main__')

REMOTE_HOSTNAME = 'https://reqres.in/api/'
NUMBER_OF_MINUTES_TO_CACHE = 1

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per day", "10 per minute"]
)

config = {
    "DEBUG": True,  # some Flask specific configs
    "CACHE_TYPE": "simple",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 60 * NUMBER_OF_MINUTES_TO_CACHE
}

app.config.from_mapping(config)
cache = Cache(app)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
@limiter.limit("1000/day")
@limiter.limit("10/minute")
@cache.cached(timeout=60 * NUMBER_OF_MINUTES_TO_CACHE)
def proxy(path):
    url = f'{REMOTE_HOSTNAME}{path}'
    if request.method == 'GET':
        res = get(url, params=request.args)
    elif request.method == 'POST':
        res = post(url, params=request.args, json=request.get_json())
    elif request.method == 'PUT':
        res = put(url, params=request.args, json=request.get_json())
    elif request.method == 'PATCH':
        res = patch(url, params=request.args, json=request.get_json())
    elif request.method == 'DELETE':
        res = delete(url)
    else:
        return 'Unsupported HTTP method'

    return Response(res.content, res.status_code)


app.run(host='127.0.0.1', port=8080, threaded=True)
