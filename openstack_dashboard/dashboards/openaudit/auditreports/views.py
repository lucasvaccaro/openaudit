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
    page_title = 'Snapshot {{ snapshot_id }} @ {{ snapshot_timestamp }}'

    def get_data(self):
        return openaudit_api.fetch_all_issues(self.kwargs["snapshot_id"])

    def get_context_data(self, **kwargs):
        snapshot = openaudit_api.fetch_one(self.kwargs["snapshot_id"])
        context = super(DetailView, self).get_context_data(**kwargs)
        context["snapshot_id"] = self.kwargs["snapshot_id"]
        context["snapshot_timestamp"] = snapshot.timestamp
        return context
