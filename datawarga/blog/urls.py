from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('halaman1/', views.halaman1, name='halaman1'),
    path('halaman2/', views.halaman2, name='halaman2'),
    path('data-warga/', views.halaman2, name='halaman2'),
    path('warga/<int:id>/', views.detail_warga, name='detail_warga'),
]