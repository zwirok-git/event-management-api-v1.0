from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers


User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={
            "input_type": "password",
            "placeholder": "Your password",
        }
    )
    repeat_password = serializers.CharField(
        write_only=True,
        required=True,
        style={
            "input_type": "password",
            "placeholder": "Repeat your password"
        },
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "repeat_password",
        ]

    def validate(self, attrs: dict):
        if attrs["password"] != attrs["repeat_password"]:
            raise serializers.ValidationError(
                {"repeat_password": "Passwords do not match."}
            )

        validate_password(attrs["password"])

        return attrs

    def create(self, validated_data: dict):
        validated_data.pop("repeat_password")

        user = User.objects.create_user(**validated_data)

        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email"
        ]
        read_only_fields = (
            "id",
            "email"
        )


class BaseUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]


class UserEventListSerializer(BaseUserListSerializer):
    class Meta(BaseUserListSerializer.Meta):
        pass


class OrganizerInfoSerializer(BaseUserListSerializer):
    class Meta(BaseUserListSerializer.Meta):
        pass
