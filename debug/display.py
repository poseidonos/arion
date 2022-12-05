import tracemalloc


def snapshot_top(snapshot, limit=10):
    snapshot = snapshot.filter_traces((
        tracemalloc.Filter(False, "<frozen importlib._bootstrap_external>"),
        tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
        tracemalloc.Filter(False, "<unknown>"),
    ))
    top_stats = snapshot.statistics('traceback')

    print("-------------------- Tracemalloc Snapshot(s) --------------------")
    print("Top %s point(s)" % limit)
    for index, stat in enumerate(top_stats[:limit], 1):
        print("#%s: %.1f KiB" % (index, stat.size / 1024))
        for line in stat.traceback.format():
            print(line)

    other = top_stats[limit:]
    if other:
        size = sum(stat.size for stat in other)
        print("%s other: %.1f KiB" % (len(other), size / 1024))
    total = sum(stat.size for stat in top_stats)
    print("Total allocated size: %.1f KiB" % (total / 1024))
    print("-----------------------------------------------------------------")
