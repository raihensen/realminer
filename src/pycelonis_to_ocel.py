from __future__ import annotations

import json

import pandas as pd
from pycelonis import get_celonis
from pycelonis.pql import PQL, PQLColumn, PQLFilter
# from dotenv import load_dotenv, find_dotenv

import json
import os
import pickle
import hashlib

DATA_MODEL_NAME = "accounts_receivable"

ALL_OBJECT_TYPES = {
    "original": ["SalesOrder", "SalesOrderItem", "o_celonis_Delivery", "DeliveryItem", "CustomerInvoice"],
    "accounts_payable": ['PurchaseOrder',
                         'IncomingMaterialDocumentItem',
                         'ReverseVendorInvoiceItem',
                         'VendorInvoiceItem',
                         'VendorAccountCreditItemBlock',
                         'VendorAccountCreditItem',
                         'VendorInvoice',
                         'PurchaseOrderItem',
                         'VendorAccountClearingAssignment',
                         'VendorAccountDebitItem'],
    "accounts_receivable": ['CustomerAccountClearingAssignment',
                            'CustomerAccountCreditItem',
                            'CustomerInvoice',
                            'CustomerAccountDebitItem',
                            'CustomerAccountDebitItemBlocks',
                            'CustomerMasterCreditManagement']
}

ALL_EVENT_TYPES = {
    "accounts_payable": ['PostVendorAccountCreditItem',
                         'PostGoodsReceipt',
                         'ClearVendorCreditMemo',
                         'ChangePurchaseOrderItem',
                         'ChangeVendorInvoice',
                         'ReverseVendorInvoice',
                         'CreateVendorInvoice',
                         'RemovePaymentBlock',
                         'ChangeVendorAccountCreditItem',
                         'SetPaymentBlock',
                         'PostVendorAccountDebitItem',
                         'CreatePurchaseOrderItem',
                         'CreatePurchaseOrderHeader',
                         'ClearVendorInvoice'],
    "accounts_receivable": [
        'CreateDunningNoticesLevel1',
        'SetDunningBlock',
        'CreateDunningNoticesLevel3',
        'RemoveDunningBlock',
        'ChangeCustomerMasterCreditManagement',
        'ChangeCustomerAccountDebitItem',
        'PerformCreditReview',
        'CreateDunningNoticesLevel2']
}

OBJECT_TYPES = ALL_OBJECT_TYPES[DATA_MODEL_NAME]
EVENT_TYPES = ALL_EVENT_TYPES[DATA_MODEL_NAME]

def _make_hash(o: dict) -> str:
    """Make a hash of a dictionary"""
    j = json.dumps(o, sort_keys=True)
    return hashlib.md5(j.encode('utf-8')).hexdigest()


class CacheManager:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        # Read cache index if it exists
        if os.path.exists(os.path.join(cache_dir, 'index.json')):
            with open(os.path.join(cache_dir, 'index.json')) as f:
                self.cache = json.load(f)
        else:
            self.cache = {}

    def load(self, key: str | dict):
        if key not in self:
            raise KeyError(f'Key {key} not found in cache')

        with open(self.get_file_path(key), 'rb') as handle:
            data = pickle.load(handle)
        return data

    def save(self, key: str | dict, value, force=False):
        if key in self and not force:
            raise KeyError(f'Key {key} already exists in cache')
        self[key] = key
        with open(self.get_file_path(key), 'wb') as handle:
            pickle.dump(value, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def delete(self, key: dict):
        if key not in self:
            raise KeyError(f'Key {key} not found in cache')
        del self[key]
        os.remove(self.get_file_path(key))

    def get_file_path(self, key: str | dict, file_ending: str = 'pickle') -> str:
        if isinstance(key, dict):
            key = _make_hash(key)
        return os.path.join(self.cache_dir, f'{key}.{file_ending}')

    def clear(self):
        self.cache = {}
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)

    def __contains__(self, key: str | dict) -> bool:
        if isinstance(key, dict):
            key = _make_hash(key)
        return key in self.cache

    def __getitem__(self, key: str | dict):
        if isinstance(key, dict):
            key = _make_hash(key)
        return self.cache[key]

    def __setitem__(self, key: str | dict, value):
        if isinstance(key, dict):
            key = _make_hash(key)
        self.cache[key] = value
        with open(os.path.join(self.cache_dir, 'index.json'), 'w') as f:
            json.dump(self.cache, f)

    def __delitem__(self, key: str | dict):
        if isinstance(key, dict):
            key = _make_hash(key)
        del self.cache[key]
        with open(os.path.join(self.cache_dir, 'index.json'), 'w') as f:
            json.dump(self.cache, f)


