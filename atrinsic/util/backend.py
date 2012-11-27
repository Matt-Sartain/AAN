from django.contrib.auth.backends import ModelBackend
from atrinsic.base.models import User
from atrinsic.base.choices import *


class UserBackend(ModelBackend):
    ''' Model Backend to handle the authentication mechanism for logging in a User '''

    def authenticate(self, email=None, password=None):
        ''' Authenticates a user by email address and password '''
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                if user.get_profile().admin_level==ADMINLEVEL_NONE:
                    if user.get_profile().organizations.all().count() == 1 and user.get_profile().organizations.filter(status=ORGSTATUS_LIVE).count() == 1:
                        return user
                    else:
                        return None
                else:
                    return user
        except User.DoesNotExist:
            return None
            
    def get_user(self, user_id):
        ''' Method to handle retrieving a user based on User ID for authentication '''

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
