from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

#import and basuc statistics
filename = "../data/datasets/ocpa_test_data.jsonocel"
ocel = ocel_import_factory.apply(filename)

def get_variants():
    frequencies = ocel.variant_frequencies
    variants = ocel.variants
    pairs = dict(zip(variants, frequencies))
    sorted_pairs = dict(sorted(pairs.items(), key=lambda item: item[1]))
    string_list = []
    count=0
    for i in sorted_pairs.keys():
        count=count+1
        string_list.append("Variant "+ str(count)+ " with frequency: "+ str(sorted_pairs[i]))
    return_dict = dict(zip(string_list, sorted_pairs.keys()))
    #print(string_list)
    #print(return_dict)
    return return_dict

def display_variant(id):
    graph = ocel.variant_graphs
    tuple = graph[id]
    g = tuple[0]
    nx.draw_networkx(g)
    plt.show()

def get_basic_stats():
    return (len(ocel.process_executions), len(ocel.variants))

#executions
#executions = ocel.process_executions
#print(type(executions))
#print(executions)
#print(type(executions[0]))
#print(executions[0])
#ex_graph = ocel.get_process_execution_graph(executions[0])
#nx.draw_networkx(ex_graph)
#plt.show()
