from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import logout, login
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.contrib import messages
from django.core.mail import send_mail
from allauth.account.utils import send_email_confirmation
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.db import transaction
import logging


from .forms import *
from .models import *

logger = logging.getLogger(__name__)
EMAIL_FROM = 'from@lanuelgram.com'

def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            return redirect_to_login(request.get_full_path())
        
    posts = profile.user.posts.all()
    
    if request.htmx:
        if "top-posts" in request.GET:
            posts = profile.user.posts.annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by("-num_likes")

        elif "top-comments" in request.GET:
            comments = profile.user.comments.select_related('parent_post').annotate(num_likes=Count('likes')).filter(num_likes__gt=0).order_by("-num_likes")
            return render(request, "snippets/loop_profile_comments.html", {"comments": comments})

        elif "liked-posts" in request.GET:
            posts = profile.user.likedposts.order_by("-likedpost__created")
        
        return render(request, "snippets/loop_profile_posts.html", {"posts": posts})
        
    context = {
        'profile':profile,
        'posts':posts,
    }
        
    return render(request, 'a_users/profile.html', context)


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)  
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
        
    if request.path == reverse('profile-onboarding'):
        onboarding = True
    else:
        onboarding = False
      
    return render(request, 'a_users/profile_edit.html', { 'form':form, 'onboarding':onboarding })


@login_required
def profile_settings_view(request):
    return render(request, 'a_users/profile_settings.html')


@login_required
def profile_emailchange(request):
    
    if request.htmx:
        form = EmailForm(instance=request.user)
        return render(request, 'partials/email_form.html', {'form':form})
    
    if request.method == 'POST':
        form = EmailForm(request.POST, instance=request.user)

        if form.is_valid():
            
            # Check if the email already exists
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exclude(id=request.user.id).exists():
                messages.warning(request, f'{email} is already in use.')
                return redirect('profile-settings')
            
            form.save() 
            
            # Then Signal updates emailaddress and set verified to False
            
            # Then send confirmation email 
            send_email_confirmation(request, request.user)
            
            return redirect('profile-settings')
        else:
            messages.warning(request, 'Email not valid or already in use')
            return redirect('profile-settings')
        
    return redirect('profile-settings')


@login_required
def profile_usernamechange(request):
    if request.htmx:
        form = UsernameForm(instance=request.user)
        return render(request, 'partials/username_form.html', {'form':form})
    
    if request.method == 'POST':
        form = UsernameForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Username updated successfully.')
            return redirect('profile-settings')
        else:
            messages.warning(request, 'Username not valid or already in use')
            return redirect('profile-settings')
    
    return redirect('profile-settings')    


@login_required
def profile_emailverify(request):
    send_email_confirmation(request, request.user)
    return redirect('profile-settings')


@login_required
def profile_delete_view(request):
    user = request.user
    if request.method == "POST":
        logout(request)
        user.delete()
        messages.success(request, 'Account deleted, what a pity!')
        return redirect('home')
    
    return render(request, 'a_users/profile_delete.html')


# === Utility Functions ===

def generate_reactivation_data(user):
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uidb64, token


def build_reactivation_link(user, request):
    uidb64, token = generate_reactivation_data(user)
    url = reverse('profile-reactivation', kwargs={'uidb64': uidb64, 'token': token})
    return request.build_absolute_uri(url)


def send_reactivation_email(user, reactivation_link):
    subject = 'Reactivate Your Lanuelgram Account'
    message = f'Click this link to reactivate your account: {reactivation_link}'
    send_mail(subject, message, EMAIL_FROM, [user.email])


