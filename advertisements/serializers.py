from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def validate(self, data):
        if self.context['request'].method == 'POST' or self.context['request'].method == 'PATCH' \
                and data['status'] == 'OPEN':
            if Advertisement.objects.filter(creator=self.context["request"].user, status='OPEN').count() >= 10:
                raise ValidationError('Too many open advertisements.')
        return data



