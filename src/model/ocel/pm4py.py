import pm4py
import logging
import seaborn as sns
import pandas as pd

from ocpa.objects.log.ocel import OCEL as Pm4pyEventLogObject
from model.ocel.base import OCEL
from pathlib import Path

logger = logging.getLogger("app_logger")


class Pm4pyEventLog(OCEL):
    """
    Event log wrapper using the pm4py module
    """

    ocel: Pm4pyEventLogObject
    filtered_ocel: Pm4pyEventLogObject

    def __init__(self, dataset, **kwargs):
        super().__init__(ocel_type="pm4py", **kwargs)

        filename = str(Path("../data/datasets") / dataset)
        logger.info(f"Importing dataset {filename}")

        # https://pm4py.fit.fraunhofer.de/documentation#object-centric-event-logs
        self.ocel = pm4py.read_ocel(filename)
        self.filtered_ocel = self.ocel
        self.active_ot = pm4py.ocel.ocel_get_object_types(self.ocel)
        self.active_activities = self._get_activities()

    def _get_object_types(self):
        return pm4py.ocel.ocel_get_object_types(self.filtered_ocel)

    def _get_object_type_counts(self):
        ot = self.ocel.objects['ocel:type']
        return ot.value_counts().to_dict()

    def _get_activities(self):
        ot_activity_dict = pm4py.ocel.ocel_object_type_activities(self.filtered_ocel)
        activities = set()
        for ot in ot_activity_dict:
            for activity in ot_activity_dict[ot]:
                activities.add(activity)
        return activities

    def _get_cases(self):
        return []

    def _get_variants(self):
        return {}

    def _discover_petri_net(self):
        logger.info("Beggining the discovery of a petri net using pm4py")
        ocpn = pm4py.discover_oc_petri_net(self.filtered_ocel)
        filename = 'static/img/ocpn.png'
        pm4py.save_vis_ocpn(ocpn, filename)
        logger.info(f"Petri net saved to {filename}")
        return ocpn
    
    def _computeHeatMap(self):
        df = self.filtered_ocel.relations
        collect = pd.DataFrame([],index=[],columns=['Events'])
        #print(collect)

        for x in set(df.loc[:,'ocel:type']):
            tmp = df.loc[lambda df: df['ocel:type'] == x]
            #print(tmp.loc[:,'ocel:eid'].tolist())
            tmp_list = tmp.loc[:,'ocel:eid'].tolist()
            tmp_df = pd.DataFrame([[tmp_list]], index=[x], columns=['Events'])
            collect = pd.concat([collect,tmp_df])
    
        #print(collect)
        matrix = pd.DataFrame([],index=[collect.index],columns=[collect.index])
        #print(matrix)
        eventlists = collect.loc[:,'Events'].tolist()

        for x in range(len(eventlists)):
            for y in range(x,len(eventlists)):
                if (x==y):
                    events = list(dict.fromkeys(eventlists[x]))
                    matrix.iloc[x,x]=events
                else:
                    events = [value for value in eventlists[x] if value in eventlists[y]]
                    matrix.iloc[x,y]=events
                    matrix.iloc[y,x]=events

        #print(matrix) 
        number_matrix = matrix
        number_matrix = number_matrix.applymap(lambda x: len(x))
        #print(number_matrix)
        heatmap = sns.heatmap(number_matrix, cmap="crest")
        figure = heatmap.get_figure()    
        figure.savefig('static/img/heatmap.png', dpi=400)
        logger.info("saved heatmap as png")
        return number_matrix 

    def filter_ocel_by_active_ot(self):
        # TODO: Once we add filtering by activities it will require an additional adjustment
        self.filtered_ocel = pm4py.filter_ocel_object_types(self.ocel, self.active_ot)

    def filter_ocel_by_ot_and_active_activities(self):
        ot_activity_dict = pm4py.ocel.ocel_object_type_activities(self.ocel)
        
        # example for desired dictionary: {“order”: [“Create Order”], “element”: [“Create Order”, “Create Delivery”]}
        active_ot_activity_filter_dict = {}
        for ot in self.active_ot:
            active_ot_activity_filter_dict[ot] = []
            for activity in self.active_activities:
                if activity in ot_activity_dict[ot]:
                    active_ot_activity_filter_dict[ot].append(activity)
        
        self.filtered_ocel =  pm4py.filter_ocel_object_types_allowed_activities(self.ocel, active_ot_activity_filter_dict)


    def export_json_ocel(self, target_path):
        pm4py.objects.ocel.exporter.jsonocel.exporter.apply(self.filtered_ocel, target_path)
