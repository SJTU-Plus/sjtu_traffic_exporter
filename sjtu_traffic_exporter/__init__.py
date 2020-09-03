from typing import Dict

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from prometheus_client import Gauge, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from .traffic import CanteenTraffic, LibraryTraffic

app = Flask(__name__)
scheduler = BackgroundScheduler()

canteen_traffic = CanteenTraffic()
library_traffic = LibraryTraffic()

canteen_fields = canteen_traffic.fields()
library_fields = library_traffic.fields()
canteen_occupied_metrics: Dict[str, Gauge] = {field: Gauge(f"Traffic_Canteen_{field}", f"Traffic of {field}") for field
                                              in canteen_fields}
library_occupied_metrics: Dict[str, Gauge] = {field: Gauge(f"Traffic_Library_{field}", f"Traffic of {field}") for field
                                              in library_fields}
canteen_overall_metrics: Dict[str, Gauge] = {field: Gauge(f"Capacity_Canteen_{field}", f"Capacity of {field}") for field
                                             in canteen_fields}
library_overall_metrics: Dict[str, Gauge] = {field: Gauge(f"Capacity_Library_{field}", f"Capacity of {field}") for field
                                             in library_fields}

app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})


@scheduler.scheduled_job("interval", seconds=30)
def update_canteen_metrics():
    canteens = canteen_traffic.get()
    for canteen in canteens:
        if canteen.name in canteen_fields:
            canteen_occupied_metrics[canteen.name].set(canteen.occupied)
            canteen_overall_metrics[canteen.name].set(canteen.overall)


@scheduler.scheduled_job("interval", seconds=30)
def update_library_metrics():
    libraries = library_traffic.get()
    for library in libraries:
        if library.name in library_fields:
            library_occupied_metrics[library.name].set(library.occupied)
            library_overall_metrics[library.name].set(library.overall)


scheduler.start()
