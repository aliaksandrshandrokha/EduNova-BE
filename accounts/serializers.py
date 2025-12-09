from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model."""
    class Meta:
        model = Profile
        fields = ['full_name']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with profile."""
    profile = ProfileSerializer(read_only=True)
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    email = serializers.EmailField(required=True)
    full_name = serializers.CharField(
        write_only=True,
        required=True,
        max_length=255
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'full_name', 'profile']
        extra_kwargs = {
            'username': {'required': True},
        }

    def validate_email(self, value):
        """Validate that email is unique."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Validate that username is unique."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        """Create a new user with profile."""
        full_name = validated_data.pop('full_name')
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )
        # Update profile with full_name
        user.profile.full_name = full_name
        user.profile.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user with profile."""
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'username', 'email']


class LoginSerializer(serializers.Serializer):
    """Serializer for login credentials."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

