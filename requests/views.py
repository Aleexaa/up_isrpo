import qrcode
import base64
from io import BytesIO
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.db.models.functions import TruncMonth
from .models import Request, Comment
from users.models import User
from .forms import RequestForm, CommentForm

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Неверный логин или пароль')
    
    return render(request, 'requests/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {}
    
    if request.user.user_type == 'Заказчик':
        context['my_requests'] = Request.objects.filter(client=request.user)
    else:
        context['recent_requests'] = Request.objects.order_by('-startDate')[:10]
        
        completed = Request.objects.filter(
            requestStatus='Готова к выдаче',
            completionDate__isnull=False
        )
        total_completed = completed.count()
        
        total_days = 0
        for req in completed:
            delta = req.completionDate - req.startDate
            total_days += delta.days
        
        avg_time = round(total_days / total_completed, 1) if total_completed > 0 else 0
        
        tech_stats = Request.objects.values('homeTechType').annotate(
            count=Count('requestID')
        ).order_by('-count')[:5]
        
        status_stats = {
            'new': Request.objects.filter(requestStatus='Новая заявка').count(),
            'in_progress': Request.objects.filter(requestStatus='В процессе ремонта').count(),
            'ready': Request.objects.filter(requestStatus='Готова к выдаче').count(),
        }
        
        monthly_stats = Request.objects.annotate(
            month=TruncMonth('startDate')
        ).values('month').annotate(
            count=Count('requestID')
        ).order_by('-month')[:6]
        
        context['total_requests'] = Request.objects.count()
        context['masters_count'] = User.objects.filter(user_type='Мастер').count()
        context['completed_count'] = total_completed
        context['avg_repair_time'] = avg_time
        context['tech_stats'] = tech_stats
        context['status_stats'] = status_stats
        context['monthly_stats'] = monthly_stats
    
    return render(request, 'requests/dashboard.html', context)

def request_list(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    requests_list = Request.objects.all()
    client_name = request.GET.get('client_name')
    
    if client_name:
        requests_list = requests_list.filter(client__fio__icontains=client_name)
    
    return render(request, 'requests/request_list.html', {'requests': requests_list})

def request_detail(request, pk):
    if not request.user.is_authenticated:
        return redirect('login')
    
    request_obj = get_object_or_404(Request, pk=pk)
    
    if request.user.user_type == 'Заказчик' and request_obj.client != request.user:
        messages.error(request, 'Нет доступа к этой заявке')
        return redirect('dashboard')
    
    if request.user.user_type == 'Заказчик':
        comments = request_obj.comments.filter(comment_type='client')
    else:
        comments = request_obj.comments.all()
    
    masters = User.objects.filter(user_type='Мастер')
    
    if request.user.user_type in ['Оператор', 'Администратор', 'Менеджер по качеству']:
        masters = User.objects.filter(user_type='Мастер')
    else:
        masters = None
    
    if request.method == 'POST' and request.user.user_type in ['Мастер', 'Менеджер по качеству']:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.master = request.user
            comment.request = request_obj
            
            comment_type = request.POST.get('comment_type', 'internal')
            if comment_type == 'client' and request.user.user_type == 'Менеджер по качеству':
                comment.comment_type = 'client'
            else:
                comment.comment_type = 'internal'
            
            comment.save()
            messages.success(request, 'Комментарий добавлен')
            return redirect('request_detail', pk=pk)
    else:
        form = CommentForm()
    
    context = {
        'request_obj': request_obj,
        'comments': comments,
        'form': form,
        'masters': masters,
        'is_client': request.user.user_type == 'Заказчик'
    }
    return render(request, 'requests/request_detail.html', context)

def request_create(request):
    if request.user.user_type not in ['Оператор', 'Администратор']:
        messages.error(request, 'Нет прав для создания заявок')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            new_request = form.save(commit=False)
            new_request.startDate = date.today()
            new_request.requestStatus = 'Новая заявка'
            new_request.save()
            messages.success(request, f'Заявка #{new_request.requestID} создана')
            return redirect('request_detail', pk=new_request.requestID)
    else:
        form = RequestForm()
    
    return render(request, 'requests/request_form.html', {'form': form, 'title': 'НОВАЯ ЗАЯВКА'})

def request_update(request, pk):
    if request.user.user_type not in ['Оператор', 'Администратор']:
        messages.error(request, 'Нет прав для редактирования')
        return redirect('dashboard')
    
    request_obj = get_object_or_404(Request, pk=pk)
    
    if request.method == 'POST':
        form = RequestForm(request.POST, instance=request_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Заявка обновлена')
            return redirect('request_detail', pk=pk)
    else:
        form = RequestForm(instance=request_obj)
    
    return render(request, 'requests/request_form.html', {'form': form, 'title': 'РЕДАКТИРОВАНИЕ'})

def request_delete(request, pk):
    if request.user.user_type not in ['Оператор', 'Администратор']:
        messages.error(request, 'Нет прав для удаления')
        return redirect('dashboard')
    
    if request.method == 'POST':
        request_obj = get_object_or_404(Request, pk=pk)
        request_id = request_obj.requestID
        request_obj.delete()
        messages.success(request, f'Заявка #{request_id} удалена')
    
    return redirect('request_list')

def assign_master(request, pk):
    if request.user.user_type not in ['Оператор', 'Администратор', 'Менеджер по качеству']:
        messages.error(request, 'Нет прав для назначения мастера')
        return redirect('dashboard')
    
    if request.method == 'POST':
        request_obj = get_object_or_404(Request, pk=pk)
        master_id = request.POST.get('master_id')
        
        if master_id:
            master = get_object_or_404(User, id=master_id, user_type='Мастер')
            request_obj.master = master
            request_obj.requestStatus = 'В процессе ремонта'
            request_obj.save()
            messages.success(request, f'Мастер {master.fio} назначен')
    
    return redirect('request_detail', pk=pk)

def extend_deadline(request, pk):
    if request.user.user_type != 'Менеджер по качеству':
        messages.error(request, 'Нет прав для продления срока')
        return redirect('dashboard')
    
    if request.method == 'POST':
        request_obj = get_object_or_404(Request, pk=pk)
        new_deadline = request.POST.get('new_deadline')
        comment_text = request.POST.get('comment', '')
        
        request_obj.deadline_extended = True
        request_obj.deadline_extended_date = new_deadline
        request_obj.extension_approved = False
        request_obj.save()
        
        comment = Comment.objects.create(
            message=f'⚠️ Запрошено продление срока до {new_deadline}. Ожидается согласование с клиентом. {comment_text}',
            master=request.user,
            request=request_obj,
            comment_type='client'
        )
        
        messages.success(request, 'Запрос на продление срока отправлен клиенту')
    
    return redirect('request_detail', pk=pk)

def approve_extension(request, pk):
    if request.user.user_type != 'Заказчик':
        messages.error(request, 'Нет прав для согласования')
        return redirect('dashboard')
    
    request_obj = get_object_or_404(Request, pk=pk)
    
    if request_obj.client != request.user:
        messages.error(request, 'Это не ваша заявка')
        return redirect('dashboard')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            request_obj.extension_approved = True
            request_obj.save()
            
            Comment.objects.create(
                message=f'✅ Клиент согласовал продление срока до {request_obj.deadline_extended_date}',
                master=request.user,
                request=request_obj,
                comment_type='internal'
            )
            messages.success(request, 'Вы согласовали продление срока')
        
        elif action == 'reject':
            request_obj.deadline_extended = False
            request_obj.deadline_extended_date = None
            request_obj.extension_approved = False
            request_obj.save()
            
            Comment.objects.create(
                message=f'❌ Клиент отклонил продление срока',
                master=request.user,
                request=request_obj,
                comment_type='internal'
            )
            messages.warning(request, 'Вы отклонили продление срока')
    
    return redirect('request_detail', pk=pk)

def generate_qr(request, pk):
    request_obj = get_object_or_404(Request, pk=pk)
    
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdhZcExx6LSIXxk0ub55mSu-WIh23WYdGG9HY5EZhLDo7P8eA/viewform"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(form_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_code = base64.b64encode(buffer.getvalue()).decode()
    
    if request.user.user_type == 'Заказчик':
        comments = request_obj.comments.filter(comment_type='client')
    else:
        comments = request_obj.comments.all()
    
    masters = User.objects.filter(user_type='Мастер')
    
    context = {
        'request_obj': request_obj,
        'comments': comments,
        'form': CommentForm(),
        'masters': masters,
        'qr_code': qr_code,
        'is_client': request.user.user_type == 'Заказчик'
    }
    
    return render(request, 'requests/request_detail.html', context)