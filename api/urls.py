from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('start_cs16_server/<int:server_id>/', views.startCS16Server, name='start_cs16_server'),
    path('stop_cs16_server/<int:server_id>/', views.stopCS16Server, name='stop_cs16_server'),
    path('server_info/<int:server_id>/', views.server_info, name='server_info'),
    path('delete_cs16__server/<int:server_id>/', views.delete_cs16__server, name='delete_cs16__server'),
    path('rcon_connection_view/<int:server_id>/', views.rcon_connection_view, name='rcon_connection_view'),
    path('send_rcon_cs16_server/<int:server_id>/<str:rcon_command>/', views.send_rcon_cs16_server, name='send_rcon_cs16_server'),
    path('create_cs16_server/<int:server_id>/', views.create_cs16_server, name='create_cs16_server'),
    path('install_plugin_cs16/<int:server_id>/<int:plugin_id>', views.install_plugin_cs16, name='install_plugin_cs16'),
   
   
    path('factoryreset_cs16_server/<int:server_id>/', views.factoryreset_cs16_server, name='factoryreset_cs16_server'),
]


