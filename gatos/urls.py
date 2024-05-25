from django.urls import path, include
from . import views

colonia_urls = [
    path('gatos/', views.GatosView.as_view(), name="gatos"),
    path('gato-add', views.GatoCreateView.as_view(), name="gato-add"),
    path('gatos/<slug:gato>', views.GatoView.as_view(), name="gato"),
    path('gatos/<slug:gato>/update', views.GatoUpdateView.as_view(),
         name="gato-update"),
    path('gatos/<slug:gato>/delete', views.GatoDeleteView.as_view(),
         name="gato-delete"),
    path('fotos/', views.FotosView.as_view(), name="fotos"),
    path('foto-add', views.FotoCreateView.as_view(), name="foto-add"),
    path('fotos/<uuid:foto>', views.FotoView.as_view(),
         name="foto"),
    path('fotos/<uuid:foto>/update', views.FotoUpdateView.as_view(),
         name="foto-update"),
    path('fotos/<uuid:foto>/delete', views.FotoDeleteView.as_view(),
         name="foto-delete")

    ]


urlpatterns = [
    path("", views.ColoniasList.as_view(), name="colonias"),
    path('colonia-add', views.ColoniaCreateView.as_view(), name="colonia-add"),
    path('colonia/<slug:colonia>', views.ColoniaView.as_view(),
         name="colonia"),
    path('colonia/<slug:colonia>/update', views.ColoniaUpdateView.as_view(),
         name="colonia-update"),
    path('colonia/<slug:colonia>/delete', views.ColoniaDeleteView.as_view(),
         name="colonia-delete"),
    path('colonia/<slug:colonia>/', include(colonia_urls)),
    ]