def get_user_from_uid_token(uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        if default_token_generator.check_token(user, token):
            return user
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None
    return None


# === Views ===
class ProfileDeactivationSuccessView(TemplateView):
    template_name = 'a_users/deactivation_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get reactivation data from session
        username = self.request.session.get('deactivated_username')
        uidb64 = self.request.session.get('reactivation_uidb64')
        token = self.request.session.get('reactivation_token')
        reactivation_link = self.request.session.get('reactivation_link')
        
        # Check if we have complete reactivation data
        has_reactivation_data = all([uidb64, token, reactivation_link])

        if has_reactivation_data:
            context.update({
                'deactivated_username': username,
                'reactivation_uidb64': uidb64,
                'reactivation_token': token,
                'reactivation_link': reactivation_link,
            })
            
            # Only clear session data if this is a GET request (not a refresh)
            # and the user came from deactivation (not direct URL access)
            if (self.request.method == 'GET' and 
                self.request.META.get('HTTP_REFERER') and 
                'deactivate' in self.request.META.get('HTTP_REFERER', '')):
                
                # Mark that we've shown the success page
                self.request.session['deactivation_success_shown'] = True
                
        else:
            # Check if user is accessing this page directly without proper flow
            if not self.request.session.get('deactivation_success_shown'):
                logger.warning("User accessed deactivation success page without proper session data")
                context['invalid_access'] = True
            else:
                logger.info("Deactivation success page accessed after session cleanup")
                context['session_expired'] = True

        return context

    def dispatch(self, request, *args, **kwargs):
        # Clean up session data when user navigates away from this page
        # This happens when they click "Return to Home" or navigate elsewhere
        if (request.session.get('deactivation_success_shown') and 
            request.META.get('HTTP_REFERER') and 
            'deactivate_successful' in request.META.get('HTTP_REFERER', '')):
            
            # User is navigating away, safe to clean up
            session_keys_to_clear = [
                'reactivation_uidb64', 
                'reactivation_token', 
                'reactivation_link',
                'deactivation_success_shown'
            ]
            
            for key in session_keys_to_clear:
                request.session.pop(key, None)
                
            logger.info("Cleaned up deactivation session data")

        return super().dispatch(request, *args, **kwargs)


@method_decorator(csrf_protect, name='dispatch')
class ProfileDeactivationView(LoginRequiredMixin, FormView):
    template_name = 'a_users/profile_deactivation.html'
    form_class = ProfileDeactivationForm

    def get_success_url(self):
        return reverse('deactivation-success')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        uidb64, token = generate_reactivation_data(self.request.user)
        context.update({
            'reactivation_uidb64': uidb64,
            'reactivation_token': token,
        })
        return context

    def form_valid(self, form):
        user = self.request.user
        try:
            with transaction.atomic():
                profile = user.profile
                reactivation_link = build_reactivation_link(user, self.request)

                # Deactivate and notify
                profile.deactivate()
                send_reactivation_email(user, reactivation_link)

                # Save what we need BEFORE logout and flush
                username = user.username
                uidb64, token = generate_reactivation_data(user)

                logout(self.request)
                self.request.session.flush()  # This clears the session entirely

                # Restore needed session data AFTER flush
                self.request.session['deactivated_username'] = username
                self.request.session['reactivation_uidb64'] = uidb64
                self.request.session['reactivation_token'] = token
                self.request.session['reactivation_link'] = reactivation_link

                logger.info(f"User {user.username} (ID: {user.id}) deactivated their account")
                messages.success(self.request, 'Your account has been successfully deactivated.')

        except Exception as e:
            logger.error(f"Profile deactivation failed for user {user.id}: {str(e)}")
            messages.error(self.request, 'An error occurred while deactivating your account. Please try again.')
            return self.form_invalid(form)

        return super().form_valid(form)


class AccountInactiveView(TemplateView):
    template_name = 'account_inactive.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        uidb64 = self.request.session.get('reactivation_uidb64')
        token = self.request.session.get('reactivation_token')
        reactivation_link = self.request.session.get('reactivation_link')

        if not (uidb64 and token and reactivation_link):
            return context  # Nothing to add

        context.update({
            'reactivation_uidb64': uidb64,
            'reactivation_token': token,
            'reactivation_link': reactivation_link,
        })
        return context


class ProfileReactivationView(FormView):
    template_name = 'a_users/profile_reactivation.html'
    form_class = ProfileReactivationForm

    def get_success_url(self):
        return reverse('home')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_active:
            messages.info(request, "Your account is already active.")
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    def get_user(self):
        return get_user_from_uid_token(
            self.kwargs.get('uidb64'),
            self.kwargs.get('token')
        )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.get_user()
        if user:
            kwargs['user'] = user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_user()
        if user and hasattr(user, 'profile'):
            profile = user.profile
            uidb64, token = generate_reactivation_data(user)
            context.update({
                'profile': profile,
                'can_reactivate': profile.can_reactivate(),
                'days_remaining': profile.days_until_permanent_deactivation(),
                'reactivation_uidb64': uidb64,
                'reactivation_token': token,
            })
        else:
            context['invalid_link'] = True
        return context

    def form_valid(self, form):
        user = self.get_user()

        if not user:
            messages.error(self.request, "Invalid reactivation request.")
            return redirect('login')

        try:
            profile = user.profile
        except Profile.DoesNotExist:
            messages.error(self.request, "Profile not found.")
            return redirect('login')

        try:
            with transaction.atomic():
                profile.reactivate()
                user.backend = 'allauth.account.auth_backends.AuthenticationBackend'
                login(self.request, user)
                messages.success(self.request, "Your account has been successfully reactivated!")
                return super().form_valid(form)

        except ProfileReactivationError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except Exception as e:
            logger.error(f"Unexpected error during reactivation: {str(e)}")
            messages.error(self.request, "An unexpected error occurred. Please try again.")
            return self.form_invalid(form)
