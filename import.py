import os
import django
import csv
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from users.models import User
from requests.models import Request, Comment

def import_data():
    print("=" * 50)
    print("НАЧАЛО ИМПОРТА")
    print("=" * 50)
    
    print("\n1. Импорт пользователей:")
    with open('data/users.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                user = User(
                    id=int(row['userID']),
                    username=row['login'],
                    fio=row['fio'],
                    phone=row['phone'],
                    user_type=row['type'],
                    email=f"{row['login']}@example.com",
                    is_staff=row['type'] in ['Администратор', 'Оператор', 'Менеджер']
                )
                user.set_password(row['password'])
                user.save()
                print(f"  ✓ {row['fio']} (ID: {row['userID']}, тип: {row['type']})")
            except Exception as e:
                print(f"  ✗ Ошибка при создании {row['fio']}: {e}")
  
    print("\n2. Импорт заявок:")
    with open('data/requests.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                client = User.objects.get(id=int(row['clientID']))
               
                master = None
                if row['masterID'] and row['masterID'] != 'null':
                    master = User.objects.get(id=int(row['masterID']))
                
                completion = None
                if row['completionDate'] and row['completionDate'] != 'null':
                    completion = datetime.strptime(row['completionDate'], '%Y-%m-%d').date()
               
                request = Request(
                    requestID=int(row['requestID']),
                    startDate=datetime.strptime(row['startDate'], '%Y-%m-%d').date(),
                    homeTechType=row['homeTechType'],
                    homeTechModel=row['homeTechModel'],
                    problemDescryption=row['problemDescryption'],
                    requestStatus=row['requestStatus'],
                    completionDate=completion,
                    repairParts=row['repairParts'] if row['repairParts'] else '',
                    master=master,
                    client=client
                )
                request.save()
                print(f"  ✓ Заявка #{row['requestID']} (клиент: {client.fio})")
            except User.DoesNotExist:
                print(f"  ✗ Заявка #{row['requestID']}: клиент с ID {row['clientID']} не найден")
            except Exception as e:
                print(f"  ✗ Заявка #{row['requestID']}: {e}")
   
    print("\n3. Импорт комментариев:")
    with open('data/comments.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                master = User.objects.get(id=int(row['masterID']))
                request = Request.objects.get(requestID=int(row['requestID']))
                
                comment = Comment(
                    commentID=int(row['commentID']),
                    message=row['message'],
                    master=master,
                    request=request
                )
                comment.save()
                print(f"  ✓ Комментарий #{row['commentID']} к заявке #{row['requestID']}")
            except Exception as e:
                print(f"  ✗ Комментарий #{row['commentID']}: {e}")
    
    print("\n" + "=" * 50)
    print("ИМПОРТ ЗАВЕРШЕН")
    print("=" * 50)
    
    print(f"\nИтоги:")
    print(f"  Пользователей: {User.objects.count()}")
    print(f"  Заявок: {Request.objects.count()}")
    print(f"  Комментариев: {Comment.objects.count()}")

if __name__ == '__main__':
    import_data()