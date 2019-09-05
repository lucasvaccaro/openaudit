from django.conf.urls import url

from openstack_dashboard.dashboards.openaudit.auditreports import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
]