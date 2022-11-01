import csv


# calculate the average of the time delay to give a score
# concordant-discordant

def calc_average(csv_file):
    con_sum = 0.0
    dis_sum = 0.0
    averages = []
    f = open(csv_file)
    csv_f = csv.reader(f)
    count = 0
    for row in csv_f:
        count += 1
        if row[0] == 'type' or count == 96:
            if con_sum != 0.0:
                averages.append(con_sum / 10)
            elif dis_sum != 0.0:
                averages.append(dis_sum / 20)
            con_sum = 0.0
            dis_sum = 0.0
        elif row[0] == 'concordant':
            con_sum = con_sum + float(row[3])
        elif row[0] == 'discordant':
            dis_sum = dis_sum + float(row[3])
    f.close()
    return averages

# def calc_error(csv_file):

def calc_error(csv_file):
    f = open(csv_file)
    error = 0.0
    csv_f = csv.reader(f)
    i = 0
    for row in csv_f:
        if row[7] == "response":
            i += 1
            continue
        elif row[4] != row[7]:
            error += 1
        i += 1
    error_score = error/90 * 100
    f.close()
    return error_score

def score(csv_file):
    average = calc_average(csv_file)
    sesh_score = []
    i = 0
    while i < len(average) - 1:
        dif = average[i + 1] - average[i]
        sesh_score.append(dif)
        i += 2
    return sesh_score

# print(calculate_average('speech.csv'))
# print(score('speech.csv'))

# usage = ''' Average Score Calculator.
#
# Usage:
#     score.py FILE
# '''
#
# args = docopt(usage)
#
# if args['FILE']:
#     scores = score('FILE')
#     for i in range(1, len(scores) + 1):
#         print("Type %d Keyboard:" + scores[i - 1], i)
