import json
from typing import Any


class ComplexEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, 'makeJSON'):
            return o.makeJSON()
        else:
            return json.JSONEncoder.default(self, o)
