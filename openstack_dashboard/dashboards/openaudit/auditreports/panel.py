from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.openaudit import dashboard

class AuditReportsPanel(horizon.Panel):
    name = _("Reports")
    slug = "auditreports"


dashboard.OpenAuditDashboard.register(AuditReportsPanel)
