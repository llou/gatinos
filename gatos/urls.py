from django.urls import path, include
from modernrpc.views import RPCEntryPoint
from . import views


gato_urls = [
    path("capturar", views.CapturarGato.as_view(), name="capturar"),
    path("liberar", views.LiberarGato.as_view(), name="liberar"),
    path("morir", views.MorirGato.as_view(), name="morir"),
    path("capturas/c/<int:pk>", views.CapturaView.as_view(),
         name="captura"),
    path("capturas/c/<int:pk>/vacunar", views.VacunarGato.as_view(),
         name="vacunar"),
    path("capturas/c/<int:pk>/update", views.CapturaUpdateView.as_view(),
         name="captura-update"),
    path("capturas/c/<int:pk>/delete",
         views.CapturaDeleteView.as_view(),
         name="captura-delete"),
    path("enfermedad/create", views.EnfermedadCreateView.as_view(),
         name="enfermedad-create"),
    path("enfermedad/<int:pk>", views.EnfermedadView.as_view(),
         name="enfermedad"),
    path("enfermedad/e/<int:pk>/update", views.EnfermedadUpdateView.as_view(),
         name="enfermedad-update"),
    path("enfermedad/e/<int:pk>/delete", views.EnfermedadDeleteView.as_view(),
         name="enfermedad-delete"),
]


colonia_urls = [
    path('comidas', views.CalendarioComidas.as_view(),
         name="comidas"),
    path('avistamientos', views.Avistamientos.as_view(), name="avistamiento"),
    path('gatos/', views.GatosView.as_view(), name="gatos"),
    path('gato-add', views.GatoCreateView.as_view(), name="gato-add"),
    path('gatos/g/<slug:gato>', views.GatoView.as_view(), name="gato"),
    path('gatos/g/<slug:gato>/update', views.GatoUpdateView.as_view(),
         name="gato-update"),
    path('gatos/g/<slug:gato>/update', views.GatoUpdateView.as_view(),
         name="gato-update"),
    path('gatos/g/<slug:gato>/', include(gato_urls)),
    path('fotos/', views.FotosView.as_view(), name="fotos"),
    path('fotos/update-miniaturas', views.update_miniaturas,
         name="update-miniaturas"),
    path('fotos/update-exifs', views.update_exifs,
         name="update-exifs"),
    path('foto-add', views.FotoCreateView.as_view(), name="foto-add"),
    path('fotos/f/<str:foto>', views.FotoView.as_view(),
         name="foto"),
    path('fotos/f/<str:foto>/update', views.FotoUpdateView.as_view(),
         name="foto-update"),
    path('fotos/f/<str:foto>/delete', views.FotoDeleteView.as_view(),
         name="foto-delete"),
    path("informes", views.InformesView.as_view(),
         name="informes"),
    path("informes/create", views.InformeCreateView.as_view(),
         name="informe-create"),
    path("informes/i/<int:pk>", views.InformeView.as_view(),
         name="informe"),
    path("informes/i/<int:pk>/update", views.InformeUpdateView.as_view(),
         name="informe-update"),
    path("informes/i/<int:pk>/delete",
         views.InformeDeleteView.as_view(),
         name="informe-delete"),
    ]

user_urls = [
    ]

urlpatterns = [
    path("", views.ColoniasList.as_view(), name="colonias"),
    path("rpc/", RPCEntryPoint.as_view(enable_doc=True), name="RPC"),
    path('colonia-add', views.ColoniaCreateView.as_view(), name="colonia-add"),
    path('colonia/c/<slug:colonia>', views.ColoniaView.as_view(),
         name="colonia"),
    path('colonia/c/<slug:colonia>/update', views.ColoniaUpdateView.as_view(),
         name="colonia-update"),
    path('colonia/c/<slug:colonia>/', include(colonia_urls)),
    path('user/u/<str:username>/profile', views.UserProfile.as_view(),
         name="user-activity"),
    path('comidas/<str:codigo>', views.CalendarioComidas.as_view(),
         name="calendario-comidas"),
    ]
