import json
import urllib2

from datetime import timedelta
from functools import update_wrapper

from flask import Flask, request, jsonify, make_response, current_app


app = Flask(__name__)
app.debug = True


try:
    source = open("langnames.json")
except IOError:
    source = urllib2.urlopen(
        "http://td.unfoldingword.org/exports/langnames.json"
    )
data = json.loads(source.read())


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ", ".join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ", ".join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
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
            if term in x["ln"].lower() or term in x["lr"].lower()
        ])
    return jsonify({"results": d, "count": len(d), "term": term})


if __name__ == "__main__":
    app.run()
