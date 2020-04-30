from csv import reader
from collections import namedtuple, defaultdict
from scipy.stats import linregress
import statistics

#settings
measure = 'max'
stdev_multiplier = -1

print(f"measure: {measure}")
print(f"stdev_multiplier: {stdev_multiplier}")

month_days = {
        1:31,
        2:28,
        3:31,
        4:30,
        5:31,
        6:30,
        7:31,
        8:31,
        9:30,
        10:31,
        11:30,
        12:31,
}

# def get_month_and_day(distance_from_mid_jan):
#     next_month = 1
#     days_in_month = month_days[next_month]
#     while distance_from_mid_jan > days_in_month:
#         distance_from_mid_jan -= days_in_month
#         next_month += 1
#         days_in_month = month_days[next_month]
#     return '/'.join([str(next_month), str(distance_from_mid_jan)])

def get_distance_from_mid_jan(month, day):
    s = sum(month_days[i] for i in range(1, month))
    s += day
    return min(abs(s-15), abs(s-380))

Record = namedtuple('Record', 'station name date tavg tmax tmin')
all_records = []
with open('temperatures.csv', 'r') as temperature_file:
    r = reader(temperature_file)
    next(r)
    for line in r:
        next_record = Record(*line)
        all_records.append(next_record)

def get_measure(record):
    if measure == 'avg':
        return record.tavg
    if measure == 'max':
        return record.tmax
    assert measure == 'min'
    return record.tmin

all_records = [r for r in all_records if r.name and 'cleveland hopkins' in r.name.strip().lower() and get_measure(r)]

temps_by_date = defaultdict(list)
for r in all_records:
    d = r.date
    d = d.split('-')
    d = '/'.join(d[1:])
    m = r.tmin
    if measure == 'avg':
        m = r.tavg
    elif measure == 'max':
        m = r.tmax
    temps_by_date[d].append(float(m))

all_stat_results = []
StatResults = namedtuple('StatResults', 'date avg stdev temp_to_use')
for d, temps in temps_by_date.items():
    avg = statistics.mean(temps)
    stdev = statistics.pstdev(temps)
    temp_to_use = int(round(avg + stdev_multiplier * stdev))
    avg = int(round(avg))
    stdev = round(stdev, 1)
    stat_results = StatResults(d, avg, stdev, temp_to_use)
    all_stat_results.append(stat_results)


x = []
y = []
for sr in all_stat_results:
    month, day = sr.date.split('/')
    month = int(month)
    day = int(day)
    m = sr.temp_to_use
    x.append(m)
    y.append(get_distance_from_mid_jan(month, day))

linregress_result = linregress(y, x)
slope = linregress_result.slope
intercept = linregress_result.intercept
for sr in all_stat_results:
    month, day = sr.date.split('/')
    month = int(month)
    day = int(day)
    dist = get_distance_from_mid_jan(month, day)
    temp = int(round(dist*slope+intercept))
    print(f"{month}-{day}: {temp}")

# for i in range(1, 182):
#     temp = int(round(i*slope+intercept))
#     print(f"{get_month_and_day(i)}: {temp}")
