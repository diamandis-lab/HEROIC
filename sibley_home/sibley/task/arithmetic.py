from psychopy import visual, core, event
from sibley.task.media import show_text


query_0 = ['100 + 11', '95 + 6', '1 + 100', '105 + 6', '91 + 10',
           '99 + 2', '90 + 11', '109 + 2', '1 + 110', '102 + 9',
           '98 + 3', '5 + 96', '100 + 1', '106 + 5', '81 + 20']
query_0_n1 = [100, 95,   1, 105, 91, 99, 90, 109,   1, 102, 98,  5, 100, 106, 81]
query_0_n2 = [11,   6, 100,   6, 10,  2, 11,   2, 110,   9,  3, 96,   1,   5, 20]


duration = 5

mywin = visual.Window([1600, 900], monitor="testMonitor", units="deg", fullscr=True, color=[-1, -1, -1])
for s in range(len(query_0_n1)):
    str_operation = str(query_0_n1[s]) + ' + ' + str(query_0_n2[s]) + ' = ?'
    show_text(mywin, str_operation, duration, height=4, wrap_width=32)

mywin.close()


