"""blog_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from allauth.account.views import confirm_email
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view

API_TITLE="Blog API"
API_DESCRIPTION='A web API for create blogs'
schema_view=get_swagger_view(title=API_TITLE)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/',include('posts.urls')),
    path('api-auth/',include('rest_framework.urls')),
    path('api/v1/rest-auth/',include('rest_auth.urls')),
    re_path(r"^api/v1/rest-auth/registration/account-confirm-email/(?P<key>[\s\d\w().+-_',:&]+)/$", confirm_email,
        name="account_confirm_email"),
    path('api/v1/rest-auth/registration/',include('rest_auth.registration.urls')),
    #re_path(r'^api/v1/rest-auth/registration/account-confirm-email/(?P<key>[-:\w]+)/$', confirm_email),
    #path('schema/',schema_view),
    path('swagger-docs/',schema_view),
    path('docs/',include_docs_urls(title='Blog API', description=API_DESCRIPTION)),
]
