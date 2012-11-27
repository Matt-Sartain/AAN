from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.defaultfilters import slugify
from django.core.mail import send_mail
from atrinsic.util.imports import *
from atrinsic.base.models import UserPasswordReset
from django.contrib.auth import authenticate, login, logout
import uuid

@url('^reset/$', 'auth_reset_password')
def auth_reset_password(request, template='auth/reset.html'):
    ''' View to allow users to reset their password.  This view takes a GET/POST variable
        of a UUID which was previously e-mailed to the User requesting a password reset.  
        If the UUID is valid, then display a PasswordResetForm allowing them to select
        a new password ''' 
    from forms import PasswordResetForm
    from atrinsic.base.models import User
    from atrinsic.util.backend import UserBackend
    from django.contrib.auth.models import AnonymousUser
    
    reset_auth = request.REQUEST.get('reset_auth', None)
    reset = get_object_or_404(UserPasswordReset, reset=reset_auth)

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)

        if form.is_valid():
            reset.user.set_password(form.cleaned_data['password'])
            reset.user.save()

            user = authenticate(email=reset.user.email, password=form.cleaned_data['password'])
            if user:    
                login(request, user)
    
                if request.session.get("organization_id", None):
                    del request.session["organization_id"]
                    
                reset.delete()
                return HttpResponseRedirect(reverse('auth_choice'))
                
    else:
        form = PasswordResetForm()

    return render_to_response(template, {
                'form' : form,
                'reset_auth' : reset_auth,
           }, context_instance = RequestContext(request))

@url(r'^login/forgotpass/$', 'forgot_pass')
def forgot_pass(request):
    from forms import ForgotPasswordForm
    from atrinsic.base.models import User

    result = ""

    try:
        
        email = request.POST['email']
        
        if email is None or len(email) < 1:
            result = "Please supply an email"
            
        u =  User.objects.get(email=email)
        if u:
            if u.get_profile().organizations.filter(status=ORGSTATUS_LIVE).count() < 1:
                result = "This E-Mail is not registered to an active account."
            else:
                reset_auth = uuid.uuid4()

                UserPasswordReset.objects.filter(user=u).delete()
                UserPasswordReset.objects.create(user=u, reset=reset_auth)

                send_mail('Password Reset', """\nHello, You have requested your password be reset.  To confirm your account and\n reset your password, please click on the link below:\n\n%s/accounts/reset?reset_auth=%s\n\n """ % (settings.SITE_URL, reset_auth), settings.SITE_CONTACT, [ u.email ], fail_silently=True)
                
                result="A link to reset your password has been emailed to the e-mail address you registered with." 
    except:
        result = "This E-Mail is not registered to an active account."
    
      
    
    return HttpResponse(result, mimetype="text/html")
    
    
@url(r'^login/$', 'auth_login')
def auth_login(request, template='auth/login.html', next='/'):
    ''' View for the main user authentication system.  Display a LoginForm to
        validate credentials, and optionally accept a ForgotPasswordForm to
        allow users to reset their password.'''
    from forms import LoginForm,ForgotPasswordForm
    from atrinsic.base.models import User
    
    form = LoginForm()
    forgotform = ForgotPasswordForm()
    user = None
    error = None

    next = request.REQUEST.get('next',next)

    if request.method == "POST":
        form = LoginForm(request.POST)
        forgotform = ForgotPasswordForm(request.POST)
        forgot_email = request.POST.get('forgot_email', None)


        if forgotform.is_valid() and forgotform.cleaned_data['forgot_email'] is not None:
            u = User.objects.get(email=forgotform.cleaned_data['forgot_email'])
            reset_auth = uuid.uuid4()

            UserPasswordReset.objects.filter(user=u).delete()
            UserPasswordReset.objects.create(user=u, reset=reset_auth)

            send_mail('Password Reset', """\nHello, You have requested your password be reset.  To confirm your account and\n reset your password, please click on the link below:\n\n%s/accounts/reset?reset_auth=%s\n\n """ % (settings.SITE_URL, reset_auth), settings.SITE_CONTACT, [ u.email ], fail_silently=True)

            return render_to_response('auth/reset.html', {}, context_instance = RequestContext(request))

        elif form.is_valid():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])

            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session["next"] = next
                    if request.session.get("organization_id",None):
                        del request.session["organization_id"]
                    return HttpResponseRedirect(reverse('auth_choice'))
                else:
                    error = "Account disabled"
            else:
                error = "Invalid Login"
        else:
            error = "Invalid Login"

    if request.GET.get("newhome",None)=="1":
        return render_to_response("notlogged/home.html",{
            'form':form,
            'error':error,
            'next' : next,
            'forgotform' : forgotform,
            }, context_instance=RequestContext(request))
    
    return render_to_response("auth/login2.html",{
    'form':form,
    'error':error,
    'next' : next,
    'forgotform' : forgotform,
    }, context_instance=RequestContext(request))



