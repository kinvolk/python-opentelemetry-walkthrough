from json import loads, dumps
from uuid import uuid4

from flask import Flask, request, render_template

import opentelemetry.ext.http_requests
from opentelemetry import trace, propagators
from opentelemetry.sdk.trace import Tracer
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware
from opentelemetry.ext.http_requests import enable
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor
from opentelemetry.sdk.context.propagation.b3_format import B3Format

from kitchen_service import KitchenService
from kitchen_consumer import KitchenConsumer
from donut import Donut
from status import NEW_ORDER


trace.set_preferred_tracer_implementation(lambda T: Tracer())

propagators.set_global_httptextformat(B3Format())

opentelemetry.ext.http_requests.enable(trace.tracer())

tracer = trace.tracer()

enable(tracer)

tracer.add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

app = Flask(__name__)
app.static_folder = 'static'

app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)


kitchen_service = KitchenService()
kitchen_consumer = KitchenConsumer()


@app.route('/')
def home():

    return render_template('index.html')


@app.route('/order', methods=['POST'])
def order():

    order_id = str(uuid4())

    with tracer.start_span('root_span'):

        for donut_data in loads(next(request.form.keys()))['donuts']:

            for _ in range(donut_data['quantity']):

                kitchen_consumer.add_donut(donut_data, order_id)

        return kitchen_consumer.check_status(order_id)


@app.route('/status', methods=['POST'])
def status():

    with tracer.start_span('status_span'):

        return kitchen_consumer.check_status(
            loads(next(request.form.keys()))['order_id']
        )


@app.route('/kitchen/add_donut', methods=['POST'])
def add_donut(*args, **kwargs):

    kitchen_service.add_donut(
        Donut(
            request.form['flavor'],
            request.form['order_id'],
            NEW_ORDER
        )
    )


@app.route('/kitchen/get_donuts', methods=['GET'])
def get_donuts():

    return dumps(
        [
            {
                'flavor': donut.flavor,
                'order_id': donut.order_id,
                'status': donut.status
            } for donut in kitchen_service.get_all_donuts()
        ]
    )


if __name__ == "__main__":

    app.run(port=8082)