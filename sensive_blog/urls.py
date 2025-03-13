from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('page/<int:page>', views.index, name='index'),
    path('tag/<slug:tag_slug>/', views.tag_filter, name='tag_filter'),
    path('post/<slug:slug>', views.post_detail, name='post_detail'),
    path('contacts/', views.contacts, name='contacts'),
    path('', views.index, name='index'),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
