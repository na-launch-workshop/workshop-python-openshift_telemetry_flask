from datetime import datetime
from flask import Blueprint, jsonify, request, abort, Response
from opentelemetry import trace
import base64

# Tracing is configured by the OpenTelemetry Operator, not here. The
# instrumentation.opentelemetry.io/inject-python annotation on the deployment
# auto-instruments Flask and exports OTLP/HTTP to the collector sidecar, so all
# this module needs to do is decorate the span the operator already created.

main = Blueprint('main', __name__)

@main.route("/", methods=["GET"])
def index():
    return Response(f"200 OK", mimetype='text/plain')


@main.route('/api/check', methods=['POST'])
def check_json():
    span = trace.get_current_span()
    data = request.get_json()
    if not data or 'amount' not in data:
        span.set_attribute("http.status_code", 500)
        span.set_attribute("error.message", "'amount' key missing in JSON body")
        abort(500, description="'amount' key missing in JSON body")

    try:
        amt = float(data.get('amount'))
    except (ValueError, TypeError):
        span.set_attribute("http.status_code", 500)
        span.set_attribute("error.message", "Invalid amount format")
        abort(500, description="Sending ERROR 500")

    if amt == 1337:
        span.set_attribute("http.status_code", 503)
        span.set_attribute("error.message", base64.b64decode("SWYgeW91IGNhbiBwcm9kdWNlIHRoaXMgbWVzc2FnZSBpbiBKYWVnZXIsIHlvdSd2ZSBmb3VuZCB0aGUgZWFzdGVyIGVnZwo=").decode("utf-8"))
        abort(503, description="Sending ERROR 503")

    if amt < 25000:
        span.set_attribute("http.status_code", 500)
        span.set_attribute("error.message", "Amount below minimum threshold")
        abort(500, description="Sending ERROR 500")

    return jsonify({"message": "SUCCESS VALID", "data": data}), 200
