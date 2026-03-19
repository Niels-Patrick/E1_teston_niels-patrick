"""
Health routes module.

This file contains the routes needed to check the health of the API (with
Uptime Kuma).
"""

from datetime import datetime
from flask import Blueprint, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from src.app.db_manager import db

# Defining a Blueprint for the Health page routes
health_management = Blueprint("health_management", __name__)


REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint']
)


@health_management.before_request
def count_request():
    REQUEST_COUNT.labels(method='GET', endpoint='/').inc()


@health_management.route("/", methods=["GET"])
def health() -> Response:
    try:
        db.session.execute("SELECT 1")
        db.session.commit()
        return {
            "status": "ok",
            "timestamp": datetime.utcnow()
        }
    except Exception:
        Response.status_code = 503
        return {
            "status": "fail",
            "timestamp": datetime.utcnow()
        }


@health_management.route("/metrics", methods=["GET"])
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
