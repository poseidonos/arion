import graph
import iogen
import json
import lib
import node
import traceback


def play(json_targets, json_inits, json_scenario, timestamp, data):
    node_manager = node.NodeManager(json_targets, json_inits)
    targets, initiators = node_manager.initialize()

    graph_fio = graph.manager.Fio(
        json_scenario["OUTPUT_DIR"], timestamp, __name__)

    data["NodeManager"] = node_manager
    data["Targets"] = targets
    data["Initiators"] = initiators
    data["GraphFio"] = graph_fio

    return data
