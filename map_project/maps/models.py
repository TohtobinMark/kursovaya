# maps/models.py
from django.db import models
from django.contrib.auth.models import User


# Существующая модель Location (оставляем)
class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    latitude = models.FloatField(verbose_name="Широта")
    longitude = models.FloatField(verbose_name="Долгота")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


# НОВАЯ МОДЕЛЬ: Заявка на дистрибутив 1С
class DistributionRequest(models.Model):
    """Заявка на подключение дистрибутива 1С"""

    STATUS_CHOICES = [
        ('pending', 'Ожидание'),
        ('in_work', 'В работе'),
        ('completed', 'Подключено'),
        ('rejected', 'Отказано'),
    ]

    BUSINESS_TYPES = [
        ('retail', 'Розничная торговля'),
        ('wholesale', 'Оптовая торговля'),
        ('manufacturing', 'Производство'),
        ('services', 'Услуги'),
        ('cafe', 'Кафе/Ресторан'),
        ('other', 'Другое'),
    ]

    # Кто добавил
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='distribution_requests',
        verbose_name='Заявитель'
    )

    # Информация о предприятии
    company_name = models.CharField('Название предприятия', max_length=200)
    business_type = models.CharField('Сфера деятельности', max_length=50, choices=BUSINESS_TYPES)
    description = models.TextField('Описание деятельности', blank=True)

    # Контактные данные
    contact_person = models.CharField('Контактное лицо', max_length=100)
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')

    # Геоданные (где находится предприятие)
    latitude = models.FloatField('Широта')
    longitude = models.FloatField('Долгота')
    address = models.CharField('Адрес', max_length=300)
    city = models.CharField('Город', max_length=100)

    # Информация о потребностях
    employees_count = models.IntegerField('Количество сотрудников', default=1)
    need_1c_buh = models.BooleanField('Нужна 1С:Бухгалтерия', default=False)
    need_1c_trade = models.BooleanField('Нужна 1С:Управление торговлей', default=False)
    need_1c_salary = models.BooleanField('Нужна 1С:Зарплата и кадры', default=False)
    need_cloud = models.BooleanField('Интересует облачная версия', default=False)
    comment = models.TextField('Дополнительный комментарий', blank=True)

    # Статус заявки
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='pending')
    manager_comment = models.TextField('Комментарий менеджера', blank=True)

    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField('Дата обработки', null=True, blank=True)

    class Meta:
        verbose_name = 'Заявка на дистрибутив'
        verbose_name_plural = 'Заявки на дистрибутив'
        ordering = ['-created_at']

    def __str__(self):
        return f"Заявка #{self.id} - {self.company_name}"

    def get_status_color(self):
        colors = {
            'pending': 'warning',
            'in_work': 'info',
            'completed': 'success',
            'rejected': 'danger',
        }
        return colors.get(self.status, 'secondary')

    def get_status_display_ru(self):
        return dict(self.STATUS_CHOICES).get(self.status, self.status)


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=DistributionRequest)
def create_client_on_completed(sender, instance, **kwargs):
    """При изменении статуса заявки на 'completed' создаем клиента в Location"""
    if instance.status == 'completed':
        # Проверяем, нет ли уже такого клиента
        existing = Location.objects.filter(
            title=instance.company_name,
            latitude=instance.latitude,
            longitude=instance.longitude
        ).first()

        if not existing:
            # Создаем нового клиента
            Location.objects.create(
                user=instance.user,
                title=instance.company_name,
                description=f"Подключено по заявке #{instance.id}. Сфера: {instance.get_business_type_display()}",
                latitude=instance.latitude,
                longitude=instance.longitude
            )
            print(f"✅ Создан клиент {instance.company_name} из заявки #{instance.id}")