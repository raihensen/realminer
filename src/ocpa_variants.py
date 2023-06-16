from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

#import and basuc statistics
filename = "../data/datasets/ocpa_test_data.jsonocel"
ocel = ocel_import_factory.apply(filename)

def get_variants():
    return ocel.variants

def display_variant(id):
    graph = ocel.variant_graphs
    tuple = graph[id]
    g = tuple[0]
    nx.draw_networkx(g)
    plt.show()

#executions
#executions = ocel.process_executions
#print(type(executions))
#print(executions)
#print(type(executions[0]))
#print(executions[0])
#ex_graph = ocel.get_process_execution_graph(executions[0])
#nx.draw_networkx(ex_graph)
#plt.show()