@url(r'^logout/$', 'auth_logout')
def auth_logout(request, next='/'):
    ''' View to handle a logout, which clears the session history as well. '''

    django_logout(request)
    if request.session.get("organization_id",None):
        del request.session["organization_id"]

    return HttpResponseRedirect(next)

@url(r'^choice/$', 'auth_choice')
@url(r'^choice/(?P<choice>[0-9]+)/$', 'auth_choice')
@login_required
def auth_choice(request,choice=None):
    ''' View for post authentication account choice. '''
    from atrinsic.base.models import Organization
    if request.user.get_profile().organizations.all().count() == 1 and request.user.get_profile().admin_level==ADMINLEVEL_NONE:
        request.session["organization_id"] = request.user.get_profile().organizations.all()[0].id
    elif choice == "0" and request.user.get_profile().admin_level > 0:
        request.session["network_login"] = True
        if request.session.get("organization_id",None):
            del request.session["organization_id"]
    elif choice != None and request.user.get_profile().organizations.filter(id=int(choice)).count() == 1:
        request.session["organization_id"] = request.user.get_profile().organizations.get(id=int(choice)).id
        
        
    if request.session.get("organization_id",None) or request.session.get("network_login",None) == True:
        try:
            next = request.session["next"]
            del request.session["next"]
        except:
            next = "/"

        if next == "/" and request.session.get("organization_id",None):
            org = Organization.objects.get(id=request.session["organization_id"])
            if org.is_publisher():
                next = reverse("publisher_dashboard")
            elif org.is_advertiser():
                next = reverse("advertiser_dashboard")
        if next == "/" and request.session.get("network_login",None):
            next=  "/network/"
        return HttpResponseRedirect(next)

    return render_to_response("auth/choice.html",{},context_instance=RequestContext(request))

@url(r'^impersonate/(?P<id>[0-9]+)/(?P<next>.*)$', 'auth_impersonate')
@admin_required
def auth_impersonate(request,id,next):
    ''' View to allow Network Admins to impersonate another account which they have
        credentials to manage. '''
    from atrinsic.base.models import Organization
    if request.user.get_profile().admin_level == ADMINLEVEL_NONE:
        raise Http404

    org = get_object_or_404(Organization,id=id)

    if org.is_publisher():
        if org in request.user.get_profile().admin_assigned_publishers():
            request.session["organization_id"] = org.id
        else:
            raise Http404
    elif org.is_advertiser():
        if org in request.user.get_profile().admin_assigned_advertisers():
            request.session["organization_id"] = org.id
        else:
            raise Http404
    return HttpResponseRedirect("/"+next)

@url(r'^unimpersonate/$','auth_unimpersonate')
@admin_required
def auth_unimpersonate(request):
    ''' View to remove the session variables of an impersonation. '''

    try:
        del request.session["organization_id"]
    except KeyError:
        pass

    return HttpResponseRedirect("/network/")
