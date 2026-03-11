from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    TYPE_CHOICES = [
        ('Администратор', 'Администратор'),
        ('Оператор', 'Оператор'),
        ('Мастер', 'Мастер'),
        ('Менеджер', 'Менеджер'),
        ('Менеджер по качеству', 'Менеджер по качеству'),
        ('Заказчик', 'Заказчик'),
    ]
    
    phone = models.CharField(max_length=20)
    user_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    fio = models.CharField(max_length=255)
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set'
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
    
    def __str__(self):
        return self.fio