import json
import os
from datetime import datetime



def prep_data(reports, data_type, name, length, cutoff):
    data = {}
    if name not in reports[0][data_type]: return False
    if length > len(reports): return False

    start = reports[length - 1]['date']
    end   = reports[0]['date']
    qtrs  = float((end - start).days) / 90

    if qtrs > cutoff or qtrs < length - 2: return False

    for report in reports[:length]:
        date  = report['date']
        days  = (date - datetime(1970, 1, 1)).days
        value = report[data_type][name]

        data[days] = value
    
    return data if len(data) > 0 else False



def avg(data, set):
    s = 0
    n = 0

    for x in data:
        s = s + x if set == 'x' else s + data[x]
        n = n + 1
    
    return float(s) / n



def get_adj_avg(input_data):
    x_avg = avg(input_data, 'x')
    y_avg = avg(input_data, 'y')
    y_sig = sigma(input_data, x_avg, y_avg, 'y')

    hi = y_avg + y_sig * 3
    lo = y_avg - y_sig * 3

    data = {}

    for x in input_data:
        if input_data[x] < hi and input_data[x] > lo: data[x] = input_data[x]

    if len(data) == 0: return 0

    x_avg = avg(data, 'x')
    y_avg = avg(data, 'y')
    y_sig = sigma(data, x_avg, y_avg, 'y')

    if y_avg == 0: return 0

    p_sig = y_sig / abs(y_avg) if y_sig < abs(y_avg) else 1
    n_sig = 1 - p_sig

    return y_avg * (n_sig ** 2)



def covariance(data, x_avg, y_avg):
    s = 0

    for x in data:
        i = x - x_avg
        j = data[x] - y_avg
        s = s + i * j
    
    return s



def variance(data, x_avg):
    s = 0

    for x in data:
        v = x - x_avg
        s = s + v ** 2
    
    return s



def sigma(data, x_avg, y_avg, set):
    values = []
    for x in data:
        values.append(x if set == 'x' else data[x])

    avg = x_avg if set == 'x' else y_avg

    pre_sigma = (sum((z - avg) ** 2 for z in values) / len(values))
    if pre_sigma < 0: return 1
    
    sigma = pre_sigma ** 0.5
    return sigma



def get_trend(input_data):
    x_avg = avg(input_data, 'x')
    y_avg = avg(input_data, 'y')
    y_sig = sigma(input_data, x_avg, y_avg, 'y')

    hi = y_avg + y_sig * 3
    lo = y_avg - y_sig * 3

    data = {}

    for x in input_data:
        if input_data[x] < hi and input_data[x] > lo: data[x] = input_data[x]

    if len(data) == 0: return 0

    x_avg = avg(data, 'x')
    y_avg = avg(data, 'y')

    x_sig = sigma(data, x_avg, y_avg, 'x')
    y_sig = sigma(data, x_avg, y_avg, 'y')

    c = covariance(data, x_avg, y_avg)
    v = variance(data, x_avg)
    m = float(c) / v
    p = float(c) / (x_sig * y_sig) if (x_sig * y_sig != 0) else 1

    trend = float(m) / y_avg if y_avg != 0 else 100
    return trend * (p ** 2)



def load_reports():
    reports = {}

    for filename in os.listdir('reports'):
        cik = int(filename[8:-5])

        with open('reports/' + filename, 'r') as file:
            reports[cik] = json.load(file)
            file.close()

    return reports




def get_reports_by_date(reports):
    output = []
    
    for date in reports:
        dt = datetime.strptime(date, '%Y-%m-%d')
        metrics = reports[date]['metrics']
        ratios  = reports[date]['ratios']
        output.append({ 'date': dt, 'metrics': metrics, 'ratios': ratios })

    output.sort(key = lambda x: x['date'], reverse=True)
    return output



def get_raw_scores(reports):
    scores = {
        'revenue':          { 'trend': None },
        'net_income':       { 'trend': None },
        'long_term_assets': { 'trend': None },
        'equity':           { 'trend': None },
        'profit_margin':    { 'trend': None, 'avg': None },
        'return_on_equity': { 'trend': None, 'avg': None },
        'debt_coverage':    { 'trend': None, 'avg': None },
        'current_leverage': { 'trend': None, 'avg': None },
        'total_leverage':   { 'trend': None, 'avg': None },
    }

    for score in scores:
        data_type = 'metrics' if score in reports[0]['metrics'] else 'ratios'

        if 'trend' in scores[score]:
            data = prep_data(reports, data_type, score, 12, 18)
            scores[score]['trend'] = get_trend(data) if data else False
        
        if 'avg' in scores[score]:
            data = prep_data(reports, data_type, score, 4, 6)
            scores[score]['avg'] = get_adj_avg(data) if data else False

    return scores



