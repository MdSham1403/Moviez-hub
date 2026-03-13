import hashlib
import time

from django.conf import settings


def generate_signed_url(video_path):
    expiry = int(time.time()) + settings.BUNNY_TOKEN_EXPIRY

    token_string = f"{settings.BUNNY_TOKEN_KEY}{video_path}{expiry}"
    token = hashlib.md5(token_string.encode()).hexdigest()

    signed_url = (
        f"{settings.BUNNY_CDN_BASE}{video_path}"
        f"?token={token}&expires={expiry}"
    )

    return signed_url