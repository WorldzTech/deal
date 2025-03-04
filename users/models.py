import uuid

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from django.utils import timezone


# Create your models here.
class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, mobilePhone, password, firstname='Poop', email='None', **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not mobilePhone:
            raise ValueError("The phone must be set")
        if not email:
            raise ValueError("The email must be set")
        email = self.normalize_email(email)
        user = self.model(mobilePhone=mobilePhone, email=email, firstname=firstname, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, mobilePhone, password, firstname='Poop', **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(mobilePhone=mobilePhone, password=password, firstname=firstname, **extra_fields)


class DealUser(AbstractBaseUser, PermissionsMixin):
    mobilePhone = models.CharField(max_length=12, unique=True)
    firstname = models.CharField(max_length=255)
    surname = models.CharField(max_length=255, blank=True, null=True)
    lastname = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    size = models.CharField(max_length=3, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)

    phoneConfirmed = models.BooleanField(default=False)

    cart = models.JSONField(null=True, blank=True, default={})

    country = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    tg = models.CharField(max_length=255, null=True, blank=True)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    favorites = models.ManyToManyField('core.Product', blank=True, null=True)

    joined_at = models.DateTimeField(auto_now_add=True, default=timezone.now)

    USERNAME_FIELD = 'mobilePhone'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.mobilePhone