def object_table_to_ocel(object_table, id_col_name, type_name, attribute_col_names_to_attribute_value_keys):
    result = dict()
    attribute_names = list(attribute_col_names_to_attribute_value_keys.keys())
    object_table[attribute_names + [id_col_name]].apply(
        lambda t: result.update({t[-1]: {"ocel:type": type_name,
                                         "ocel:ovmap": {
                                             attribute_col_names_to_attribute_value_keys[
                                                 col_name]: attr for
                                             col_name, attr in
                                             zip(attribute_names,
                                                 t)}}}),
        axis=1)
    return result


def event_table_to_ocel(event_table, id_col_name, timestamp_col_name, activity_name,
                        attribute_col_names_to_attribute_value_keys):
    result = dict()
    attribute_names = list(attribute_col_names_to_attribute_value_keys.keys())
    event_table[attribute_names + [id_col_name, timestamp_col_name]].apply(
        lambda t: result.update({t[-2]: {"ocel:activity": activity_name,
                                         "ocel:timestamp": t[-1],
                                         "ocel:omap": [],  # filled later, with data from the relation table
                                         "ocel:vmap": {attribute_col_names_to_attribute_value_keys[col_name]: attr for
                                                       col_name, attr in zip(attribute_names, t)}}}),
        axis=1)
    return result


def events_to_ocel(events_df: pd.DataFrame,
                   id_col_name: str = 'ID',
                   timestamp_col_name: str = 'Time',
                   activity_col_name: str = 'Type') -> dict:
    result = dict()

    def to_ocel_event(row):
        result.update({row[id_col_name]: {
            "ocel:activity": row[activity_col_name],
            "ocel:timestamp": row[timestamp_col_name],
            "ocel:omap": [],  # filled later, with data from the relation table
            "ocel:vmap": {k: row[k] for k in row.keys() if
                          k not in [id_col_name, timestamp_col_name, activity_col_name]}
        }})

    events_df.apply(to_ocel_event, axis=1)
    return result


def objects_to_ocel(objects_df: pd.DataFrame,
                    id_col_name: str = 'ID',
                    type_col_name: str = 'Type') -> dict:
    result = dict()

    def to_ocel_object(row):
        result.update({row[id_col_name]: {
            "ocel:type": row[type_col_name],
            "ocel:ovmap": {k: row[k] for k in row.keys() if
                           k not in [id_col_name, type_col_name]}
        }})

    objects_df.apply(to_ocel_object, axis=1)
    return result


def add_relationships(rel_table: pd.DataFrame, object_col_name: str, event_col_name: str, object_dict: dict,
                      event_dict: dict):
    def add(t):
        o, e = t
        if e in event_dict:
            omap = event_dict[e]["ocel:omap"]
            if o in object_dict and o not in omap:
                omap.append(o)

    rel_table[[object_col_name, event_col_name]].apply(add, axis=1)


def construct_ocel(events_dict, objects_dict, attributes, object_types):
    return {
        'ocel:global-event': {
            'ocel:activity': '__INVALID__',
        },
        'ocel:global-object': {
            'ocel:type': '__INVALID__',
        },
        'ocel:global-log': {
            'ocel:attribute-names': attributes,
            'ocel:object-types': object_types,
            'ocel:version': '1.0',
            'ocel:ordering': 'timestamp',
        },
        'ocel:events': events_dict,
        'ocel:objects': objects_dict,
    }


