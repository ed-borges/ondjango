"""Validate lesson video URLs and produce safe, canonical playback sources.

No URL is fetched by the server. Only supported video providers or direct
HTTPS MP4/WebM links are accepted; authors remain responsible for access and
licensing of the media they provide.
"""
import re
from urllib.parse import parse_qs, urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


YOUTUBE_ID = re.compile(r'^[A-Za-z0-9_-]{11}$')
VIMEO_ID = re.compile(r'^[0-9]{1,20}$')
VALIDATE_HTTPS = URLValidator(schemes=['https'])
VIDEO_ERROR = 'Usa um link HTTPS do YouTube, Vimeo ou um ficheiro direto MP4/WebM.'


def video_source(value):
    """Return an allowlisted playback URL and type, or None if invalid/empty."""
    if not value or not isinstance(value, str):
        return None
    try:
        VALIDATE_HTTPS(value)
        parts = urlsplit(value)
        if parts.scheme != 'https' or not parts.hostname or parts.username or parts.password or parts.port not in (None, 443):
            return None
        host = parts.hostname.lower()
        path = parts.path
        video_id = None
        if host in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            if path == '/watch':
                values = parse_qs(parts.query).get('v', [])
                video_id = values[0] if len(values) == 1 else None
            elif path.startswith('/embed/') or path.startswith('/shorts/'):
                video_id = path.split('/')[-1]
        elif host == 'youtu.be':
            video_id = path.removeprefix('/') if path.count('/') == 1 else None
        if video_id and YOUTUBE_ID.fullmatch(video_id):
            return {'kind': 'youtube', 'url': f'https://www.youtube-nocookie.com/embed/{video_id}'}
        if host in ('vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
            # Private/unlisted Vimeo URLs require access parameters we do not support.
            if 'h' in parse_qs(parts.query):
                return None
            match = re.fullmatch(r'/(?:video/)?([0-9]{1,20})/?', path)
            if match and VIMEO_ID.fullmatch(match.group(1)):
                return {'kind': 'vimeo', 'url': f'https://player.vimeo.com/video/{match.group(1)}'}
        # Do not treat malformed provider links as direct files.
        if host in ('youtube.com', 'www.youtube.com', 'm.youtube.com', 'youtu.be', 'vimeo.com', 'www.vimeo.com', 'player.vimeo.com'):
            return None
        if path.lower().endswith(('.mp4', '.webm')) and not parts.fragment:
            return {'kind': 'file', 'url': value}
    except (ValidationError, ValueError, TypeError):
        return None
    return None


def validate_video_url(value):
    if value and not video_source(value):
        raise ValidationError(VIDEO_ERROR, code='invalid_video_url')
