from django.db import models
from users.models import User

class Request(models.Model):
    STATUS_CHOICES = [
        ('Новая заявка', 'Новая заявка'),
        ('В процессе ремонта', 'В процессе ремонта'),
        ('Готова к выдаче', 'Готова к выдаче'),
    ]
    
    TECH_TYPE_CHOICES = [
        ('Холодильник', 'Холодильник'),
        ('Стиральная машина', 'Стиральная машина'),
        ('Фен', 'Фен'),
        ('Тостер', 'Тостер'),
        ('Мультиварка', 'Мультиварка'),
        ('Плита', 'Плита'),
        ('Микроволновка', 'Микроволновка'),
    ]
    
    requestID = models.AutoField(primary_key=True)
    startDate = models.DateField()
    homeTechType = models.CharField(max_length=50, choices=TECH_TYPE_CHOICES)
    homeTechModel = models.CharField(max_length=100)
    problemDescryption = models.TextField()
    requestStatus = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Новая заявка')
    completionDate = models.DateField(null=True, blank=True)
    repairParts = models.TextField(blank=True, null=True)
    deadline_extended = models.BooleanField(default=False)
    deadline_extended_date = models.DateField(null=True, blank=True)
    extension_approved = models.BooleanField(default=False)
    
    master = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='master_requests'
    )
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='client_requests'
    )
    
    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-startDate']
    
    def __str__(self):
        return f"Заявка #{self.requestID}"


class Comment(models.Model):
    COMMENT_TYPES = [
        ('internal', 'Внутренний'),
        ('client', 'Для клиента'),
    ]
    
    commentID = models.AutoField(primary_key=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    comment_type = models.CharField(max_length=20, choices=COMMENT_TYPES, default='internal')
    
    master = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    request = models.ForeignKey(
        Request,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Комментарий #{self.commentID}"