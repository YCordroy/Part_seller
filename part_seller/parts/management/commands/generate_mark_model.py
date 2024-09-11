from django.core.management.base import BaseCommand

from parts.models import Mark, Model

marks = (
    ("Honda", "Япония"),
    ("Toyota", "Япония"),
    ("Mazda", "Япония"),
    ("Kia", "Корея"),
    ("Audi", "Германия")
)

models = (
    ("Civic", 1),
    ("Fit", 1),
    ("Accord", 1),
    ("Stepwgn", 1),
    ("CR-V", 1),
    ("Corolla", 2),
    ("Prius", 2),
    ("Yaris", 2),
    ("Aqua", 2),
    ("Vitz", 2),
    ("Mazda 3", 3),
    ("Mazda 6", 3),
    ("Mazda 2", 3),
    ("CX-30", 3),
    ("CX-50", 3),
    ("K5", 4),
    ("Rio", 4),
    ("Sportage", 4),
    ("Ceed", 4),
    ("Soul", 4),
    ("A4", 5),
    ("Q3", 5),
    ("A6", 5),
    ("A8", 5),
    ("A3", 5)

)


class Command(BaseCommand):

    def handle(self, *args, **options):
        for mark, country in marks:
            Mark(
                name=mark,
                producer_country_name=country
            ).save()
        for model, mark in models:
            Model(
                name=model,
                mark_id=mark
            ).save()
