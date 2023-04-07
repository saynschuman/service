import os
import time


def path_and_rename(instance, filename):
    upload_to = 'material'
    base_filename, file_extension = os.path.splitext(filename)
    if len(base_filename) > 50:
        base_filename = base_filename[:50]

    new_filename = '{}_{}.{}'.format(time.time(), base_filename, file_extension)
    return os.path.join(upload_to, new_filename)