def extract_tables():
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    # load_dotenv(find_dotenv())
    #
    # celonis = get_celonis()

    EMS_API_TOKEN_FILE = "../ems_apikey"
    DATA_POOL_ID = "3f9e0c7b-a9d5-4e51-a322-b38e6b10d8b1"
    DATA_MODEL_IDS = {
        "accounts_payable": "77da2001-dcf7-4699-b5d3-ce89dc2234d3",
        "accounts_receivable": "524481f7-ed83-4f3b-8452-a6e7897afacb",
        "inventory_management": "a1cd3a04-fbec-4e6e-9fec-65c2fc79ed77",
        "order_management": "213ab550-b1cf-4abc-ad05-23be6a2fd1b8",
        "procurement": "535e9505-0662-432c-b18a-af07edb6137d"
    }

    celonis = get_celonis(
        base_url="https://pads-x-celonis-group-1.try.celonis.cloud/",
        api_token=open(EMS_API_TOKEN_FILE).read(),
        key_type="APP_KEY"
    )

    datapool = celonis.data_integration.get_data_pool(DATA_POOL_ID)
    # the test data model (copy)
    datamodel = datapool.get_data_model(DATA_MODEL_IDS["accounts_receivable"])
    # the original data model
    # datamodel = datapool.get_data_model('a6f71ae3-ba37-4387-9f9b-5686d7a6e18e')

    cache = CacheManager('cache')

    # === events ===
    if 'events_df' not in cache:
        print('Extracting events...')
        default_event_columns = ["ID", "Type", "Time", "ExecutedBy", "ExecutionType"]
        event_table_names = [
            ("e_celonis_CreateSalesOrderScheduleLine", default_event_columns),
            (
                "e_celonis_ChangeSalesOrderScheduleLine",
                [*default_event_columns, "ChangedAttribute", "OldValue", "NewValue"]),
            ("e_celonis_DeleteSalesOrderScheduleLine", default_event_columns),
            ("e_celonis_PostGoodsIssue", default_event_columns),
            ("e_celonis_ApproveSalesOrderItem", default_event_columns),
            ("e_celonis_ApproveSalesQuotationItem", default_event_columns),
            ("e_celonis_CreateSalesOrder", default_event_columns),
            ("e_celonis_CreateDelivery", default_event_columns),
            ("e_celonis_ClearCustomerInvoice", default_event_columns),
            ("e_celonis_CreateCustomerInvoice", default_event_columns),
            ("e_celonis_ApproveSalesOrder", default_event_columns),
            ("e_celonis_PostCustomerInvoice", default_event_columns),
            ("e_celonis_SendOrderConfirmation", default_event_columns),
            ("e_celonis_ExecutePicking", default_event_columns),
            ("e_celonis_CreateSalesQuotation", default_event_columns),
            ("e_celonis_ChangeSalesOrderItem", [*default_event_columns, "ChangedAttribute", "OldValue", "NewValue"]),
            ("e_celonis_ChangeSalesOrder", [*default_event_columns, "ChangedAttribute", "OldValue", "NewValue"]),
            ("e_celonis_RemoveDeliveryBlock", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_ChangePostedCustomerInvoice", [*default_event_columns, "ChangedAttribute"]),
            ("e_celonis_SetRejectionReason", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_AddSalesOrderItems", default_event_columns),
            ("e_celonis_ReleaseCreditHold", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_SetDunningBlock", [*default_event_columns, "ChangedAttribute"]),
            ("e_celonis_ChangeSalesQuotation", [*default_event_columns, "ChangedAttribute"]),
            ("e_celonis_CancelGoodsIssue", default_event_columns),
            ("e_celonis_CreateDunningNoticesLevel1", default_event_columns),
            ("e_celonis_RemoveBillingBlock", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_PassCredit", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_CancelRejectionReason", default_event_columns),
            ("e_celonis_AddSalesQuotationItems", default_event_columns),
            ("e_celonis_CreateDunningNoticesLevel2", default_event_columns),
            ("e_celonis_AddDeliveryItems", default_event_columns),
            ("e_celonis_SetDeliveryBlock", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_SetBillingBlock", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_CreateDunningNoticesLevel3", default_event_columns),
            ("e_celonis_SetCreditHold", [*default_event_columns, "OldValue", "NewValue"]),
            ("e_celonis_RejectSalesQuotation", default_event_columns),
            ("e_celonis_SplitOutboundDelivery", default_event_columns),
            ("e_celonis_RemoveDunningBlock", [*default_event_columns, "ChangedAttribute"]),
            ("e_celonis_RemoveDunningNotices", default_event_columns),
            ("e_celonis_EnterInvoiceWithoutSalesOrder", default_event_columns),
        ]

        event_tables = []
        for table, cols in event_table_names:
            query = PQL()
            for col in cols:
                query += PQLColumn(query=f'"{table}"."{col}"', name=col)
            event_tables.append(datamodel.export_data_frame(query))
        event_df = pd.concat(event_tables, ignore_index=True)
        event_df = event_df.sort_values(by=["Time"])
        cache.save('events_df', event_df)
        print('Done extracting events and saved to cache.')
    else:
        print('Loading events from cache...')
        event_df = cache.load('events_df')

    # === objects ===
    if 'object_df' not in cache:
        print('Extracting objects...')
        default_object_columns = ["ID", "Type"]
        object_table_names = [(f"o_celonis_{ot}", default_object_columns) for ot in OBJECT_TYPES]

        object_tables = []
        for table, cols in object_table_names:
            query = PQL()
            for col in cols:
                query += PQLColumn(query=f'"{table}"."{col}"', name=col)
            object_tables.append(datamodel.export_data_frame(query))
        object_df = pd.concat(object_tables, ignore_index=True)
        cache.save('object_df', object_df)
        print('Done extracting objects and saved to cache.')
    else:
        print('Loading objects from cache...')
        object_df = cache.load('object_df')

    # === relationships ===
    if 'relationship_table' not in cache:
        print('Extracting relationships...')
        rel_query = PQL()
        for col in ["EventID", "ObjectID", "EventType", "ObjectType"]:
            rel_query += PQLColumn(query=f'"rel_table"."{col}"', name=col)
        relationship_table = datamodel.export_data_frame(rel_query)
        cache.save('relationship_table', relationship_table)
        print('Done extracting relationships and saved to cache.')
    else:
        print('Loading relationships from cache...')
        relationship_table = cache.load('relationship_table')

    return event_df, object_df, relationship_table


def to_json_ocel():
    cache = CacheManager('cache')

    event_df, object_df, relationship_table = extract_tables()

    # === merge ===
    if 'merged' not in cache:
        print('Merging events and objects...')
        events = events_to_ocel(event_df)
        objects = objects_to_ocel(object_df)
        add_relationships(relationship_table,
                          event_col_name='EventID',
                          object_col_name='ObjectID',
                          event_dict=events,
                          object_dict=objects)
        cache.save('merged', (events, objects))
        print('Done merging events and objects and saved to cache.')
    else:
        print('Loading merged events and objects from cache...')
        events, objects = cache.load('merged')

    attribute_names = [a for a in event_df.columns.values.tolist() if a not in ["ID", "Type", "Time"]]
    object_types = object_df["Type"].unique().tolist()

    with open("sales_order_events.json", "w") as f:
        json.dump(construct_ocel(events, objects, attribute_names, object_types), fp=f, default=str)


def to_csv_ocel():
    event_df, object_df, relationship_table = extract_tables()
    object_types = object_df["Type"].unique().tolist()

    print('Calculate the mapping EventId & ObjectType --> ObjectId')
    mapping = relationship_table.groupby(['EventID', 'ObjectType'])['ObjectID'].apply(set)
    print('Unstack to column per object type')
    mapping_by_event = mapping.unstack(level=1, fill_value=set())
    print('Merge with events')
    ocel_df = pd.merge(event_df, mapping_by_event[object_types], left_on='ID', right_index=True)
    print('Saving...')
    ocel_df.to_pickle('dataset.pickle')


if __name__ == '__main__':
    to_csv_ocel()
