from json import loads, dumps
from uuid import uuid4

from flask import Flask, request, render_template

from kitchen import KitchenService
from status import NEW_ORDER, RECEIVED, COOKING, READY
from donut import Donut

import opentelemetry.ext.http_requests
from opentelemetry import trace, propagators
from opentelemetry.sdk.trace import Tracer
from opentelemetry.ext.wsgi import OpenTelemetryMiddleware
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.sdk.trace.export import SimpleExportSpanProcessor
from opentelemetry.sdk.context.propagation.b3_format import B3Format


# Set the factory to be used to create the tracer
trace.set_preferred_tracer_implementation(lambda T: Tracer())

propagators.set_global_httptextformat(B3Format())

opentelemetry.ext.http_requests.enable(trace.tracer())

tracer = trace.tracer()

tracer.add_span_processor(
    SimpleExportSpanProcessor(ConsoleSpanExporter())
)

app = Flask(__name__)
app.static_folder = 'static'

app.wsgi_app = OpenTelemetryMiddleware(app.wsgi_app)


kitchen_service = KitchenService()


@app.route('/')
def home():

    return render_template('index.html')


@app.route('/order', methods=['POST'])
def order():

    order_id = str(uuid4())

    with tracer.start_span('root_span') as root_span:

        root_span

        from ipdb import set_trace
        set_trace()

        for donut_data in loads(next(request.form.keys()))['donuts']:

            for _ in range(donut_data['quantity']):

                kitchen_service.add_donut(
                    Donut(donut_data['flavor'], order_id)
                )

        return check_status(order_id)


@app.route('/status', methods=['POST'])
def status():

    # The issue is that tracer.get_current_span().parent is not root_span

    from ipdb import set_trace
    set_trace()

    with tracer.start_span('status_span') as status_span:

        status_span

        from ipdb import set_trace
        set_trace()

        return check_status(loads(next(request.form.keys()))['order_id'])


def check_status(order_id):

    order_donuts = []

    for donut in kitchen_service.get_all_donuts():

        if donut.order_id == order_id:

            order_donuts.append(donut)

    estimated_time = 0

    status = READY

    for order_donut in order_donuts:

        status = order_donut.status

        if status == NEW_ORDER:

            estimated_time = estimated_time + 3

        elif status == RECEIVED:

            estimated_time = estimated_time + 2

        elif status == COOKING:

            estimated_time = estimated_time + 1

    return dumps(
        {
            'order_id': order_id,
            'estimated_delivery_time': estimated_time,
            'state': status
        }
    )


if __name__ == "__main__":

    app.run(port=8082)
