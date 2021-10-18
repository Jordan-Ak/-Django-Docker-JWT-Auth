# from django.contrib.sites.models import Site##  Intended to use this import for getting domain name

from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import Profile

from users.serializers import (ProfileSerializer, UserAdminListSerializer, UserAdminRetrieveSerializer, 
                               UserCreateSerializer, UserPasswordChangeSerializer, 
                               UserPasswordResetConfirmSerializer,UserPasswordResetSerializer,
                               UserRetrieveSerializer, UserUpdateSerializer,)

from users.services import (profile_retrieve_user, profile_update, profile_user_check, 
                            user_all_refresh_blacklist,user_password_reset_send,
                            user_password_reset_validity,user_retrieve_email_token,
                            user_retrieve_email, user_create, user_email_verification_flow,
                            user_email_verified_check, user_retrieve_password_reset, user_update,
                            user_email_verification_confirm, user_password_change, 
                            user_password_reset_change)
from users.tasks import user_email_verification_flow_async, user_password_reset_send_async

# Create your views here.

class UserCreateView(APIView):
    serializer_class = UserCreateSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception= True)
        
        host = request.META['HTTP_HOST']
        
        data = serializer.validated_data
        user = user_create(data['username'], data['email'], data['password'])
        user_email_verification_flow_async.delay(user.email, user.email_verification_token, host)
        #user_email_verification_flow(user.email, user.email_verification_token, host)
        return Response({'message':'User Created Successfully, verify your email'},
                         status = status.HTTP_201_CREATED)

class UserDetailView(APIView):
    serializer_class = UserRetrieveSerializer
    serializer_class_PUT = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        user = request.user
        serializer = self.serializer_class_PUT(data = request.data, instance = user,
                                                                             partial = partial,)
        serializer.is_valid(raise_exception = True)
        user_update(user, **serializer.validated_data)
        return Response({'message': 'User Updated Successfully'}, status = status.HTTP_202_ACCEPTED)

class UserAdminListView(generics.ListAPIView):
    serializer_class = UserAdminListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()

class UserAdminDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserAdminRetrieveSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = get_user_model().objects.all()
    lookup_url_kwarg = 'id'

class UserEmailVerificationConfirmView(APIView):
    
    def post(self, request, email_verification_token = None, *args, **kwargs):
        user = user_retrieve_email_token(email_verification_token)
        user_email_verification_confirm(user)
        return Response({'message': 'Your email is now verified'}, status = status.HTTP_200_OK)

class UserResendEmailVerificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        host = request.META['HTTP_HOST']

        user = request.user
        user_email_verified_check(user)
        user.generate_email_verification_token()
        user_email_verification_flow_async.delay(user.email, user.email_verification_token, host)
        #user_email_verification_flow(user.email, user.email_verification_token, host)
        return Response({'message': 'Email confirmation has been re-sent'}, status = status.HTTP_200_OK)
    
class UserPasswordChangeView(APIView):
    serializer_class = UserPasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data = request.data,)
        serializer.is_valid(raise_exception = True)
        user_password_change(user, **serializer.validated_data)
        return Response({'message':'Password Changed Successfully'},
                          status = status.HTTP_202_ACCEPTED)

class UserPasswordResetView(APIView):
    serializer_class = UserPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        host = request.META['HTTP_HOST']

        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        user = user_retrieve_email(serializer.validated_data['email'])
        

        user.generate_password_verification_token()
        user_password_reset_send_async.delay(serializer.validated_data['email'], user.password_reset_token, host)
        #user_password_reset_send(serializer.validated_data['email'], user.password_reset_token, host)
        return Response({'message':'Password Reset sent successfully, All accounts have been logged out'},
                          status = status.HTTP_202_ACCEPTED)

class UserPasswordResetConfirmView(APIView):
    serializer_class = UserPasswordResetConfirmSerializer

    def get(self, request, password_reset_token = None, *args, **kwargs):
        user = user_retrieve_password_reset(password_reset_token)
        user_password_reset_validity(user)
        return Response({'message': "Please put in your new password"}, status = status.HTTP_200_OK)

    def post(self, request, password_reset_token = None, *args, **kwargs):
        user = user_retrieve_password_reset(password_reset_token)
        user_password_reset_validity(user)
        serializer = self.serializer_class(data = request.data)
        serializer.is_valid(raise_exception = True)
        user_password_reset_change(user, serializer.validated_data['new_password'])
        user_all_refresh_blacklist(user)
        return Response({'message':'Password has been reset successfully'}, status = status.HTTP_202_ACCEPTED)

class UsersLogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message':"User has logged out successfully"}, 
                            status = status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response({"message": "Error occurred with current action."},
                                    status = status.HTTP_400_BAD_REQUEST)

class ProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProfileSerializer

    def get(self, request, username = None, *args, **kwargs):
        profile = profile_retrieve_user(username)
        #I just learnt if you put the context = {"request": request} django rest automatically gives you 
        #  The full image url instead of one without the domain name
        serializer = self.serializer_class(profile, context={"request": request})
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, username = None, *args, **kwargs):
        user = self.request.user
        profile_user_check(user, username)
        profile = profile_retrieve_user(username)
        serializer = self.serializer_class(data = request.data, instance =profile)
        serializer.is_valid(raise_exception = True)
        profile_update(profile, **serializer.validated_data)
        return Response({'message': 'Profile Updated Successfully'}, status = status.HTTP_202_ACCEPTED)
