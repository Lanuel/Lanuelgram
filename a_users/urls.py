from django.urls import path
from a_users.views import *

urlpatterns = [
    path('', profile_view, name="profile"),
    path('edit/', profile_edit_view, name="profile-edit"),
    path('onboarding/', profile_edit_view, name="profile-onboarding"),
    path('settings/', profile_settings_view, name="profile-settings"),
    path('emailchange/', profile_emailchange, name="profile-emailchange"),
    path('usernamechange/', profile_usernamechange, name="profile-usernamechange"),
    path('emailverify/', profile_emailverify, name="profile-emailverify"),
    path('delete/', profile_delete_view, name="profile-delete"),
    path('deactivate/', ProfileDeactivationView.as_view(), name="profile-deactivation"),
    path('deactivate_successful/', ProfileDeactivationSuccessView.as_view(), name='deactivation-success'),
    path('reactivate/<uidb64>/<token>/', ProfileReactivationView.as_view(), name="profile-reactivation")
]
