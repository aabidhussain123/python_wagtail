from django.http import JsonResponse
from django.shortcuts import redirect
from wagtail.models import Page


def quick_search(request):
    """
    Live autocomplete search API for the header search bar.
    Returns JSON list of matching pages.
    """
    q = (request.GET.get("q") or request.GET.get("query") or "").strip()
    if not q:
        return JsonResponse({"results": []})

    live_pages = Page.objects.live().public().exclude(depth__lte=2)

    # 1. Exact/Substring title matches
    title_matches = list(live_pages.filter(title__icontains=q)[:8])
    seen_ids = set(p.id for p in title_matches)

    # 2. Wagtail search for body/content matches
    try:
        wagtail_matches = [p for p in live_pages.search(q)[:8] if p.id not in seen_ids]
    except Exception:
        wagtail_matches = []

    combined = (title_matches + wagtail_matches)[:8]

    results = []
    for p in combined:
        try:
            url = p.url
        except Exception:
            url = f"/{p.slug}/"
        results.append({
            "id": p.id,
            "title": p.title,
            "url": url,
            "type": p.specific_class.__name__ if hasattr(p, "specific_class") and p.specific_class else "Page",
        })

    return JsonResponse({"results": results})


def search(request):
    """
    Direct navigation search:
    If a query is submitted, immediately redirects the user to the matching page.
    """
    search_query = (request.GET.get("query") or "").strip()
    if search_query:
        # 1. Check exact title match
        exact = Page.objects.live().public().exclude(depth__lte=2).filter(title__iexact=search_query).first()
        if exact:
            return redirect(exact.url)

        # 2. Check substring title match
        sub_match = Page.objects.live().public().exclude(depth__lte=2).filter(title__icontains=search_query).first()
        if sub_match:
            return redirect(sub_match.url)

        # 3. Wagtail full-text search top result
        try:
            top_match = Page.objects.live().public().exclude(depth__lte=2).search(search_query).first()
            if top_match:
                return redirect(top_match.url)
        except Exception:
            pass

    return redirect("/")
