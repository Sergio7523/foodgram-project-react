from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.paginations import CustomPagination
from users.models import Follow, User
from users.serializers import (
    FollowSerializer,
    ResponeSubscribeSerializer,
    UserSerializer,
    CreateUserSerializer
)


class CustomUserViewSet(UserViewSet):
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CreateUserSerializer
        if self.request.method == 'GET':
            return UserSerializer
        return ResponeSubscribeSerializer

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)
        serializer = FollowSerializer(
            data={'user': user.id, 'author': author.id}
        )

        if request.method == 'POST':
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = ResponeSubscribeSerializer(
                author, context={'request': request}
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = Follow.objects.filter(user=user, author=author)

        if not follow.exists():
            return Response(
                {'errors': 'Вы не подписаны на пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('GET',),
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,),
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = ResponeSubscribeSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
