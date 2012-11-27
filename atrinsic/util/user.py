from django.contrib.auth.models import User
import time

def generate_username(buf):
    ''' Generate a unique username based on the string passed as an argument

        Returns a string that is unique to the User Model's username field '''
    
    username = "%s-%s" % (buf[:16], str(time.time())[:13], )

    if User.objects.filter(username=username).count() > 0:

        while True:
            username = "%s-%s" % (buf[:16], str(time.time())[:13], )

            if User.objects.filter(username=username).count() < 1:
                break
           

    return username 

