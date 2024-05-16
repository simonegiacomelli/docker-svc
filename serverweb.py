#!/usr/bin/env python3

import os
from functools import partial
from http.server import HTTPServer

from dispatch import Dispatch
from webservice import WebService
from request_handler import RequestHandler
import sys


def main():
    cwd = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__)
    print(f'cwd={cwd}')
    os.chdir(cwd)

    port = 8090
    print('Starting server web v1.0.0 ')
    print(f'Web server address http://localhost:{port}/')
    print(f'Web server address http://0.0.0.0:{port}/')

    api_dispatch = Dispatch().register(WebService, 'API_')

    def handler(request: RequestHandler) -> bool:
        params, rpath = request.decode_request()
        api_prefix = '/svc/'

        if rpath == '/' or rpath == api_prefix:
            request.send_response(302)
            request.send_header('Location', f'{api_prefix}index')
            request.end_headers()
            return True

        if not rpath.startswith(api_prefix):
            return False

        api_name = rpath[len(api_prefix):]

        if api_name == 'list':
            request.send_json(list(api_dispatch.registered.keys()))
        elif api_name == 'index':
            request.serve_file(os.path.dirname(__file__), "index.html")
        else:
            instance = WebService()
            instance.request = request
            result = api_dispatch.dispatch(instance, api_name, params)
            if isinstance(result, str):
                print(result)
                request.send_string(result)
            elif isinstance(result, (list, set, dict, tuple)):
                request.send_json(result)
            else:
                request.send_json(result.__dict__)

        return True

    httpd = HTTPServer(('', port), partial(RequestHandler, handler=handler))
    httpd.timeout = 10

    print('serving...')
    httpd.serve_forever()
    exit(0)


if __name__ == '__main__':
    main()
