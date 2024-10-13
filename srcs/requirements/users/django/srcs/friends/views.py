from rest_framework import generics, serializers
from rest_framework.response import Response

from friends.models import Friends, FriendRequests
from friends.serializers import FriendsManagementSerializer
from user_management.permissions import get_object
from users.models import Users


class ManageFriendsView(generics.ListCreateAPIView):
    serializer_class = FriendsManagementSerializer

    # def get_object(self):
    #     return get_object(self.request)

    def create(self, request, *args, **kwargs):
        sender = get_object(request)
        receiver_name = request.data.get('username')

        if receiver_name is None:
            raise serializers.ValidationError({'username': ['This field is required.']})

        if receiver_name == sender.username:
            raise serializers.ValidationError({'error': 'You cannot send a friend request to yourself.'})

        if FriendRequests.objects.filter(sender=sender.pk).count() > 20:
            raise serializers.ValidationError({'error': 'You cannot send more than 20 friend requests at the same time.'})

        try:
            receiver = Users.objects.get(username=receiver_name)
            assert not receiver.blocked_users.filter(pk=sender.pk).exists()
        except (Users.DoesNotExist, AssertionError):
            raise serializers.ValidationError({'error': 'This user does not exist.'})

        if sender.blocked_users.filter(pk=receiver.pk).exists():
            raise serializers.ValidationError({'error': 'You block this user.'})

        if Friends.objects.filter(friends__in=[sender, receiver]).distinct().exists():
            raise serializers.ValidationError({'error': 'You are already friends with this user.'})

        if not receiver.accept_friend_request:
            raise serializers.ValidationError({'error': 'This user does not accept friend requests.'})

        if FriendRequests.objects.filter(sender=sender, receiver=receiver).exists():
            raise serializers.ValidationError({'error': 'You already send a friend requests.'})

        try:
            friend_request = FriendRequests.objects.get(sender=receiver, receiver=sender)
            friend_request.accept()
            return Response({"message": "Friendship established."})
        except FriendRequests.DoesNotExist:
            FriendRequests.objects.create(sender=sender, receiver=receiver)
            return Response({"message": "Friend request sent."})


friends_view = ManageFriendsView.as_view()
