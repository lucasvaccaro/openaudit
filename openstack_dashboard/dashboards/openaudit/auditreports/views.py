from horizon import tables
from horizon import tabs

from openstack_dashboard.api import openaudit as openaudit_api
from openstack_dashboard.dashboards.openaudit.auditreports import tables as auditreports_table

class IndexView(tables.DataTableView):  
    table_class = auditreports_table.SnapshotsTable
    template_name = 'openaudit/auditreports/index.html'

    def get_data(self):
        return openaudit_api.fetch_all()

class DetailView(tables.DataTableView):
    table_class = auditreports_table.DetailTable
    template_name = 'openaudit/auditreports/detail.html'

    def get_data(self):
        return None
