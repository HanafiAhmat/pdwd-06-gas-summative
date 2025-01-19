from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from secrets import token_urlsafe
from libs.commons import send_email
from .models import CustomerProfile, CustomerPasswordResetRequest, CustomerAddress, CustomerGender
from orders.models import Order
from .forms import RegistrationForm, CustomerAddressForm, ProfileForm

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            emailSubject = 'Registration Successful!'
            emailBody = {
                "text": f"Hi {user.first_name} {user.last_name}, \n\nWelcome to SmartShop.\nYou have successfully registered into our system.",
                "html": f"<h2>Hi {user.first_name} {user.last_name},</h2> <br><p>Welcome to SmartShop.</p><p>You have successfully registered into our system.</p>"
            }
            emailResult = send_email(recipient_email=user.email, email_subject=emailSubject, email_body=emailBody);

            return redirect('account_register_success')
        else:
            is_validated = True
            messages.error(request, 'Email already exists. Please choose a different email.', extra_tags="danger")
    else:
        is_validated = False
        form = RegistrationForm()

    return render(request, "account/register.html", {'form': form, 'is_validated': is_validated})
 
def registration_success(request):
    return render(request, "account/registration-success.html") 

def user_login(request):
    if request.method == "POST":
        username = request.POST['email']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            if request.user.is_superuser:
                return redirect("staff")
            else:
                return redirect("home")
            return redirect("home")
        else:
            messages.error(request, 'Incorrect username or password.', extra_tags="danger")
            return render(request, "account/login.html")

    return render(request, "account/login.html")
 
def user_logout(request):
    logout(request)
    return redirect ("/")

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            if user is not None:
                token = token_urlsafe()
                CustomerPasswordResetRequest.objects.create(email=email, token=token)
                resetUrl = request.build_absolute_uri(f'/auth/password-reset/{token}')
                emailSubject = 'Password Reset Request'
                emailBody = {
                    "text": f"Hi {user.first_name} {user.last_name}, \
                                \n\nThere is a request to reset your password.\nUse the link below to proceed with this process.\
                                \n\n{resetUrl}\
                                \n\nIf you did not initiated this request, please ignore this email.",
                    "html": f"<h2>Hi {user.first_name} {user.last_name},</h2>\
                                <br><p>There is a request to reset your password.</p><p>Use the link below to proceed with this process.</p>\
                                <br><p><a href=\"{resetUrl}\" target=\"_blank\">Password Reset Page</a></p>\
                                <br><p>If you did not initiated this request, please ignore this email.</p>"
                }
                emailResult = send_email(recipient_email=email, email_subject=emailSubject, email_body=emailBody);
        except Exception as e:
            pass
        messages.info(request, 'A password reset email has been sent if the email exists in our system.')
    return render(request, "account/password-reset-request.html")

def password_reset(request, token):
    form = SetPasswordForm
    is_validated = False;
    try:
        passwordResetRequest = get_object_or_404(CustomerPasswordResetRequest, token=token)
        try:
            user = get_object_or_404(User, email=passwordResetRequest.email)
            if request.method == 'POST':
                form = SetPasswordForm(user=user, data=request.POST)
                if form.is_valid():
                    form.save()
                    passwordResetRequest.is_used = 1
                    passwordResetRequest.save()
                    messages.success(request, 'New Password saved successfully')
                    return redirect('account_login')
                else:
                    is_validated = True;
                    messages.error(request, 'Please correct the error(s) below.', extra_tags="danger")
        except Exception as e:
            messages.error(request, 'User does not exists.', extra_tags="danger")
    except Exception as e:
        messages.error(request, 'Token is invalid.', extra_tags="danger")
    
    return render(request, 'account/password-reset.html', {'form': form, 'is_validated': is_validated})

@login_required(login_url='account_login')
def profile(request):
    try:
        profile = CustomerProfile.objects.get(user=request.user)
    except Exception as e:
        profile = CustomerProfile(user=request.user)

    if profile is not None:
        return render(request, 'account/authenticated/profile.html', {'profile': profile})
    else:
        return redirect('/')

