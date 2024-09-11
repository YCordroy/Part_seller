from random import choice, randrange

from django.core.management.base import BaseCommand

from parts.models import Location, Mark, Model, Part, User

part_names = (
    "Амортизатор задний",
    "Привод правый передний",
    "Блок управления двигателем",
    "Форсунка топливная",
    "Подушка безопасности пассажира"
)

colors = (
    "Белый",
    "Чёрный",
    "Синий",
    "Красный",
    "Серый"
)


class Command(BaseCommand):
    help = 'Создание записей в таблице Part'

    @staticmethod
    def get_json_data():
        # Генерирует случайный json_data
        json_data = {}
        if choice((True, False)):
            json_data["color"] = choice(colors)
        if choice((True, False)):
            json_data["is_new_part"] = choice((True, False))
        return json_data

    def handle(self, *args, **options):
        parts = []
        models = Model.objects.all()
        mark_model = [(model.mark_id, model.id) for model in models]
        users = User.objects.all()
        locations = Location.objects.all()

        for _ in range(500):
            name = choice(part_names)
            mark, model = choice(mark_model)
            author = choice(users)
            location = choice(locations)
            contact = '12345'
            description = 'test'
            price = float(randrange(1000, 50001, 500))
            json_data = self.get_json_data()

            part = Part(
                name=name,
                mark_id=mark,
                model_id=model,
                price=price,
                json_data=json_data,
                author=author,
                location=location,
                contact=contact,
                description=description
            )
            parts.append(part)
        Part.objects.bulk_create(parts)
