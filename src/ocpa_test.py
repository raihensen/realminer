
import pandas as pd
from ocpa.objects.log.importer.ocel import factory as ocel_import_factory
from ocpa.algo.util.process_executions.factory import CONN_COMP, LEAD_TYPE
from ocpa.algo.util.variants.factory import ONE_PHASE, TWO_PHASE
from pathlib import Path

# example dataset from celonis
DATASET_CELONIS = "celonis"

# from https://ocel-standard.org
DATASET_GITHUB = "github_pm4py.jsonocel"
DATASET_O2C = "o2c.jsonocel" # SAP
DATASET_P2P = "p2p.jsonocel" # SAP
DATASET_TRANSFER = "transfer_order.jsonocel" # SAP
DATASET_RECRUITING = "recruiting.jsonocel"
DATASET_ORDER = "running-example.jsonocel"
DATASET_WINDOWS = "windows_events.jsonocel"

ocel_standard_datasets = [DATASET_GITHUB, DATASET_O2C, DATASET_P2P, DATASET_TRANSFER, DATASET_RECRUITING, DATASET_ORDER, DATASET_WINDOWS]

filename = Path("../data/datasets") / DATASET_WINDOWS
ocel = ocel_import_factory.apply(filename, parameters={"execution_extraction": LEAD_TYPE,
                                                       "leading_type": "case:concept:name",
                                                       "variant_calculation": TWO_PHASE,
                                                       "exact_variant_calculation": False})

# https://ocpa.readthedocs.io/en/latest/eventlogmanagement.html
num_exec = len(ocel.process_executions)

print(f"Object types: {ocel.object_types}")
print(f"Number of process executions: {num_exec}")
print(f"Events of the first process execution: {ocel.process_executions[0]}")
print(f"Objects of the first process execution: {ocel.process_execution_objects[0]}")
print(f"Process execution graph of the first execution: {ocel.get_process_execution_graph(0)}")
print(f"Process execution of the first event with event id 0: {ocel.process_execution_mappings[0]}")

exec_info = pd.DataFrame([{"index": i, **{f"num_{ot}": len([obj for t, obj in objects if t == ot]) for ot in ocel.object_types}} for i, objects in enumerate(ocel.process_execution_objects)])
print(exec_info)
print(exec_info.describe())
