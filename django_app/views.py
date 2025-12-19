from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .make_token import get_tokens_for_user
from .models import Category, News, Comment, User
from .serializers import CategorySerializer, NewsSerializer, CommentSerializer, UserSerializer, LoginSerializer, \
    UserCreateSerializer
from .permissions import CanReadComment, CanCreateComment, CanUpdateDeleteComment, AdminNoUpdatePermission


class LoginUser(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: '{"refresh": "string", "access": "string"}'}
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = get_tokens_for_user(user)
        return Response(data=token, status=status.HTTP_200_OK)

class CategoryListCreate(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("You cannot create categories")
        serializer.save()

class CategoryDetail(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if not (self.request.user.is_staff or self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("You cannot update categories")
        serializer.save()

    def perform_destroy(self, instance):
        if not (self.request.user.is_staff or self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("You cannot delete categories")
        instance.delete()

class NewsListCreate(ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

class NewsDetail(RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.author != self.request.user and not (self.request.user.is_staff or self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("You can only update your own news")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.author != self.request.user and not (self.request.user.is_staff or self.request.user.is_admin or self.request.user.is_superuser):
            raise PermissionDenied("You can only delete your own news")
        instance.delete()

class CommentListCreate(ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CanReadComment | CanCreateComment]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_create(self, serializer):
        if self.request.user.is_manager:
            raise PermissionDenied("You cannot create comments")
        serializer.save()

class CommentDetail(RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    permission_classes = [CanReadComment | CanUpdateDeleteComment]

    def get_queryset(self):
        return Comment.objects.all()

    def perform_update(self, serializer):
        if not self.request.user.is_admin:
            raise PermissionDenied("You cannot update comments")
        serializer.save()

    def perform_destroy(self, instance):
        if not self.request.user.is_admin:
            raise PermissionDenied("You cannot delete comments")
        instance.delete()

class UserListCreateView(ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AdminNoUpdatePermission]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AdminNoUpdatePermission]

    def update(self, request, *args, **kwargs):
        if request.user.is_admin and not request.user.is_superuser:
            return Response(
                {"detail": "Admins cannot update users."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.is_admin and not request.user.is_superuser:
            return Response(
                {"detail": "Admins cannot update users."},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().partial_update(request, *args, **kwargs)