from django.utils.translation import ugettext_lazy as _

from horizon import tables

class DetailAction(tables.LinkAction):
    name = "detail"
    verbose_name = _("Details")
    url = "horizon:openaudit:auditreports:detail"


class SnapshotsTable(tables.DataTable):
    snapshot_id = tables.Column("id", verbose_name=_("Snapshot ID"))
    snapshot_timestamp = tables.Column("timestamp", verbose_name=_("Date & Time"))
    snapshot_issues = tables.Column("issues", verbose_name=_("Issues Found"))
    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super(SnapshotsTable, self).__init__(
            request,
            data=data,
            needs_form_wrapper=needs_form_wrapper,
            **kwargs)

    class Meta:
        name = "snapshotstable"
        verbose_name = _("Snapshots")
        row_actions = (DetailAction,)

class DetailTable(tables.DataTable):
    layer = tables.Column("layer", verbose_name=_("Layer"))
    device = tables.Column("device", verbose_name=_("Device"))
    issue = tables.Column("issue", verbose_name=_("Issue"))
    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super(DetailTable, self).__init__(
            request,
            data=data,
            needs_form_wrapper=needs_form_wrapper,
            **kwargs)

    class Meta:
        name = "detailtable"
        verbose_name = _("Detail")
