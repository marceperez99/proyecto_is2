from django.urls import path
from . import views
urlpatterns = [
    path('tipo_de_item/', views.tipo_de_item_view, name='tipos_de_item'),
]
