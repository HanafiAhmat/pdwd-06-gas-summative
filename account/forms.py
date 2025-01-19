from django.forms import Form, ModelForm, ValidationError, EmailField, CharField, Select, IntegerField, DateField
from django.contrib.auth.models import User
from .models import CustomerProfile, CustomerAddress, CustomerGender

class RegistrationForm(Form):
    first_name = CharField(max_length=120, required=True)
    last_name = CharField(max_length=120, required=True)
    email = EmailField(max_length=196, required=True)
    password = CharField(min_length=6, max_length=120, required=True)
    confirm_password = CharField(min_length=6, max_length=120, required=True)
    phone = CharField(max_length=15, required=False)
   
    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already exists. Please choose a different email.")

        return email

    def clean(self):
        password = self.cleaned_data.get("password", '')
        confirm_password = self.cleaned_data.get("confirm_password", '')

        if password != confirm_password:
            msg = "Password and Confirm Password do not match."
            self.add_error("confirm_password", msg)
            raise ValidationError(msg)

        return self.cleaned_data

    def save(self, commit=True): 
        if commit is True:
            user = User.objects.create_user(
                username=self.cleaned_data.get('email'), 
                email=self.cleaned_data.get('email'), 
                password=self.cleaned_data.get('password'), 
                first_name=self.cleaned_data.get('first_name'), 
                last_name=self.cleaned_data.get('last_name')
            )
            CustomerProfile.objects.create(user=user, phone=self.cleaned_data.get('phone'))
        else:
            user = User(
                username=self.cleaned_data.get('email'), 
                email=self.cleaned_data.get('email'), 
                password=self.cleaned_data.get('password'), 
                first_name=self.cleaned_data.get('first_name'), 
                last_name=self.cleaned_data.get('last_name')
            )
            CustomerProfile(user=user, phone=self.cleaned_data.get('phone'))

        return user

class ProfileForm(Form):   
    first_name = CharField(max_length=120, required=True)
    last_name = CharField(max_length=120, required=True)
    email = EmailField(max_length=196, required=True)
    phone = CharField(max_length=15, required=False)
    date_of_birth = DateField(required=False)
    gender_id = IntegerField(required=False)
    user_id = IntegerField(required=True)

    def clean(self):
        userId = self.cleaned_data.get("user_id")
        email = self.cleaned_data.get("email")

        if User.objects.exclude(id=userId).filter(email=email).exists():
            raise ValidationError("Email already exists. Please choose a different email.")

        return self.cleaned_data

    def save(self):
        user = User.objects.get(id=self.cleaned_data.get('user_id'))
        user.email = self.cleaned_data.get('email')
        user.first_name = self.cleaned_data.get('first_name') 
        user.last_name = self.cleaned_data.get('last_name')
        user.save()

        if user.profile is None:
            CustomerProfile.objects.create(
                user=user, 
                phone=self.cleaned_data.get('phone'),
                date_of_birth=self.cleaned_data.get('date_of_birth'),
                gender_id=self.cleaned_data.get('gender_id')
            )
        else:
            user.profile.phone = self.cleaned_data.get('phone')
            user.profile.date_of_birth = self.cleaned_data.get('date_of_birth')
            user.profile.gender_id = self.cleaned_data.get('gender_id')
            user.profile.save()

        return user.profile

    class Meta:
        gender_choices = (
            ('1', 'Undisclosed'),
            ('2', 'Female'),
            ('3', 'Male'),
        )

        widgets = {
            'gender_id': Select(choices=gender_choices, attrs={'class': 'form-control'}),
        }

class CustomerAddressForm(ModelForm):
    class Meta:
        model = CustomerAddress
        fields = "__all__"
   
        IS_DEFAULT_CHOICES = (
            ('0', 'No'),
            ('1', 'Yes'),
        )
        widgets = {
            'default': Select(choices=IS_DEFAULT_CHOICES, attrs={'class': 'form-control'}),
        }

# class LoginForm(ModelForm):
#     # specify the name of model to use
#     class Meta:
#         model = ChatHistory
#         fields = "__all__"
