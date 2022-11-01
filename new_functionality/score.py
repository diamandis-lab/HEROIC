from average_score import *
from docopt import docopt
doc = ''' Average Score Calculator.

Usage: 
    score.py <file>

# Options:
    # -h --help 
    
Score Meaning:
Average Score: Average change in Reaction time between concordant and discordant blocks (in milliseconds)
                - Score should not exceed 1000
Error Score: Percentage of mistakes made over total number of questions, out of 90
'''



args = docopt(doc)

if args['<file>']:
    session = args['<file>']
    scores = score(session)
    print("Average Score")
    for i in range(1, len(scores) + 1):
        score = scores[i - 1]*1000
        print("Type %d Keyboard: %.2f" % (i, score))
    error = calc_error(session)
    print("Error Score")
    print("Out of 90: %.2f %%" % error)

#python score.py speech2.csv
