from django.shortcuts import get_object_or_404

from djoser import views as djoser_viewset

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from api.permissions import IsAuthorOrReadOnlyPermissions, ReadOnly
from api.pagination import CustomPagination
from users.models import CustomUser
from users.serializers import (AvatarSerializer, PostUserSerializer,
                               UserSerializer, SubscriptionListSerializer,
                               SubscriptionSerializer)


# class UserViewSet(djoser_viewset.UserViewSet):
#     """Вьюсет из djoser для стандартных операций с пользователями."""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     pagination_class = CustomPagination
#     http_method_names = ['get', 'post', 'delete', ]

#     def get_serializer_class(self):
#         if self.request.method == 'POST':
#             return PostUserSerializer
#         return UserSerializer


class UserViewSet(djoser_viewset.UserViewSet):
    """""Вьюсет из djoser."""
    queryset = CustomUser.objects.all()
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'delete', ]

    # @action(detail=True, methods=['get'])
    # def me(self, request):
    #     user = CustomUser.objects.get(user=self.request.user.id)
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)


    # def list(self, request):
    #     queryset = User.objects.all()
    #     serializer = UserSerializer(queryset, many=True)
    #     return Response(serializer.data)

    # def get_permissions(self):
    #     if self.action == 'list':
    #         return (ReadOnly(),)
    #     return super().get_permissions()

    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return PostUserSerializer
    #     if self.request.method == 'PUT':
    #         return AvatarSerializer
    #     return UserSerializer

    # @action(detail=True, methods=['get'])
    # def me(self, request):
    #     user = User.objects.get(user=self.request.user)
    #     serializer = self.get_serializer(user)
    #     return Response(serializer.data)

    # @action(detail=True, methods=['put', 'delete'], url_path='me/avatar')
    # def avatar(self, request):
    #     image = request.FILES['avatar']
    #     user = request.user
    #     user.avatar = image
    #     user.save()


class SubscriptionListViewSet(viewsets.ModelViewSet):
    """Вьюсет модели Subscription. Получает все подписки пользователя."""
    serializer_class = SubscriptionListSerializer
    http_method_names = ['get']

    def get_queryset(self):
        return CustomUser.objects.filter(
            following__customuser=self.request.user
        )


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    Вьюсет модели Subscription.
    Работает только с Post и Delete запросами.
    """
    serializer_class = SubscriptionSerializer
    http_method_names = ['post', 'delete', ]

    def create(self, request, pk=None):
        author = get_object_or_404(CustomUser, pk=pk)
        serializer = SubscriptionSerializer(author)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        author = get_object_or_404(CustomUser, pk=pk)
        author.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
