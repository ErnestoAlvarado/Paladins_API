from datetime import timedelta, datetime
import json


def time_stamp():
    current_time = datetime.utcnow()
    utc_time = current_time.strftime("%Y%m%d%H%M%S")

    return utc_time


def print_json(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)
