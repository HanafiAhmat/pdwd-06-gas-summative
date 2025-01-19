from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
 
class CustomerGender(models.Model):
    name = models.CharField(max_length=24)
    code = models.CharField(max_length=24)
    default = models.BooleanField(default=False)

    class Meta:
        db_table = 'customer_genders'

    def __str__(self):
        return str(self.name) + " ["+str(self.code)+"]"

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, default=None, blank=True, null=True)
    date_of_birth = models.DateField(default=None, blank=True, null=True)
    gender = models.ForeignKey(CustomerGender, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        db_table = 'customer_profiles'

    def fullname(self):
        return str(self.user.first_name) + " " + str(self.user.last_name)

    def __str__(self):
        return str(self.fullname) + " ["+str(self.phone)+"]" + " ["+str(self.date_of_birth)+"]"

class CustomerPasswordResetRequest(models.Model):
    email = models.CharField(max_length=100)
    token = models.CharField(max_length=192)
    is_used = models.BooleanField(default=0)
    expire_at = models.DateTimeField()
   
    class Meta:
        db_table = 'customer_password_reset_requests'

    def save(self, *args, **kwargs):
        self.expire_at = timezone.now() + timedelta(hours=1)
        return super().save(*args, **kwargs)

    def __str__(self):
        return ""

class CustomerAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    recipient_first_name = models.CharField(max_length=120, default=' ')
    recipient_last_name = models.CharField(max_length=120, default=' ')
    recipient_phone = models.CharField(max_length=15, default=' ')
    postcode = models.CharField(max_length=10, default=' ')
    street = models.CharField(max_length=196, default=' ')
    street_optional = models.CharField(max_length=196, default=None, blank=True, null=True)
    building_name = models.CharField(max_length=196, default=None, blank=True, null=True)
    city = models.CharField(max_length=196, default=None, blank=True, null=True)
    state = models.CharField(max_length=196, default=None, blank=True, null=True)
    country = models.CharField(max_length=196, default='Singapore')
    default = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
   
    class Meta:
        db_table = 'customer_addresses'
        ordering = ["default"]

    def recipient_fullname(self):
        return str(self.recipient_first_name) + " " + str(self.recipient_last_name)

    def __str__(self):
        address = f"{self.recipient_fullname()}<br>{self.postcode}<br>"
        if self.state is not None:
            address += f"{self.state} "
        if self.city is not None:
            address += f"{self.city} "
        
        address += f"{self.street}<br>"

        if self.street_optional is not None:
            address += f"{self.street_optional} "
        if self.building_name is not None:
            address += f"{self.building_name} "

        address += f"<br>tel: {self.recipient_phone}"

        return address







