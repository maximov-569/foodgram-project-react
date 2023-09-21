from djoser.serializers import UserSerializer
from rest_framework import serializers, status
from rest_framework.response import Response
from users.models import User, Subscription


class CustomUserSerializer(UserSerializer):
    """Serialize user model adding additional field 'is_subscribed'
    that true if user subscribed on serialized user.
    Also, added extra validation for 'users/me/' endpoint.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserSerializer.Meta.fields + ('is_subscribed',)
        read_only_fields = UserSerializer.Meta.read_only_fields

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, author=obj).exists()

    def validate(self, attrs):
        if ('me' in self.context['request'].path
                and self.context['request'].user.is_anonymous):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        return super().validate(attrs)
