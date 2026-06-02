from django.urls import path
from . import views

app_name = 'diagosis'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_image, name='upload'),
    path('classify/<int:pk>/', views.classify_image, name='classify'),
    path('dataset/', views.dataset_list, name='dataset'),
]
