from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django_app.views import *

schema_view = get_schema_view (
    openapi.Info (
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact ( email="contact@snippets.local" ),
        license=openapi.License ( name="BSD License" ),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path ( 'admin/', admin.site.urls ),

    path ( 'api/token/', LoginUser.as_view (), name='token_obtain_pair' ),
    path ( 'api/token/refresh/', TokenRefreshView.as_view (), name='token_refresh' ),
    path ( 'api/token/verify/', TokenVerifyView.as_view (), name='token_verify' ),

    path('categories/', CategoryListCreate.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryDetail.as_view(), name='category-detail'),
    path('news/', NewsListCreate.as_view(), name='news-list-create'),
    path('news/<int:pk>/', NewsDetail.as_view(), name='news-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
    path ( 'users/', UserListCreateView.as_view (), name='user-list-create' ),
    path ( 'users/<int:pk>/', UserDetailView.as_view (), name='user-detail' ),

    path ( 'swagger<format>/', schema_view.without_ui ( cache_timeout=0 ), name='schema-json' ),
    path ( 'swagger/', schema_view.with_ui ( 'swagger', cache_timeout=0 ), name='schema-swagger-ui' ),
    path ( 'redoc/', schema_view.with_ui ( 'redoc', cache_timeout=0 ), name='schema-redoc' ),
]