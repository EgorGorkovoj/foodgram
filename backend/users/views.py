from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404

from djoser import views as djoser_viewset

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.pagination import CustomPagination
from users.models import User, Subscription
from users.serializers import (AvatarSerializer, UserSerializer,
                               SubscriptionListSerializer,
                               SubscriptionSerializer)


class UserViewSet(djoser_viewset.UserViewSet):
    """""Вьюсет из djoser."""
    queryset = User.objects.all()
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'delete', ]

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        user = User.objects.get(pk=self.request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @action(
        ['put', 'delete', ], detail=False, url_path='me/avatar',
        permission_classes=[IsAuthenticated]
    )
    def add_avatar(self, request):
        if request.method == 'PUT':
            serializer = AvatarSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            avatar = serializer.validated_data.get('avatar')
            request.user.avatar = avatar
            request.user.save()
            avatar_url = self.request.build_absolute_uri(
                f'/media/users/{avatar.name}'
            )
            return Response({'avatar': avatar_url}, status=status.HTTP_200_OK)
        file_path = request.user.avatar.path
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get', ], detail=False, url_path='subscriptions',
        permission_classes=[IsAuthenticated],
    )
    def get_subscriptions(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        user_sub = user.follower.all()
        following = [sub.author for sub in user_sub]
        pagination = CustomPagination()
        numbering = pagination.paginate_queryset(following, request)
        if user_sub is not None:
            serializer = SubscriptionListSerializer(
                numbering, many=True, context={'request': request}
            )
            return pagination.get_paginated_response(serializer.data)
        serializer = SubscriptionListSerializer(
            following, context={'request': request})
        return Response(serializer.data)

    @action(
        ['post', 'delete', ], detail=True,
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe_or_unsubscribe(self, request, id):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                context={'request': request},
                data={'user': user.id, 'author': author.id}
            )
            serializer.is_valid(raise_exception=True)
            author = serializer.validated_data.get('author')
            user = serializer.validated_data.get('user')
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        subscrip = Subscription.objects.filter(user=user, author=author)
        if not subscrip.exists():
            return Response(
                {'Error': 'Вы не были подписаны на данного пользователя!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscrip.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
