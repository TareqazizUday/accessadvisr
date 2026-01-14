from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json


class RegisterView(View):
    """Handle user registration with validation"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            username = data.get('username', '').strip()
            email = data.get('email', '').strip()
            password = data.get('password', '')
            confirm_password = data.get('confirm_password', '')
            
            # Validation
            errors = {}
            
            # Username validation
            if not username:
                errors['username'] = 'Username is required'
            elif len(username) < 3:
                errors['username'] = 'Username must be at least 3 characters long'
            elif User.objects.filter(username=username).exists():
                errors['username'] = 'Username already exists'
            
            # Email validation
            if not email:
                errors['email'] = 'Email is required'
            elif '@' not in email or '.' not in email:
                errors['email'] = 'Please enter a valid email address'
            elif User.objects.filter(email=email).exists():
                errors['email'] = 'Email already registered'
            
            # Password validation
            if not password:
                errors['password'] = 'Password is required'
            elif len(password) < 8:
                errors['password'] = 'Password must be at least 8 characters long'
            else:
                try:
                    # Use Django's password validators
                    validate_password(password)
                except ValidationError as e:
                    errors['password'] = ', '.join(e.messages)
            
            # Confirm password validation
            if not confirm_password:
                errors['confirm_password'] = 'Please confirm your password'
            elif password != confirm_password:
                errors['confirm_password'] = 'Passwords do not match'
            
            # If there are validation errors, return them
            if errors:
                return JsonResponse({
                    'success': False,
                    'errors': errors
                }, status=400)
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            
            # Log the user in
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Registration successful!',
                'user': {
                    'username': user.username,
                    'email': user.email
                }
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'errors': {'general': 'Invalid data format'}
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'general': str(e)}
            }, status=500)


class LoginView(View):
    """Handle user login"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            username = data.get('username', '').strip()
            password = data.get('password', '')
            
            if not username or not password:
                return JsonResponse({
                    'success': False,
                    'errors': {'general': 'Username and password are required'}
                }, status=400)
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                return JsonResponse({
                    'success': True,
                    'message': 'Login successful!',
                    'user': {
                        'username': user.username,
                        'email': user.email
                    }
                })
            else:
                return JsonResponse({
                    'success': False,
                    'errors': {'general': 'Invalid username or password'}
                }, status=401)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'errors': {'general': 'Invalid data format'}
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'errors': {'general': str(e)}
            }, status=500)


class LogoutView(View):
    """Handle user logout"""
    
    def get(self, request):
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful!'
        })
    
    def post(self, request):
        logout(request)
        return JsonResponse({
            'success': True,
            'message': 'Logout successful!'
        })
