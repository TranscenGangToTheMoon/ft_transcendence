from rest_framework import serializers

from users.models import Users


class UsersSerializer(serializers.ModelSerializer):
    rename_property = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Users
        fields = [
            'id',
            'username',
            'password',
            'rank',
            'trophy',
            'rename_property',
            'is_guest',
            'created_at',
            'updated_at',
        ]

    def get_rename_property(self, obj):
        if not hasattr(obj, 'id'):
            return None
        return obj.property_name

    def save(self, **kwargs):
        if self.validated_data.get('password') is not None:
            kwargs['is_guest'] = False
        super().save(**kwargs)
