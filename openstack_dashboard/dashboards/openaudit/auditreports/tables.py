from django.utils.translation import ugettext_lazy as _

from horizon import tables

class SnapshotsTable(tables.DataTable):
    snapshot_id = tables.Column("id", verbose_name=_("ID"))
    snapshot_timestamp = tables.Column('timestamp', verbose_name=_("Data/Hora"))
    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super(SnapshotsTable, self).__init__(
            request,
            data=data,
            needs_form_wrapper=needs_form_wrapper,
            **kwargs)

    class Meta:
        name = "snapshotstable"
        verbose_name = _("Snapshots")
