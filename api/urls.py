from django.urls import path, re_path

from . import views

urlpatterns = [
    path('retro', views.RetroView.as_view(), name='retro'),
    path('retro/<uuid:retro_id>', views.RetroView.as_view(), name='retro_id'),
    path('retro/<uuid:retro_id>/user', views.RetroUserView.as_view(), name='retro_id_user'),
    path('retro/<uuid:retro_id>/issue', views.RetroIssueView.as_view(), name='retro_id_issue'),
    path('retro/<uuid:retro_id>/issue/<uuid:issue_id>', views.RetroIssueView.as_view(), name='retro_id_issue_id'),
    path('health', views.HealthView.as_view(), name='health_check')
]
