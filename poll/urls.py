from django.urls import path
from . import views

urlpatterns = [
    path('', views.poll_list, name='poll_list'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my-votes/', views.my_votes, name='my_votes'),
    path('poll/<int:poll_id>/', views.poll_detail, name='poll_detail'),
    path('poll/<int:poll_id>/results/', views.poll_results, name='poll_results'),
    path('poll/<int:poll_id>/results/json/', views.poll_results_json, name='poll_results_json'),
    path('poll/<int:poll_id>/export/', views.export_poll_results, name='export_poll_results'),
    path('create-poll/', views.create_poll, name='create_poll'),
    path('manage-polls/', views.manage_polls, name='manage_polls'),
    path('toggle-poll/<int:poll_id>/', views.toggle_poll_status, name='toggle_poll_status'),
]