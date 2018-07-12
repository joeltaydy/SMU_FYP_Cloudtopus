from django.conf.urls import url
from Module_Account import views


urlpatterns = [
    url(r'^$', views.login, name='login'),
    url(r'^accounts/login/', views.login, name='login'),
    url(r'^accounts/logout/', views.logout, name='logout')
]
