from json import loads, dumps
from uuid import uuid4

from flask import Flask, request, render_template

from kitchen import KitchenService
from status import NEW_ORDER, RECEIVED, COOKING, READY
from donut import Donut

from ipdb import set_trace

app = Flask(__name__)
app.static_folder = 'static'


kitchen_service = KitchenService()


@app.route('/')
def home():

    return render_template('index.html')


@app.route('/order', methods=['POST'])
def order():

    set_trace

    order_id = str(uuid4())

    for donut_data in loads(next(request.form.keys()))['donuts']:

        for _ in range(donut_data['quantity']):

            kitchen_service.add_donut(
                Donut(donut_data['flavor'], order_id)
            )

    return check_status(order_id)


@app.route('/status', methods=['POST'])
def status():

    set_trace

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
