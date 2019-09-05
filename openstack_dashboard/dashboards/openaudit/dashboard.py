from django.utils.translation import ugettext_lazy as _

import horizon

class AuditGroup(horizon.PanelGroup):
    slug = "auditgroup"
    name = _("Audit")
    panels = ('auditreports',)

class OpenAuditDashboard(horizon.Dashboard):
    name = _("OpenAudit")
    slug = "openaudit"
    panels = (AuditGroup,)
    default_panel = 'auditreports'

horizon.register(OpenAuditDashboard)
