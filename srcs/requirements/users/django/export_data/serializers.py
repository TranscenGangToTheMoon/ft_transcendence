from rest_framework import serializers
from rest_framework.exceptions import APIException

from blocking.serializers import BlockedSerializer
from friend_requests.serializers import FriendRequestsSerializer
from friends.serializers import FriendsSerializer
from lib_transcendence import endpoints
from lib_transcendence.serializer import Serializer
from lib_transcendence.services import request_chat, request_game
from stats.serializers import StatsSerializer, RankedStatsSerializer
from users.models import Users
from users.serializers import UsersMeSerializer


class FriendDataSerializer(Serializer):
    friends = FriendsSerializer(many=True)
    friend_requests_sent = FriendRequestsSerializer(many=True)
    friend_requests_received = FriendRequestsSerializer(many=True)
    blocked_users = BlockedSerializer(source='blocked', many=True)

    class Meta:
        model = Users
        fields = [
            'friends',
            'friend_requests_sent',
            'friend_requests_received',
            'blocked_users',
        ]


class DownloadDataSerializer(Serializer):
    user_data = UsersMeSerializer(source='*')
    friend_data = FriendDataSerializer(source='*')
    stats_data = StatsSerializer(source='stats', many=True)
    ranked_data = RankedStatsSerializer(source='ranked_stats', many=True)
    chat_data = serializers.SerializerMethodField()
    game_data = serializers.SerializerMethodField()

    class Meta:
        model = Users
        fields = [
            'user_data',
            'friend_data',
            'stats_data',
            'ranked_data',
            'chat_data',
            'game_data',
        ]

    @staticmethod
    def get_chat_data(obj):
        try:
            return request_chat(endpoints.UsersManagement.fexport_data.format(user_id=obj.id), 'GET')
        except APIException:
            return []

    @staticmethod
    def get_game_data(obj):
        try:
            result = request_game(endpoints.UsersManagement.fexport_data.format(user_id=obj.id), 'GET')
        except APIException:
            result = {'matches': [], 'tournaments': []}
        return result
