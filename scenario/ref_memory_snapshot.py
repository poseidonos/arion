import tracemalloc
import debug.display


def play(tgts, inits, scenario, timestamp, data):
    tracemalloc.start(30)

    str1 = 'line1\n'
    str1 += 'line2\n'
    print(str1)

    snapshot = tracemalloc.take_snapshot()
    debug.display.snapshot_top(snapshot)

    dict1 = {'Obj1': 1554}
    dict1['Obj2'] = 42334
    print(dict1)

    snapshot = tracemalloc.take_snapshot()
    debug.display.snapshot_top(snapshot, 1)

    return data
