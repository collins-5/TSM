from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import User, UserProfile
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, UserUpdateForm
from .decorators import admin_required


def register(request):
    """View for user registration"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Authenticate and login the user
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            messages.success(request, f'Account created successfully. Welcome to TSM!')
            return redirect('/')
        
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/registration/register.html', {'form': form})

@csrf_exempt
def login_view(request):
    """View for user login"""
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to the appropriate dashboard based on user type
            if user.is_admin_user or user.is_staff:
             return redirect('dashboard:admin_dashboard')
            elif user.is_buyer:
              return redirect('dashboard:buyer_dashboard')
            elif user.is_supplier:
              return redirect('dashboard:supplier_dashboard')
            return redirect('dashboard:home')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/registration/login.html', {'form': form})


@login_required
def profile_view(request):
    """View for viewing user profile"""
    user = request.user
    profile = user.profile
    
    return render(request, 'accounts/profile/view.html', {
        'user': user,
        'profile': profile
    })


@login_required
def profile_edit(request):
    """View for editing user profile"""
    user = request.user
    profile = user.profile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile, user=user)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile, user=user)
    
    return render(request, 'accounts/profile/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


@admin_required
def user_management(request):
    """View for user management (admin only)"""
    users = User.objects.all().order_by('-date_joined')
    
    return render(request, 'accounts/management/list.html', {
        'users': users
    })


@admin_required
def user_detail(request, user_id):
    """View for user details (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    return render(request, 'accounts/management/detail.html', {
        'user': user,
        'profile': user.profile
    })


@admin_required
def user_edit(request, user_id):
    """View for editing users (admin only)"""
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'User {user.username} has been updated successfully.')
            return redirect('accounts:user_detail', user_id=user.id)
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    return render(request, 'accounts/management/edit.html', {
        'user': user,
        'user_form': user_form,
        'profile_form': profile_form
    })


@admin_required
def user_delete(request, user_id):
    """View for deleting users (admin only)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been deleted successfully.')
        return redirect('accounts:user_management')
    
    return render(request, 'accounts/management/delete.html', {
        'user': user
    })