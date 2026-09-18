from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin
from django.http import Http404
from django.shortcuts import redirect

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.models import Page
from wagtail.views import serve as wagtail_serve

from search import views as search_views
from home import views as home_views


def custom_wagtail_serve(request, path=""):
    """
    Enhanced Wagtail page server with smart nested slug routing fallback.
    If a nested URL path (e.g., /national-rural-health-missionnrhm/about-nhm/)
    is requested and Wagtail's strict tree lookup raises 404,
    this automatically resolves and redirects to the matching live page.
    """
    try:
        return wagtail_serve(request, path)
    except Http404:
        slugs = [s for s in (path or "").strip("/").split("/") if s]
        if slugs:
            leaf_slug = slugs[-1]
            target_page = Page.objects.live().public().exclude(depth__lte=2).filter(slug=leaf_slug).first()
            if target_page:
                try:
                    return redirect(target_page.url)
                except Exception:
                    return target_page.specific.serve(request)
        raise


urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("api/quick-search/", search_views.quick_search, name="quick_search"),
    path("api/set-theme/", home_views.set_user_theme, name="set_user_theme"),
]



if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # Custom catch-all that resolves tree pages and fallback nested slugs seamlessly
    re_path(r"^((?:[\w\-]+/)*)$", custom_wagtail_serve, name="wagtail_serve"),
]
