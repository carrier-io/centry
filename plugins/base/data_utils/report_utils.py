import random
from datetime import datetime, timezone
from ..constants import str_to_timestamp, MAX_DOTS_ON_CHART


def colors(n):
    try:
        ret = []
        r = int(random.random() * 256)
        g = int(random.random() * 256)
        b = int(random.random() * 256)
        step = 256 / n
        for i in range(n):
            r += step
            g += step
            b += step
            r = int(r) % 256
            g = int(g) % 256
            b = int(b) % 256
            ret.append((r, g, b))
        return ret
    except ZeroDivisionError:
        return [(0, 0, 0)]


def create_dataset(timeline, data, label, axe):
    labels = []
    for _ in timeline:
        labels.append(datetime.strptime(_, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d %H:%M:%S"))
    r, g, b = colors(1)[0]
    return {
        "labels": labels,
        "datasets": [
            {
                "label": label,
                "fill": False,
                "data": list(data.values()),
                "yAxisID": axe,
                "borderWidth": 2,
                "lineTension": 0,
                "spanGaps": True,
                "backgroundColor": f"rgb({r}, {g}, {b})",
                "borderColor": f"rgb({r}, {g}, {b})"
            }
        ]
    }


def comparison_data(timeline, data):
    labels = []
    for _ in timeline:
        labels.append(datetime.strptime(_, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d %H:%M:%S"))
    chart_data = {
        "labels": labels,
        "datasets": [
        ]
    }
    col = colors(len(data.keys()))
    for record in data:
        color = col.pop()
        dataset = {
            "label": record,
            "fill": False,
            "data": list(data[record][0].values()),
            "yAxisID": data[record][1],
            "borderWidth": 2,
            "lineTension": 0,
            "spanGaps": True,
            "backgroundColor": f"rgb({color[0]}, {color[1]}, {color[2]})",
            "borderColor": f"rgb({color[0]}, {color[1]}, {color[2]})"
        }
        chart_data["datasets"].append(dataset)
    return chart_data


def chart_data(timeline, users, other, yAxis="response_time"):
    labels = []
    try:
        for _ in timeline:
            labels.append(datetime.strptime(_, "%Y-%m-%dT%H:%M:%SZ").strftime("%m-%d %H:%M:%S"))
    except:
        labels = timeline
    _data = {
        "labels": labels,
        "datasets": []
    }
    if users:
        _data['datasets'].append({"label": "Active Users", "fill": False,
                                  "data": list(users['users'].values()),
                                  "yAxisID": "active_users",
                                  "borderWidth": 2, "lineTension": 0, "spanGaps": True})
    colors_array = colors(len(other.keys()))
    for each in other:
        color = colors_array.pop()
        dataset = {
            "label": each,
            "fill": False,
            "backgroundColor": f"rgb({color[0]}, {color[1]}, {color[2]})",
            "yAxisID": yAxis,
            "borderWidth": 1,
            "lineTension": 0.2,
            "pointRadius": 1,
            "spanGaps": True,
            "borderColor": f"rgb({color[0]}, {color[1]}, {color[2]})",
            "data": []
        }
        for _ in timeline:
            if str(_) in other[each]:
                dataset['data'].append(other[each][str(_)])
            else:
                dataset['data'].append(None)
        _data['datasets'].append(dataset)
    return _data


def render_analytics_control(requests):
    item = {
        "Users": "getData('Users', '{}')",
        "Hits": "getData('Hits', '{}')",
        "Throughput": "getData('Throughput', '{}')",
        "Errors": "getData('Errors', '{}')",
        "Min": "getData('Min', '{}')",
        "Median": "getData('Median', '{}')",
        "Max": "getData('Max', '{}')",
        "pct90": "getData('pct90', '{}')",
        "pct95": "getData('pct95', '{}')",
        "pct99": "getData('pct99', '{}')",
        "1xx": "getData('1xx', '{}')",
        "2xx": "getData('2xx', '{}')",
        "3xx": "getData('3xx', '{}')",
        "4xx": "getData('4xx', '{}')",
        "5xx": "getData('5xx', '{}')"
    }
    control = {}
    for each in ["All"] + requests:
        control[each] = {}
        for every in item:
            control[each][every] = item[every].format(each)
    return control


def calculate_proper_timeframe(low_value, high_value, start_time, end_time, aggregation, time_as_ts=False):
    start_time = str_to_timestamp(start_time)
    end_time = str_to_timestamp(end_time)
    interval = end_time - start_time
    start_shift = interval * (float(low_value) / 100.0)
    end_shift = interval * (float(high_value) / 100.0)
    end_time = start_time + end_shift
    start_time += start_shift
    real_interval = end_time - start_time
    seconds = real_interval / MAX_DOTS_ON_CHART
    if seconds > 1:
        seconds = int(seconds)
    else:
        seconds = 1
    if aggregation == 'auto':
        aggregation = f'{seconds}s'
    if time_as_ts:
        return int(start_time), int(end_time), aggregation
    return (
        datetime.fromtimestamp(start_time, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        datetime.fromtimestamp(end_time, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        aggregation
    )