def save_raw_scores(reports):
    scores = {}

    for cik in reports:
        reports_by_dt = get_reports_by_date(reports[cik])
        scores[cik]   = get_raw_scores(reports_by_dt)

    with open('scores/raw-scores.json', 'w') as file:
        json.dump(scores, file)
        file.close()



def minify_raw_scores():
    with open('scores/raw-scores.json', 'r') as file:
        scores = json.load(file)
        file.close()

    mini = {}

    for cik in scores:
        for score in scores[cik]:
            if score not in mini: mini[score] = {}

            for data_type in scores[cik][score]:
                if data_type not in mini[score]:
                    mini[score][data_type] = { 'data': [], 'count': 0 }

                val = scores[cik][score][data_type]
                cnt = mini[score][data_type]['count']

                if val: mini[score][data_type]['data'].append(val)
                mini[score][data_type]['count'] = cnt + 1

    with open('scores/raw-scores-mini.json', 'w') as file:
        json.dump(mini, file)
        file.close()



def get_limit(scores):
    scores = list(map(lambda x: x if x > 0 else 0, scores))

    tot = len(scores)
    avg = sum(scores) / tot

    sigma = (sum((x - avg) ** 2 for x in scores) / tot) ** 0.5

    return avg + 2 * sigma



def normalize(value, limit):
    if (not value) or (not limit): return False

    norm = value * (100 / limit)

    if norm < 0:   norm = 0
    if norm > 100: norm = 100
    return norm



def save_score_limits():
    with open('scores/raw-scores-mini.json', 'r') as file:
        scores = json.load(file)
        file.close()

    limits = {}
    for score in scores:
        limits[score] = {}

        for data_type in scores[score]:
            data  = scores[score][data_type]['data']
            limit = get_limit(data) if data and len(data) > 0 else False

            limits[score][data_type] = limit

    with open('scores/score-limits.json', 'w') as file:
        json.dump(limits, file)
        file.close()



def normalize_scores():
    with open('scores/raw-scores.json', 'r') as file:
        scores = json.load(file)
        file.close()

    with open('scores/score-limits.json', 'r') as file:
        limits = json.load(file)
        file.close()

    normalized = {}

    for cik in scores:
        normalized[cik] = {}
        
        for score in scores[cik]:
            normalized[cik][score] = {}
            
            for data_type in scores[cik][score]:
                value = scores[cik][score][data_type]
                limit = limits[score][data_type]

                normalized[cik][score][data_type] = normalize(value, limit)

    with open('scores/normalized-scores.json', 'w') as file:
        json.dump(normalized, file)
        file.close()



def get_weight(data_type, score):
    weights = {
        'avg': {
            'wt': 0.35,
            'components': {
                'efficiency': {
                    'wt': 0.5,
                    'components': {
                        'profit_margin':    0.6,
                        'return_on_equity': 0.4
                    }
                },
                'debt': {
                    'wt': 0.5,
                    'components': {
                        'debt_coverage':    0.3,
                        'current_leverage': 0.5,
                        'total_leverage':   0.2
                    }
                }
            }
        },
        'trend': {
            'wt': 0.65,
            'components': {
                'growth': {
                    'wt': 0.4,
                    'components': {
                        'revenue':          0.4,
                        'long_term_assets': 0.2,
                        'equity':           0.4
                    }
                },
                'efficiency': {
                    'wt': 0.3,
                    'components': {
                        'net_income':       0.4,
                        'profit_margin':    0.3,
                        'return_on_equity': 0.3
                    }
                },
                'debt': {
                    'wt': 0.3,
                    'components': {
                        'debt_coverage':    0.3,
                        'current_leverage': 0.5,
                        'total_leverage':   0.2
                    }
                }
            }
        }
    }

    weight = weights[data_type]['wt']

    for category in weights[data_type]['components']:
        if score in weights[data_type]['components'][category]['components']:
            weight = weight * weights[data_type]['components'][category]['wt']
            weight = weight * weights[data_type]['components'][category]['components'][score]

    return weight



def get_value_scores():
    with open('scores/normalized-scores.json', 'r') as file:
        scores = json.load(file)
        file.close()

    out = {}

    for cik in scores:
        total = 0
        fail  = False

        for score in scores[cik]:
            for data_type in scores[cik][score]:
                value  = scores[cik][score][data_type]
                weight = get_weight(data_type, score)
                total  = total + value * weight

                if value == 0: fail = True
        
        if not fail: out[cik] = total

    with open('scores/value-scores.json', 'w') as file:
        json.dump(out, file)
        file.close()



reports = load_reports()
save_raw_scores(reports)

minify_raw_scores()
save_score_limits()
normalize_scores()
get_value_scores()
