import random
import string

from django.db.models import Q
from rest_framework import serializers

from users.models import Users, Friends
from users.validators import validate_username


class UsersRetrieveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-detail', lookup_field='pk')
    username = serializers.CharField(validators=[validate_username], read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'profile_picture',
            'accept_friend_request',
            'online_status',
            'last_online',
            'created_at',
            'is_guest',
            'trophy',
            'level',
            'title',
            'rank',
            'url',
        ]

    def validate_username(self, value):
        request = self.context.get('request').user
        print(request)
        username = request.username
        if value == "me":
            raise serializers.ValidationError("Username can't be 'me'")
        qs = Users.objects.filter(username=username, username__iexact=value) #iexact == case insensitive
        if qs.exists():
            raise serializers.ValidationError("Username already exists")
        if value is not None:
            value = value.upper()
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        print(request)
        if request is not None:
            if Users.objects.filter(django_user=request.id).exist():
                raise serializers.ValidationError("User already exists")
            validated_data['username'] = request.user.username
            print('hey:', validated_data['username'])
        print(validated_data)
        if validated_data.get('username') is None:
            print('coucou')
            validated_data['username'] = 'Guest' + ''.join(random.choices(string.digits, k=5))
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        return instance

    def save(self, **kwargs):
        if self.validated_data.get('password') is not None:
            kwargs['is_guest'] = False
        super().save(**kwargs)


class UsersMeSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-detail', lookup_field='pk')

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'profile_picture',
            'own_profile_picture',
            'accept_friend_request',
            'blocked_users',
            # 'friends',
            'online_status',
            'last_online',
            'created_at',
            'updated_at',
            'is_guest',
            'trophy',
            'level',
            'title',
            'own_titles',
            'rank',
            'url',
        ]

    # def get_friends(self):
    #     self_id = self.validated_data.get('id')
    #     if self_id is None:
    #         return None
    #     return Friends.objects.filter(Q(user1=self_id) | Q(user2=self_id))

    def save(self, **kwargs):
        if self.validated_data.get('password') is not None:
            kwargs['is_guest'] = False
        super().save(**kwargs)
