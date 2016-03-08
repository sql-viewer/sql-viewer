"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

from django.conf.urls import url


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from sqlviewer.glimpse.views import diagram_details_view, model_details_view, models_list_view, ModelView, VersionView, DiagramView

api = [
    url(r'^api/v1/models/(?P<model_id>\d+)?$', ModelView.as_view()),
    url(r'^api/v1/models/(?P<model_id>\d+)/versions/(?P<version_id>\d+)?$', VersionView.as_view()),
    url(r'^api/v1/models/(?P<model_id>\d+)/versions/(?P<version_id>\d+)/diagrams/(?P<diagram_id>\d+)?$', DiagramView.as_view()),
]
pages = [
    url(r'^$', models_list_view, name="model"),
    url(r'^models/(?P<model_id>[\w\-]+)[/]?$', model_details_view, name='model_details'),
    url(r'^models/(?P<model_id>[\w\-]+)/diagrams/(?P<diagram_id>[\w\-]+)[/]?$', diagram_details_view, name='diagram_details')
]

urlpatterns = pages + api
