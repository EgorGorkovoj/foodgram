from django.shortcuts import get_object_or_404

from djoser import views as djoser_viewset

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.permissions import IsAuthorOrReadOnlyPermissions
from api.pagination import CustomPagination
from users.models import CustomUser, Subscription
from users.serializers import (AvatarSerializer, UserSerializer,
                               SubscriptionListSerializer,
                               SubscriptionSerializer)


class UserViewSet(djoser_viewset.UserViewSet):
    """""Вьюсет из djoser."""
    queryset = CustomUser.objects.all()
    pagination_class = CustomPagination
    http_method_names = ['get', 'post', 'put', 'delete', ]

    @action(detail=False, methods=['get'],)
    def me(self, request):
        user = CustomUser.objects.get(pk=self.request.user.id)
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
        request.user.avatar.delete()
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ['get', ], detail=False, url_path='subscriptions',
        permission_classes=[IsAuthenticated],
        serializer_class=[SubscriptionListSerializer],
    )
    def get_subscriptions(self, request):
        subscriptions = CustomUser.objects.filter(
            following__customuser=self.request.user
        )
        return Response(subscriptions, status=status.HTTP_200_OK)

    @action(
        ['post', 'delete', ], detail=True,
        url_path='subscribe',
        permission_classes=[IsAuthenticated],
    )
    def subscribe_or_unsubscribe(self, request, id):
        author = CustomUser.objects.get(pk=id)
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










# class UserViewSet(viewsets.ReadOnlyModelViewSet):
#     """""Вьюсет из djoser."""
#     pagination_class = CustomPagination
#     serializer_class = UserSerializer
#     http_method_names = ['get', 'post', 'put', 'delete', ]

    # def get_queryset(self, pk=None):
    #     pk = self.kwargs.get('pk')
    #     return CustomUser.objects.filter(pk=pk)

    # @action(detail=False, permission_classes=[IsAuthenticated], methods=['get'])
    # def me(self, request):
    #     user = CustomUser.objects.get(pk=self.request.user.id)
    #     serializer = UserSerializer(user)
    #     return Response(serializer.data)
    
    # def list(self, request):
    #     queryset = User.objects.all()
    #     serializer = UserSerializer(queryset, many=True)
    #     return Response(serializer.data)

    # def get_permissions(self, pk=None):
    #     pk = self.kwargs.get('pk')
    #     if pk and self.action == 'retrieve':
    #         return (AllowAny(),)
    #     return super().get_permissions()

    # def get_serializer_class(self):
    #     if self.request.method == 'POST':
    #         return PostUserSerializer
    #     if self.request.method == 'PUT':
    #         return AvatarSerializer
    #     return UserSerializer

# class SubscriptionListViewSet(viewsets.ModelViewSet):
#     """Вьюсет модели Subscription. Получает все подписки пользователя."""
#     serializer_class = SubscriptionListSerializer
#     http_method_names = ['get']

#     def get_queryset(self):
#         return CustomUser.objects.filter(
#             following__customuser=self.request.user
#         )


# class SubscriptionViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет модели Subscription.
#     Работает только с Post и Delete запросами.
#     """
#     serializer_class = SubscriptionSerializer
#     pagination_class = CustomPagination
#     http_method_names = ['post', 'delete', ]

#     def perform_create(self, serializer):
#         user = self.request.user
#         pk = self.kwargs.get('author_id')
#         author = get_object_or_404(CustomUser, pk=pk)
#         data = {'author': author.id, 'user': user.id}
#         serializer = SubscriptionSerializer(data=data, context={'request': self.request})
#         serializer.is_valid(raise_exception=True)
#         serializer.save()


    # def create(self, request, author_id):
    #     pk = self.kwargs.get('author_id')
    #     user = get_object_or_404(CustomUser, pk=pk)
    #     serializer = SubscriptionSerializer(user)
    #     self.perform_create(serializer)
    #     return Response(serializer.data)

    # def destroy(self, request, pk=None):
    #     author = get_object_or_404(CustomUser, pk=pk)
    #     author.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
