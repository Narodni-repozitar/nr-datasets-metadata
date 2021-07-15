from datetime import datetime, date


def convert_dates(x):
    if isinstance(x, datetime):
        return x.isoformat()
    elif isinstance(x, date):
        return str(x)
    elif isinstance(x, dict):
        return {k: convert_dates(v) for k, v in x.items()}
    elif isinstance(x, list) or isinstance(x, tuple):
        return [convert_dates(v) for v in x]
    return x
