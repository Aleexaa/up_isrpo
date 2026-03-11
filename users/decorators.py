from django.shortcuts import redirect
from django.contrib import messages

def role_required(allowed_roles=[]):
    """Декоратор для проверки роли пользователя"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.user_type in allowed_roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('dashboard')
        return wrapper
    return decorator

def master_required(view_func):
    """Только для мастеров"""
    return role_required(['Мастер'])(view_func)

def operator_required(view_func):
    """Только для операторов"""
    return role_required(['Оператор'])(view_func)

def manager_required(view_func):
    """Только для менеджеров"""
    return role_required(['Менеджер'])(view_func)

def client_required(view_func):
    """Только для заказчиков"""
    return role_required(['Заказчик'])(view_func)