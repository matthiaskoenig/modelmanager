from django.conf.urls import url

from simapp import views
from simapp.reports import sbml_report

urlpatterns = [
    url(r'^models/$', views.models, name='models'),
    url(r'^model/(?P<model_id>\d+)$', views.model, name='model'),
    url(r'^cores/$', views.cores, name='cores'),
    url(r'^simulations/(?P<status>\w+)$', views.simulations, name='simulations'),
    url(r'^simulations/$', views.simulations, name='simulations'),
    url(r'^simulation/(?P<simulation_id>\d+)$', views.simulation, name='simulation'),
    
    url(r'^report/(?P<model_pk>\d+)$', sbml_report.report, name='report'),
    
    url(r'^methods/$', views.methods, name='methods'),
    url(r'^method/(?P<method_id>\d+)$', views.method, name='method'),

    url(r'^results/$', views.results, name='results'),

    url(r'^tasks/$', views.tasks, name='tasks'),
    url(r'^task/(?P<task_id>\d+)$', views.task, name='task'),
    url(r'^task/T(?P<task_id>\d+)$', views.task_report, name='task_parameters'),
    url(r'^task/C(?P<task_id>\d+)$', views.task_report_csv, name='task_report_csv'),

    url(r'^about/$', views.about, name='about'),

    url(r'^$', views.models, name='index'),
]
