from django.urls import path
from . import views

urlpatterns = [
    path('', views.gamepanel, name="gamepanel"),
    path('gp-login/', views.gp_login, name='gp-login'),
    path('gp-register/', views.gp_register, name='gp-register'),
    path('gp-servers/', views.gp_servers, name='gp-servers'),
    path('gp-support/', views.gp_support, name='gp-support'),
    path('gp-support/<int:ticket_id>/', views.ticket_details, name='ticket_details'),
    path('gp-user/', views.gp_user, name='gp-user'),
    
    path('logout/', views.user_logout, name='user_logout'),

    path('agp-home/', views.agp_home, name='agp-home'),
    path('agp-servers/', views.agp_servers, name='agp-servers'),
    path('agp-clients/', views.agp_clients, name='agp-clients'),
    
    path('agp-machines/', views.agp_machines, name='agp-machines'),
    path('agp-machines/<int:machine_id>/', views.agp_machines_detail, name='agp-machines-detail'),
    
    path('agp-support/', views.agp_support, name='agp-support'),
    path('agp-webftp/', views.agp_webftp, name='agp-webftp'),

    path('cs/<int:server_id>/', views.cs_overview, name='cs-overview'),
    path('cs/configure-server/<int:server_id>/', views.cs_configure, name='cs_configure'),

    

    path('cs/webftp/<int:server_id>/', views.cs_webftp, name='cs-webftp'),
    path('cs/webftp/<int:server_id>/<path:current_dir>/', views.cs_webftp, name='cs_webftp'),
    path('cs/fetch_file_content/<int:server_id>/<path:file_path>/', views.fetch_file_content, name='fetch_file_content'),
    path('cs/edit_file/<int:server_id>/<path:file_path>/', views.edit_file, name='edit_file'),
    path('cs/edit_files/<int:server_id>/<path:file_path>/', views.edit_files, name='edit_files'),
    path('cs/edit_admins/<int:server_id>/<path:file_path>/', views.edit_admins, name='edit_admins'),
    path('cs/edit_plugins/<int:server_id>/<path:file_path>/', views.edit_plugins, name='edit_plugins'),
    path('cs/get_server_info/<str:ip_port>/', views.get_server_info, name='get_server_info'),

    path('cs/console/<int:server_id>/', views.cs_console, name='cs-console'),
    path('cs/admins/<int:server_id>/', views.cs_admins, name='cs-admins'),
    path('cs/mods/<int:server_id>/', views.cs_mods, name='cs-mods'),
    path('cs/plugins/<int:server_id>/', views.cs_plugins, name='cs-plugins'),
    path('cs/backup/<int:server_id>/', views.cs_backup, name='cs-backup'),
    path('cs/boost/<int:server_id>/', views.cs_boost, name='cs-boost'),
    
    path('update_server_mod/<int:server_id>/', views.update_server_mod, name='update_server_mod'),
    path('cs/pokreni_server/<int:server_id>/', views.pokreni_server, name='pokreni_server'),
    path('cs/stopiraj_server/<int:server_id>/', views.stopiraj_server, name='stopiraj_server'),
    path('cs/restartuj_server/<int:server_id>/', views.restartuj_server, name='restartuj_server'),
    path('cs/factory_restart_server/<int:server_id>/', views.factory_restart_server, name='factory_restart_server'),
    path('cs/instaliraj_plugin/<int:server_id>/<int:plugin_id>/', views.instaliraj_plugin, name='instaliraj_plugin'),
    

]