@login_required(login_url='account_login')
def profile_update(request):
    allGenders = CustomerGender.objects.all()
    initialData = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'email': request.user.email,
        'phone': request.user.profile.phone,
        'date_of_birth': request.user.profile.date_of_birth,
        'gender_id': request.user.profile.gender_id,
        'user_id': request.user.id,
    }
    form = ProfileForm(initial=initialData)
    is_validated = False
    if request.method == 'POST':
        form = ProfileForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('account_profile')
        else:
            is_validated = True;
            messages.error(request, 'Please correct the error(s) below.', extra_tags="danger")

    data = {
        'form': form, 
        'allGenders': allGenders, 
        'is_validated': is_validated
    }
    return render(request, 'account/authenticated/profile-update.html', data)

@login_required(login_url='account_login')
def profile_change_password(request):
    form = PasswordChangeForm
    is_validated = False
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Password updated successfully')
            return redirect('account_profile')
        else:
            is_validated = True;
            messages.error(request, 'Please correct the error(s) below.', extra_tags="danger")
    return render(request, 'account/authenticated/change-password.html', {'form': form, 'is_validated': is_validated})

@login_required(login_url='account_login')
def home(request):
    return render(request, 'account/authenticated/home.html')

@login_required(login_url='account_login')
def addresses(request):
    addresses = request.user.addresses.all()

    return render(request, 'account/authenticated/addresses.html', {'addresses': addresses})

@login_required(login_url='account_login')
def add_edit_address(request, address_id=None):
    is_validated = False
    if address_id is None:
        mode = 'Add'
        address = CustomerAddress()
        form = CustomerAddressForm()
    else:
        mode = 'Edit'
        address = CustomerAddress.objects.filter(id=address_id).first()
        if address is None:
            messages.error(request, 'Requested address to be updated does not exists.', extra_tags="danger")
            return redirect('account_addresses')
        form = CustomerAddressForm(instance=address)

    if request.method == "POST":
        postData = request.POST.copy()
        postData['user'] = request.user
        form = CustomerAddressForm(postData, instance=address)
        if form.is_valid():
            userNoOfAddresses = request.user.addresses.count()
            if request.POST.get('default') == '1':
                if userNoOfAddresses > 0:
                    defaultAddress = request.user.addresses.get(default=True)
                    defaultAddress.default = False
                    defaultAddress.save()

            address = form.save()
            if address.default == False and userNoOfAddresses < 2:
                address.default = True
                address.save()

            if mode == 'Add':
                messages.success(request, 'Customer Address added successfully')
            else:
                messages.success(request, 'Customer Address updated successfully')
            return redirect('account_addresses')
        else:
            dd(form.errors)
            is_validated = True
            messages.error(request, 'Error creating new address.', extra_tags="danger")

    data = {
        'mode': mode, 
        'form': form,
        'is_validated': is_validated
    }
    return render(request, 'account/authenticated/address-form.html', data)

@login_required(login_url='account_login')
@csrf_protect
def delete_address(request, address_id):
    if request.method == 'POST':
        address = CustomerAddress.objects.filter(id=address_id).first()
        if address is None:
            messages.error(request, 'Requested address to be deleted does not exists.', extra_tags="danger")
            return redirect(request.META.get('HTTP_REFERER', 'account_addresses'))
    
        if address.default is True:
            adressAsDefault = CustomerAddress.objects.filter(default=False).first()
            if adressAsDefault is not None:
                adressAsDefault.default = True
                adressAsDefault.save()

        address.delete()
        messages.success(request, f'Selected Address deleted successfully')
        return redirect('account_addresses')
    else:
        messages.error(request, 'Bad Request.', extra_tags="danger")
        return redirect(request.META.get('HTTP_REFERER', 'account_addresses'))

@login_required(login_url='account_login')
def orders(request):
    orders = request.user.orders.all()

    return render(request, 'account/authenticated/orders.html', {'orders': orders})

@login_required(login_url='account_login')
def order_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
    except Exception as e:
        order = None
        messages.error(request, f'Requested "{order.id}" is not found.', extra_tags="danger")

    return render(request, 'account/authenticated/order-info.html', {'order': order})

















