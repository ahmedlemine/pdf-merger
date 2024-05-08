from django.db import models

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin


class CustomUserManager(BaseUserManager):
    """a custom manager for the custom user model to override 'create' as per djoser recommendation
    and as part of the whole process of creating a custom user model.
    """

    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)

        return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """a custom user model to allow for things like:
    1- defining USERNAME_FIELD and REQUIRED_FIELDS for djoser base endpoints to work (user creation and mange.).
    2- register and login using email instead of username.
    3- adding custom fields to the user model in future as needed.
    """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "user"

    def __str__(self):
        return self.email
