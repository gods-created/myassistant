from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import UserManager

class AdminManager(UserManager):
    def validate_admin(self, email, password) -> bool:
        user = self.filter(email=email).only('password', 'is_staff').first()
        if not user:
            return False
        
        if not check_password(password, user.password) or not user.is_staff:
            return False
        
        return True
