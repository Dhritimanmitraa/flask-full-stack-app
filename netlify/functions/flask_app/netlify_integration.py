import json
from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import Headers
import base64

def run_wsgi_app(app, event, context):
    headers = Headers()
    for key, value in event["headers"].items():
        headers.add(key, value)

    method = event["httpMethod"]
    path = event["path"]
    body = event["body"]

    if event["isBase64Encoded"] and body:
        body = base64.b64decode(body)
    elif body is None:
        body = b''
    else:
        body = body.encode('utf-8')

    with Request.application(app) as request:
        request.method = method
        request.path = path
        request.headers = headers
        request.data = body

        response = request.get_response(app)

        response_headers = {}
        for key, value in response.headers.items():
            response_headers[key] = value

        return {
            "statusCode": response.status_code,
            "headers": response_headers,
            "body": response.get_data(as_text=True)
        }
