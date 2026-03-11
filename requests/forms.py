from django import forms
from .models import Request, Comment
from users.models import User
from datetime import date

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['homeTechType', 'homeTechModel', 'problemDescryption', 'client', 'master']
        widgets = {
            'problemDescryption': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Опишите проблему...'}),
            'homeTechType': forms.Select(attrs={'class': 'form-control'}),
            'homeTechModel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Indesit DS 316 W'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'master': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['client'].queryset = User.objects.filter(user_type='Заказчик')
        self.fields['master'].queryset = User.objects.filter(user_type='Мастер')
        self.fields['master'].required = False
        self.fields['client'].label = 'Клиент'
        self.fields['homeTechType'].label = 'Тип техники'
        self.fields['homeTechModel'].label = 'Модель'
        self.fields['problemDescryption'].label = 'Описание проблемы'


class CommentForm(forms.ModelForm):
    comment_type = forms.ChoiceField(
        choices=[('internal', 'Внутренний комментарий'), ('client', 'Сообщение клиенту')],
        widget=forms.Select(attrs={'class': 'form-control mb-2'}),
        required=False,
        label='Тип комментария'
    )
    
    class Meta:
        model = Comment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Введите комментарий...'}),
        }
        labels = {
            'message': 'Комментарий'
        }