from json import JSONEncoder


# https://stackoverflow.com/a/8230505
class SetEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)
