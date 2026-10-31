"""Private local media storage; files are served only through an access-checked view."""
import uuid
from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class PrivateVideoStorage(FileSystemStorage):
    def __init__(self):
        super().__init__(location=settings.PRIVATE_VIDEO_ROOT, base_url=None)

    def url(self, name):
        raise ValueError('Private video files do not have a direct URL.')


def video_upload_path(instance, filename):
    return f'videos/{uuid.uuid4().hex}{Path(filename).suffix.lower()}'
