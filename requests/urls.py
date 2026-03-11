from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/create/', views.request_create, name='request_create'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('requests/<int:pk>/update/', views.request_update, name='request_update'),
    path('requests/<int:pk>/delete/', views.request_delete, name='request_delete'),
    path('requests/<int:pk>/assign/', views.assign_master, name='assign_master'),
    path('requests/<int:pk>/extend/', views.extend_deadline, name='extend_deadline'),
    path('requests/<int:pk>/approve/', views.approve_extension, name='approve_extension'),
    path('requests/<int:pk>/qr/', views.generate_qr, name='generate_qr'),
]