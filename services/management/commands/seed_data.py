from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import Service, ServiceCategory
from orders.models import Order
from services.signals import invalidate_top_5_cache


class Command(BaseCommand):
    help = "Наполняет базу данных тестовыми мастерами, услугами и заявками для проекта ТОП СТР Enterprise"

    def handle(self, *args, **options):
        self.stdout.write("Начало наполнения базы данных ТОП СТР...")

        # 1. Создаем Администратора сервиса
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@topstr.enterprise",
                "first_name": "Администратор",
                "last_name": "Сервиса",
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Создан администратор: admin / admin123"))

        # 2. Создаем тестовых мастеров
        masters_info = [
            ("master_santehnik", "Азамат", "Сантехников", "santeh@topstr.kg"),
            ("master_cleaner", "Айсулуу", "Клинингова", "clean@topstr.kg"),
            ("master_tutor", "Бакыт", "Учитель", "tutor@topstr.kg"),
            ("master_it", "Данияр", "Программист", "dev@topstr.kg"),
            ("master_beauty", "Нуржамал", "Стилист", "beauty@topstr.kg"),
        ]

        masters = {}
        for username, first_name, last_name, email in masters_info:
            master, c = User.objects.get_or_create(
                username=username,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": email,
                }
            )
            if c:
                master.set_password("master123")
                master.save()
            masters[username] = master

        self.stdout.write(self.style.SUCCESS("Созданы специалисты с паролем 'master123'."))

        # 3. Создаем каталог услуг
        services_data = [
            {
                "title": "Установка стиральной машины",
                "description": "Профессиональное подключение к водопроводу и канализации, выравнивание по уровню, первый запуск и проверка на протечки.",
                "category": ServiceCategory.REPAIR,
                "price": Decimal("2500.00"),
                "discount": 10,
                "is_active": True,
                "author": masters["master_santehnik"],
            },
            {
                "title": "Устранение засоров труб любой сложности",
                "description": "Механическая и гидродинамическая прочистка труб, устранение неприятных запахов, гарантия чистоты.",
                "category": ServiceCategory.REPAIR,
                "price": Decimal("1800.00"),
                "discount": 0,
                "is_active": True,
                "author": masters["master_santehnik"],
            },
            {
                "title": "Генеральная уборка квартир и офисов",
                "description": "Комплексная влажная и сухая уборка всех комнат, чистка санузла, кухни, бытовой техники сертифицированными эко-средствами.",
                "category": ServiceCategory.CLEANING,
                "price": Decimal("4500.00"),
                "discount": 15,
                "is_active": True,
                "author": masters["master_cleaner"],
            },
            {
                "title": "Мойка панорамных окон и фасадов",
                "description": "Качественная мойка окон без разводов на любой высоте, мытье рам, подоконников и москитных сеток.",
                "category": ServiceCategory.CLEANING,
                "price": Decimal("3000.00"),
                "discount": 20,
                "is_active": True,
                "author": masters["master_cleaner"],
            },
            {
                "title": "Подготовка к ОРТ и математика для школьников",
                "description": "Индивидуальные занятия с разбором тестовых заданий, устранение пробелов в знаниях, гарантия высокого балла.",
                "category": ServiceCategory.EDUCATION,
                "price": Decimal("1200.00"),
                "discount": 10,
                "is_active": True,
                "author": masters["master_tutor"],
            },
            {
                "title": "Разговорный английский и подготовка к IELTS",
                "description": "Практика речи с сертифицированным преподавателем (IELTS 8.5), подготовка к собеседованиям за рубежом.",
                "category": ServiceCategory.EDUCATION,
                "price": Decimal("1600.00"),
                "discount": 0,
                "is_active": True,
                "author": masters["master_tutor"],
            },
            {
                "title": "Создание современных сайтов и веб-сервисов",
                "description": "Разработка адаптивных сайтов, интернет-магазинов и API на Python Django под ключ.",
                "category": ServiceCategory.IT,
                "price": Decimal("25000.00"),
                "discount": 20,
                "is_active": True,
                "author": masters["master_it"],
            },
            {
                "title": "Настройка Wi-Fi роутеров и локальных сетей",
                "description": "Быстрая настройка стабильного интернета дома и в офисе, прокладка кабеля, защита сети.",
                "category": ServiceCategory.IT,
                "price": Decimal("2000.00"),
                "discount": 5,
                "is_active": True,
                "author": masters["master_it"],
            },
            {
                "title": "Вечерний и свадебный макияж с выездом",
                "description": "Стойкий премиальный макияж на профессиональной косметике с выездом на дом в удобное для вас время.",
                "category": ServiceCategory.BEAUTY,
                "price": Decimal("3500.00"),
                "discount": 10,
                "is_active": True,
                "author": masters["master_beauty"],
            },
        ]

        created_services = []
        for s_data in services_data:
            service, s_created = Service.objects.get_or_create(
                title=s_data["title"],
                defaults=s_data
            )
            created_services.append(service)

        self.stdout.write(self.style.SUCCESS(f"Создано {len(created_services)} услуг в каталоге."))

        # 4. Создаем несколько тестовых заявок
        if created_services:
            orders_data = [
                {
                    "service": created_services[0],  # стиральная машина
                    "client_name": "Канатбек",
                    "client_phone": "+996555112233",
                    "comment": "Ждем завтра в 14:00, адрес ул. Киевская 120, кв 45."
                },
                {
                    "service": created_services[0],  # стиральная машина
                    "client_name": "Елена",
                    "client_phone": "+996700889900",
                    "comment": "Срочно нужно сегодня вечером!"
                },
                {
                    "service": created_services[2],  # уборка
                    "client_name": "Нурлан",
                    "client_phone": "+996777334455",
                    "comment": "Трешка 90 кв.м, суббота утро."
                },
            ]
            for o_data in orders_data:
                Order.objects.get_or_create(
                    client_phone=o_data["client_phone"],
                    service=o_data["service"],
                    defaults=o_data
                )
            self.stdout.write(self.style.SUCCESS(f"Создано {len(orders_data)} тестовых заявок."))

        # Сбрасываем кэш, чтобы топ-5 был свежим
        invalidate_top_5_cache()

        self.stdout.write(self.style.SUCCESS("\nGotovo! Baza dannyh TOP STR Enterprise uspeshno zapolnena."))
        self.stdout.write("Uchetnye zapisi:")
        self.stdout.write("  Admin: admin / admin123")
        self.stdout.write("  Mastera: master_santehnik / master123, master_cleaner / master123, master_tutor / master123")
