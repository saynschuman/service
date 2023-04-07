from django.core.management.base import BaseCommand
from backend.courses.models import Passing


class Command(BaseCommand):
    help = 'Fix passing status after refactoring'

    def handle(self, *args, **kwargs):
        """
        PASSED = 0
        NOT_PASSED = 1
        ON_CHECK = 2

        PASSED_CHOICES = (
            (PASSED, 'Успешно'),
            (NOT_PASSED, 'Не пройдено'),
            (ON_CHECK, 'На проверке'),
        )

        PASSED = 0
        ON_CHECK = 1
        LIMIT = 2
        ATTEMPTS = 3
        SCORE = 4

        PASSED_CHOICES = (
            (PASSED, 'Тест пройден успешно'),
            (ON_CHECK, 'На проверке'),
            (LIMIT, 'Превышено допустимое время прохождения'),
            (ATTEMPTS, 'Превышено допустимое кол-во попыток'),
            (SCORE, 'Процент прохождения не набран'),
        )
        """
        all_passing = Passing.objects.all()
        for passing in all_passing:

            # Если пройдено (0) - оставляем как было
            if passing.success_passed == 0:
                continue

            # Если было на проверке (2) - мнеяем на 1
            if passing.success_passed == 2:
                passing.success_passed = 1
                passing.save()
                continue

            # Если было не пройдено (1)
            if passing.success_passed == 1:
                # И еще не закончено - ставим на проверке (1)
                if not passing.finish_time:
                    passing.success_passed = 1
                    passing.save()
                    continue
                else:
                    passing.check_passing(finish=False)

        self.stdout.write(self.style.WARNING(f'All passing fixed.'))
