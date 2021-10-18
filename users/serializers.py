from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import Profile
from users.services import validate_password, validate_password_match, validate_unique_email

class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(required = True, validators = [
                                        UniqueValidator(queryset = get_user_model().objects.all())])
    email = serializers.EmailField(required = True,)
    password = serializers.CharField(required = True,
                                validators = [validate_password])
    password2 = serializers.CharField(required = True)

    def validate(self, attrs) -> str:
        validate_password_match(attrs['password'], attrs['password2'])
        validate_unique_email(attrs['email'])
        return attrs
    

        


class UserRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name','last_name')

class UserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(validators = [UniqueValidator(
                                                queryset = get_user_model().objects.all())])
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UserAdminListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email',)

class UserAdminRetrieveSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = '__all__'


class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField(validators = [validate_password])
    password2 = serializers.CharField()

    def validate(self, attrs) -> str:
        validate_password_match(attrs['password'], attrs['password2'])
        
        return attrs

class UserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

class UserPasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(validators = [validate_password])
    new_password2 = serializers.CharField()

    def validate(self, attrs) -> str:
        validate_password_match(attrs['new_password'], attrs['new_password2'])
        
        return attrs

class ProfileSerializer(serializers.Serializer):
    username = serializers.CharField(validators = [UniqueValidator(
                                                queryset = Profile.objects.all())], required = False)
    profile_photo = serializers.ImageField(required = False,)
    contact = serializers.CharField(required = False)
    bio = serializers.CharField(required = False)
    #private = serializers.CharField()

    