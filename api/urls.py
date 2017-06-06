from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    url(r'^$', views.ocrView, name='ocrView'),
    #url(r'^$', views.index, name='index'),
    #url(r'^api/$', views.ocr, name='ocr'),
    #url(r'^api/(?P<filename>[\w\W]+)/$', views.ocr, name='ocr'),
    #url(r'^api/(?P<image_full_name>[\w\W]+)/$', views.ocr, name='ocr'),
]
