from datetime import datetime
from django.core.exceptions import ValidationError


def validate_past_date(date):
        if datetime.now().date() > date:
            raise ValidationError("Past date is not accepted")