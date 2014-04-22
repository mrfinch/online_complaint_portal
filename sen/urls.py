'''url for index view'''
from django.conf.urls import patterns, include, url
from sen import views
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'sen.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$',views.home,name="home"),
    url(r'^complaint_portal/',include('complaint_portal.urls',namespace="complaint_portal")),
    url(r'^admin/', include(admin.site.urls)),
)
