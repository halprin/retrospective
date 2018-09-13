from django.urls import path

from .views import generic_views, views

urlpatterns = [
    path('retro', generic_views.GenericRetroView.as_view(), name='retro'),
    path('retro/<uuid:retro_id>', generic_views.GenericRetroView.as_view(), name='retro_id'),
    path('retro/<uuid:retro_id>/user', generic_views.GenericRetroUserView.as_view(), name='retro_id_user'),
    path('retro/<uuid:retro_id>/issue', views.RetroIssueView.as_view(), name='retro_id_issue'),
    path('retro/<uuid:retro_id>/issue/<uuid:issue_id>', views.RetroIssueView.as_view(), name='retro_id_issue_id'),
    path('health', views.HealthView.as_view(), name='health_check')
]
