"""
RechteDB URL Configuration

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
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin

from django.urls import path
from django.views.generic import RedirectView

admin.site.site_header = 'RApp - Adminseiten'
admin.site.site_title = 'RApp - Administration'
admin.site.index_title = 'RApp - Übersicht'

urlpatterns = [
    path('admin', admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]

# Use include() to add paths from the rapp application
urlpatterns += [
    path('accounts/', include('django.contrib.auth.urls')),
    path('rapp/', include('rapp.urls')),
    path('mdeditor/', include('mdeditor.urls')),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Das ist die wichtigste Zeile: / wird auf /rapp gemappt
urlpatterns += [
    path('', RedirectView.as_view(url='/rapp')),
]
