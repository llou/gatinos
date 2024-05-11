from django.urls import path, include
from . import views

gatos_urls = [
    path('gatos/', views.GatosView.as_view(), name="gatos"),
    path('gatos-add', views.GatoCreateView.as_view(), name="gato-add"),
    path('gatos/<slug:gato>', views.GatoView.as_view(), name="gato"),
    path('gatos/<slug:slug>/update', views.GatoUpdateView.as_view(),
         name="gato-update"),
    path('gatos/<slug:slug>/delete', views.GatoDeleteView.as_view(),
         name="gato-delete"),
    ]

urlpatterns = [
    path("", views.ColoniasList.as_view(), name="colonias"),
    path('colonia-add', views.ColoniaCreateView.as_view(), name="colonia-add"),
    path('colonia/<slug:colonia>', views.ColoniaView.as_view(),
         name="colonia"),
    path('colonia/<slug:slug>/update', views.ColoniaUpdateView.as_view(),
         name="colonia-update"),
    path('colonia/<slug:slug>/delete', views.ColoniaDeleteView.as_view(),
         name="colonia-delete"),
    path('colonia/<slug:colonia>/', include(gatos_urls)),
    ]
