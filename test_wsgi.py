import cgi
import json
import re


HELLO_WORLD = b"Hello world!\n"


def simple_app(environ, start_response):
    """Simplest possible application object"""
    status = '200 OK'
    print(environ)
    if environ["REQUEST_METHOD"] == 'POST':
        post_env = environ.copy()
        post_env['QUERY_STRING'] = ''
        post = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=post_env,
            keep_blank_values=True
        )
        post_data = \
            list(post)[0].replace(':', '":').replace(', ', '", "').replace('{', '{"').replace('}', '"}').replace('}"', '}')
        for i in range(len(post_data)):
            if post_data[i] == ':':
                if post_data[i+2] != '{':
                    post_data = post_data[:i+2] + '"' + post_data[i+2:]
        json_obj = json.loads(post_data)
        result = json.dumps(json_obj).encode('utf-8') + b'\n'
        print(result)
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [result]
    if environ["REQUEST_METHOD"] == 'GET':
        get_data = environ["QUERY_STRING"]
        get_data = '{"' + str(get_data).replace("=", '": "').replace("&", '", "') + '"}'
        result = get_data.encode('utf-8') + b'\n'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [result]


application = simple_app

dct = {"method": "publish", "params": {"channel": "chat", "data": {"text": "hello"}}}
