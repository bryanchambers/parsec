import json
import os
from datetime import datetime




def reorg_reports():
    reports = {}

    for year in range(2010, 2020):
        for qtr in range(1, 5):
            filename = 'index-' + str(year) + 'q' + str(qtr) + '.json'

            try:
                with open('index/' + filename, 'r') as file:
                    index = json.load(file)
                    file.close()

            except FileNotFoundError: index = False

            if index:
                for cik in index:
                    date = index[cik]['date']

                    if 'ratios' in index[cik] and index[cik]['ratios']:
                        if cik not in reports:
                            filename = 'reports-' + str(cik) + '.json'
                            
                            try:
                                with open('reports/' + filename, 'r') as file:
                                    reports[cik] = json.load(file)
                                    file.close()
                            
                            except FileNotFoundError: reports[cik] = {}

                        reports[cik][date] = { 'metrics': add_special_metrics(index[cik]['metrics']), 'ratios': index[cik]['ratios'] }


    for cik in reports:
        filename = 'reports-' + str(cik) + '.json'

        with open('reports/' + filename, 'w') as file:
            json.dump(reports[cik], file)
            file.close()






def get_companies():
    companies = {}

    for year in range(2010, 2020):
        for qtr in range(1, 5):
            filename = 'index-' + str(year) + 'q' + str(qtr) + '.json'

            try:
                with open('index/' + filename, 'r') as file:
                    index = json.load(file)
                    file.close()

            except FileNotFoundError: index = False

            if index:
                for cik in index:
                    if cik not in companies:
                        companies[cik] = { 'name': index[cik]['name'] } 

    with open('info/companies.json', 'w') as file:
        json.dump(companies, file)
        file.close()






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




def add_special_metrics(metrics):
    tot_equity = metrics['total_equity']
    tot_assets = metrics['total_assets']
    cur_assets = metrics['current_assets']
    tot_liabilities = metrics['total_liabilities']

    metrics['equity'] =  tot_equity if tot_equity else tot_assets - tot_liabilities
    metrics['long_term_assets'] = tot_assets - cur_assets
    return metrics






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




def recommend():
    with open('scores/value-scores.json', 'r') as file:
        scores = json.load(file)
        file.close()

    score_list = []

    for cik in scores:
        score_list.append({ 'cik': cik, 'score': scores[cik] })

    score_list.sort(key = lambda x: x['score'], reverse=True)
    
    for x in score_list[:1000]:
        print(str(x['cik']).rjust(8) + ' : ' + str(round(x['score'], 1)))
    
    cik = score_list[0]['cik']
    print_report_data(cik)
    print_scores('raw-scores', cik)
    print_scores('normalized-scores', cik)






def print_report_data(cik):
    print('\nCIK: ' + str(cik))

    with open('reports/reports-1494162.json', 'r') as file:
        reports = json.load(file)
        file.close()

    reports_by_date = get_reports_by_date(reports)

    header = '|    date    | '
    for metric in reports_by_date[0]['metrics']:
        header = header + metric.replace('_', '')[:9].rjust(9) + ' | '

    for ratio in reports_by_date[0]['ratios']:
        header = header + ratio.replace('_', '')[:9].rjust(9) + ' | '

    print('-' * 194)
    print(header)
    print('-' * 194)

    for report in reports_by_date:
        out = '| ' + report['date'].strftime('%Y-%m-%d') + ' | '

        for metric in report['metrics']:
            out = out + str(report['metrics'][metric]).rjust(9) + ' | '

        for ratio in report['ratios']:
            out = out + str(report['ratios'][ratio]).rjust(9) + ' | '
        
        print(out)

    print('-' * 194)


def print_scores(filename, cik):
    with open('scores/' + filename + '.json', 'r') as file:
        scores = json.load(file)
        file.close()

    print('')

    len_trend = 0
    for metric in scores[cik]:
        val = scores[cik][metric]['trend']
        txt = str(round(val, 2))
        if len(txt) > len_trend: len_trend = len(txt)

    len_avg = 0
    for metric in scores[cik]:
        val = scores[cik][metric]['avg'] if 'avg' in scores[cik][metric] else 0
        txt = str(round(val, 2))
        if len(txt) > len_avg: len_avg = len(txt)
    
    if len_trend < 5: len_trend = 5
    if len_avg   < 5: len_avg   = 5

    print('-' * (28 + len_trend + len_avg))
    print('metric'.rjust(20) + ' | ' + 'trend'.rjust(len_trend) + ' | ' + 'avg'.rjust(len_avg) + ' |')
    print('-' * (28 + len_trend + len_avg))

    for metric in scores[cik]:
        out   = metric.rjust(20) + ' | '
        score = scores[cik][metric]

        out = out + str(round(score['trend'], 2)).rjust(len_trend) if 'trend' in score else out + ' ' * len_trend
        out = out + ' | '
        
        out = out + str(round(score['avg'], 2)).rjust(len_avg) if 'avg' in score else out + ' ' * len_avg
        out = out + ' |'
        
        print(out)
    
    print('-' * (28 + len_trend + len_avg))
    print('')





reorg_reports()
print('Reported reorganized')
get_companies()
print('Saved company list')

reports = load_reports()
save_raw_scores(reports)
print('Saved raw scores')

minify_raw_scores()
print('Minified scores')

save_score_limits()
print('Saved score limits')

normalize_scores()
print('Normalized scores')

get_value_scores()
print('Saved value scores')

#recommend()



# with open('index/companies.json', 'r') as file:
#     companies = json.load(file)
#     file.close()

# for cik in companies:
#     print(companies[cik]['name'])