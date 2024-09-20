from djoser import views

from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from users.models import User  # Subscription
from users.serializers import (AvatarSerializer, PostUserSerializer,
                               UserSerializer)


class UserViewSet(views.UserViewSet):
    """Вьюсет модели Tag."""
    queryset = User.objects.all()
    pagination_class = LimitOffsetPagination
    http_method_names = ['get', 'post', 'put', 'delete',]

    def get_serializer_class(self):
        if self.action == 'post':
            return PostUserSerializer
        if self.action == 'put':
            return AvatarSerializer
        return UserSerializer

    @action(detail=True, methods=['get'])
    def me(self, request):
        user = User.objects.get(user=self.request.user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    @action(detail=True, methods=['put', 'delete'], url_path='me/avatar/')
    def avatar(self, request):
        image = request.FILES['avatar']
        user = request.user
        user.avatar = image
        user.save()
