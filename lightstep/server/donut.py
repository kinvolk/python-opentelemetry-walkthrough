from status import NEW_ORDER


class Donut(object):

    def __init__(self, flavor, order_id):

        self.flavor = flavor
        self.order_id = order_id
        self.status = NEW_ORDER


__all__ = ['Donut']
