"""django_projects URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path
from django.contrib import admin
import UWPath.views as uwPath

urlpatterns = [
    path('', uwPath.index, name='index'),
    path(r'admin/', admin.site.urls),
    path(r'api/', uwPath.AllApp.as_view()),
    path(r'api/course-info/get/<str:pk>', uwPath.Course_Info_API.as_view()),
    path(r'api/course-info/filter', uwPath.Course_Info_API.filter),
    path(r'api/course-info/', uwPath.Course_Info_List.as_view()),
    path(r'api/prereqs/', uwPath.Prereqs_List.as_view()),
    path(r'api/prereqs/get/<str:pk>', uwPath.Prereqs_API.as_view()),
    path(r'api/antireqs/', uwPath.Antireqs_List.as_view()),
    path(r'api/antireqs/get/<str:pk>', uwPath.Antireqs_API.as_view()),
    path(r'api/breath/', uwPath.Breath_List.as_view()),
    path(r'api/breath/get/<str:pk>', uwPath.Breath_API.as_view()),
    path(r'api/breath_met/', uwPath.BreathAPI.as_view()),
    path(r'api/requirements/', uwPath.Requirements_List.as_view()),
    path(r'api/requirements/get/<str:pk>', uwPath.Requirements_API.as_view()),
    path(r'api/communications/', uwPath.Communications_List.as_view()),
    path(r'api/communications/get/<int:pk>', uwPath.Communications_API.as_view()),
    path(r'api/meets_prereqs/get/<str:pk>', uwPath.UWPath_API.as_view()),

    #a little bit hardcoded below
    path(r'major/<str:major>/<str:majorExtended>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/', uwPath.requirements, name='requirements'),

    # major + option
    path(r'major/<str:major>/<str:majorExtended>/option/<str:option>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/<str:majorExtended>/option/<str:option>/<str:optionExtended>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/option/<str:option>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/option/<str:option>/<str:optionExtended>/', uwPath.requirements, name='requirements'),

    # major + minor
    path(r'major/<str:major>/minor/<str:minor>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/<str:majorExtended>/minor/<str:minor>/', uwPath.requirements, name='requirements'),

    # major + option + minor

    path(r'major/<str:major>/<str:majorExtended>/option/<str:option>/minor/<str:minor>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/<str:majorExtended>/option/<str:option>/<str:optionExtended>/minor/<str:minor>/', uwPath.requirements,
         name='requirements'),
    path(r'major/<str:major>/option/<str:option>/minor/<str:minor>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/option/<str:option>/<str:optionExtended>/minor/<str:minor>/', uwPath.requirements, name='requirements'),

    path(r'major/<str:major>/<str:majorExtended>/minor/<str:minor>/option/<str:option>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/<str:majorExtended>/minor/<str:minor>/option/<str:option>/<str:optionExtended>/', uwPath.requirements,
         name='requirements'),
    path(r'major/<str:major>/minor/<str:minor>/option/<str:option>/', uwPath.requirements, name='requirements'),
    path(r'major/<str:major>/minor/<str:minor>/option/<str:option>/<str:optionExtended>/', uwPath.requirements, name='requirements'),

    path(r'contact', uwPath.contact, name='contact'),
    re_path(r'(?P<pk>\d+)', uwPath.AppView.as_view()),
]
