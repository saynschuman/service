from django.core.management.base import BaseCommand
from backend.courses.models import Passing
from tqdm import tqdm


class Command(BaseCommand):
    help = 'Delete old passings'

    def handle(self, *args, **kwargs):
        all_passing = Passing.objects.all().select_related('task__material__course')
        to_delete = []
        for passing in tqdm(all_passing, desc='check course'):
            user = passing.user
            course = passing.task.material.course
            if user not in course.users.all():
                to_delete.append(passing.id)

        Passing.objects.filter(pk__in=to_delete).delete()

        self.stdout.write(self.style.WARNING(f'All passing fixed.'))
