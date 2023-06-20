#!/usr/bin/env python

#  Copyright (c) 2014 unfoldingWord
#  
#  http://creativecommons.org/licenses/MIT/
#  
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#  
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

#  Contributors:
#  Patrick Altman <paltman@eldarion.com>
#  Jesse Griffin <jesse@distantshores.org>
#  Jaap-Jan Swijnenburg <jaap-jan.swijnenburg@unfoldingword.org>

import sys
import json

from datetime import timedelta
from functools import update_wrapper

from flask import Flask, request, make_response, current_app
from urllib.request import urlopen
from urllib.error import HTTPError, URLError
import logging
from socket import timeout

app = Flask(__name__)
app.debug = True

# Init logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Loading langnames.json at startup
# Initially from URL. If URL does timeout, then load from local (which might be slightly outdated)
# Try catch flow taken from https://stackoverflow.com/a/8763542
url = "https://td.unfoldingword.org/exports/langnames.json"
try:
    source = urlopen(url, timeout=10)
    logging.info('Loading languages from URL %s', url)
except HTTPError as error:
    logging.error('HTTP Error: Data not retrieved because %s\nURL: %s', error, url)
    logging.info('Loading from local file: langnames.json')
    source = open("langnames.json")
except URLError as error:
    if isinstance(error.reason, timeout):
        logging.error('Timeout Error: Data not retrieved because %s\nURL: %s', error, url)
        logging.info('Loading from local file: langnames.json')
        source = open("langnames.json")
    else:
        logging.error('URL Error: Data not retrieved because %s\nURL: %s', error, url)
        logging.info('Loading from local file: langnames.json')
        source = open("langnames.json")

data = json.loads(source.read())


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ", ".join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, str):
        headers = ", ".join(x.upper() for x in headers)
    if not isinstance(origin, str):
        origin = ", ".join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers["allow"]

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == "OPTIONS":
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != "OPTIONS":
                return resp

            h = resp.headers

            h["Access-Control-Allow-Origin"] = origin
            h["Access-Control-Allow-Methods"] = get_methods()
            h["Access-Control-Max-Age"] = str(max_age)
            if headers is not None:
                h["Access-Control-Allow-Headers"] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


@app.route("/")
@crossdomain(origin="*")
def autocomplete():
    # {"cc": ["ET"], "ln": "Afaraf", "lr": "Africa", "lc": "aa"}
    term = request.args.get("q").lower()
    d = []
    if len(term) <= 3:
        # search: cc, lc
        d.extend([
            x
            for x in data
            if term in x["lc"].lower() or term in [y.lower() for y in x["cc"]]
        ])
    if len(term) >= 3:
        # search: ln, lr
        d.extend([
            x
            for x in data
            if term in x["ln"].lower() or term in x["lr"].lower() or term in x["ang"].lower()
        ])

    full_result = {"count": len(d), "term": term, "results": d}
    response = app.response_class(
        response=json.dumps(full_result),
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == "__main__":
    try:
        port_number = int(sys.argv[1])
    except:
        port_number = 5000

    app.run(host='0.0.0.0', port=port_number)
