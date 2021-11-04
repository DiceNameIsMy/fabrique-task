from django.contrib import admin
from django.urls import path, include

from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer

schema_view = get_schema_view(
    title='Users API', 
    renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer]
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('v1/', include([
            path('accounts/', include('apps.accounts.api.v1.urls')),
            path('surveys/', include('apps.surveys.api.v1.urls')),
        ])),
    ])),
    path('docs/', schema_view, name='docs'),
]
