from json import JSONEncoder
from pint import Quantity
from decimal import Decimal


# https://stackoverflow.com/a/8230505
class MyEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Quantity):
            return {"magnitude": obj.magnitude, "units": str(obj.units)}
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            return JSONEncoder.default(self, obj)
