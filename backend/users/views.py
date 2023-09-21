from rest_framework import permissions, status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from users.models import Subscription, User
from foodgram.serializers import SubscriptionSerializer


class SubscriptionsViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscriptionSerializer

    def get_queryset(self):
        return (User.objects.filter(
            id__in=Subscription.objects.filter(
                user=self.request.user).values_list('author__id', flat=True)
        ).all())


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def subscribe(request, pk):
    author = get_object_or_404(User, id=pk)

    if request.method == 'POST':
        if (Subscription.objects.filter(user=request.user,
                                        author=author).exists()
                or request.user == author):
            error = {
                'detail': 'Already subscribed or trying to subscribe yourself.'
            }
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

        Subscription.objects.create(user=request.user, author=author)
        context = dict()
        context['request'] = request
        serializer = SubscriptionSerializer(author, context=context)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    if request.method == 'DELETE':
        subscription = Subscription.objects.filter(user=request.user,
                                                   author=author)
        if subscription.exists():
            subscription.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        return Response(
            {'detail': 'You already unsubscribed this author.'},
            status=status.HTTP_400_BAD_REQUEST
        )
