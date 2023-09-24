from djoser.serializers import UserSerializer, UserCreateSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from users.models import Subscription
from foodgram_backend.settings import FORBIDDEN_USERNAMES


class CustomReadUserSerializer(UserSerializer):
    """Serialize user model adding additional field 'is_subscribed'
    that true if user subscribed on serialized user.
    Also, added extra validation for 'users/me/' endpoint.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ('is_subscribed',)
        read_only_fields = UserSerializer.Meta.read_only_fields

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return False if user.is_anonymous else (
            Subscription.objects.filter(user=user, author=obj).exists())

    def validate(self, attrs):
        if ('me' in self.context['request'].path
                and self.context['request'].user.is_anonymous):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return super().validate(attrs)


class CustomCreateUserSerializer(UserCreateSerializer):
    class Meta:
        model = UserCreateSerializer.Meta.model
        fields = UserCreateSerializer.Meta.fields

    def validate(self, attrs):
        if attrs.get('username').lower() in FORBIDDEN_USERNAMES:
            raise ValidationError(
                detail='This username is forbidden.'
            )

        return super().validate(attrs)
