import ttkbootstrap as ttk
import logging
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from controller.export import Export


logger = logging.getLogger("app_logger")


class TableViewWidget:
    def __init__(self, master, controller, model, **kwargs):
        logger.info("Setting up table ...")

        self.controller = controller
        self.model = model
        self.master = master
        self.ocel_df = model.extended_table

        self.dv = Tableview(
            master=self.master,
            paginated=True,
            searchable=True,
            bootstyle=PRIMARY,
            autofit=True,
            pagesize=30,
        )
        self.dv.pack(fill=BOTH, expand=YES, padx=10, pady=10) # Tableview is placed
        logger.info("Table setup complete")

        self.update_table()

    def get_columns(self):
        logger.info("Getting columns to present in the table...")
        column_names = self.ocel_df.columns
        columns = [{"text": column_name} for column_name in column_names]
        return columns

    def get_rows(self):
        rows = [tuple(row) for row in self.ocel_df.values]
        return rows

    def update_table(self):
        logger.info("Updating table according to update ocel...")
        self.ocel_df = self.model.extended_table

        self.controller.current_export = Export("event_log", "jsonocel",
                                                write_to_path=self.controller.model.export_json_ocel,
                                                use_dialog=True)
        columns = self.get_columns()
        row_data = self.get_rows()

        self.dv.build_table_data(columns, row_data)
        self.dv.autofit_columns()
        self.dv.load_table_data()
        logger.info("Table Update complete")
