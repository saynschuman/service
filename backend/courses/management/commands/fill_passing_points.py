from django.core.management.base import BaseCommand
from backend.courses.models import Passing
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Fill passing max_points and user_points fields'

    def handle(self, *args, **kwargs):
        passings = Passing.objects.all()

        for passing in tqdm(passings, desc='fill max_points'):
            passing.max_points = passing.task.get_questions_score()
            passing.save(update_fields=['max_points'])

        for passing in tqdm(passings.filter(finish_time__isnull=False), desc='fill user_points'):
            passing.user_points = passing._get_user_points()
            passing.save(update_fields=['user_points'])

        self.stdout.write(self.style.WARNING(f'All passing filled.'))
