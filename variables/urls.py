from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('manage_target_year/', views.manage_target_year, name='manage_target_year'),
    path('input_yearly_values/', views.input_yearly_values, name='input_yearly_values'),
    path('variables/', views.variables, name='variables'),
    path('variables/details/<int:id>', views.details, name='details'),
    path('testing/', views.testing, name='testing'),
    path('output/', views.output, name='output'),
    path('output/graph', views.graph, name='graph'),
]