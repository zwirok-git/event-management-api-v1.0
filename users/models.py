from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


name_validator = RegexValidator(
    regex="^[A-Za-z]+(?:'[A-Za-z]+)*$",
    message="Only English letters and apostrophes are allowed."
)


class User(AbstractUser):
    first_name = models.CharField(
        max_length=150,
        validators=[name_validator]
    )
    last_name = models.CharField(
        max_length=150,
        validators=[name_validator]
    )

    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
