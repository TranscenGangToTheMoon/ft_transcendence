import random
import string

from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import serializers

from users.models import Users, Friends
from users.validators import validate_username


# class UserRegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#
#     class Meta:
#         model = User
#         fields = ('username', 'password', 'email')
#
#     def post(self, request):
#         serializer = UserRegisterSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return generi({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data['email'],
#             password=validated_data['password']
#         )
#         return user
#
#     def create(self, validated_data):
#         request = self.context.get('request')
#         print(request)
#         if request is not None:
#             if Users.objects.filter(django_user=request.id).exist():
#                 raise serializers.ValidationError("You already connected")
#             if Users.objects.filter(django_user=request.id).exist():
#                 raise serializers.ValidationError("")
#             validated_data['username'] = request.user.username
#         print(validated_data)
#         if validated_data.get('username') is None:
#             validated_data['username'] = 'Guest' + ''.join(random.choices(string.digits, k=5))
#         return super().create(validated_data)


class UserPublicSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email'
        ]


class UsersRetrieveSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='users-detail', lookup_field='pk')
    username = serializers.CharField(validators=[validate_username], read_only=True)
    user = UserPublicSerializer(source='django_user', read_only=True)
    email = serializers.EmailField(source="django_user.email", write_only=True)
    coucou = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'user',
            'email',
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
            'coucou'
        ]

    def get_coucou(self, obj):
        print("hey salut")
        return "coucou"

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
        validated_data.pop('email')
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
