import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from home.models import THEME_PRESETS


@require_POST
def set_user_theme(request):
    """
    Session/cookie-based theme switcher for website visitors.
    Stores the user's chosen theme in their session or cookie.
    If the user is an admin/staff, optionally allows saving globally as well if requested.
    """
    try:
        data = json.loads(request.body)
        theme_key = (data.get('theme') or '').strip()
    except (ValueError, AttributeError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON body.'}, status=400)

    valid_keys = list(THEME_PRESETS.keys())
    if theme_key not in valid_keys:
        return JsonResponse(
            {'ok': False, 'error': f'Unknown theme "{theme_key}". Valid: {valid_keys}'},
            status=400,
        )

    # Save to user session
    request.session['user_theme'] = theme_key

    response = JsonResponse({
        'ok': True,
        'theme': theme_key,
        'variables': THEME_PRESETS[theme_key]
    })
    # Set cookie for persistence across sessions (30 days)
    response.set_cookie('user_theme', theme_key, max_age=30*24*60*60, samesite='Lax')
    return response
