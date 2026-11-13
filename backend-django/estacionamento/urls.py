from django.urls import include, path

urlpatterns = [
    path('api/', include('api.urls')),
]

handler404 = 'api.views.utils.nao_encontrado'
handler500 = 'api.views.utils.erro_interno'
