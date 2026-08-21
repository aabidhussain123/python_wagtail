from django.utils.safestring import mark_safe
from wagtail import hooks
from home.models import AdminBrandingSettings

@hooks.register('insert_global_admin_css')
def global_admin_css():
    try:
        settings = AdminBrandingSettings.load()
        css = settings.custom_css
    except Exception:
        css = ""
    
    default_css = """
    <style>
        /* Default custom styling for left and right logos in Wagtail admin */
        .custom-admin-logo-left {
            max-height: 45px;
            width: auto;
            object-fit: contain;
            display: inline-block;
            vertical-align: middle;
        }
        .custom-admin-logo-right-container {
            position: fixed;
            top: 15px;
            right: 24px;
            z-index: 9999;
            pointer-events: none;
            display: flex;
            align-items: center;
        }
        .custom-admin-logo-right-container img {
            max-height: 40px;
            width: auto;
            object-fit: contain;
            display: block;
        }
    </style>
    """
    if css:
        return mark_safe(default_css + f"<style>{css}</style>")
    return mark_safe(default_css)

@hooks.register('insert_global_admin_js')
def global_admin_js():
    try:
        settings = AdminBrandingSettings.load()
        js = settings.custom_js
    except Exception:
        js = ""
    if js:
        return mark_safe(f"<script>{js}</script>")
    return ""


# --- CUSTOM ADMIN MENUS FOR NEWS, NOTICES, & GOVT ORDERS ---

from wagtail.admin.viewsets.pages import PageListingViewSet
from home.models import NewsPage, NoticePage, GovtOrderPage

class NewsPageListingViewSet(PageListingViewSet):
    model = NewsPage
    icon = 'newspaper'
    menu_label = 'News Articles'
    menu_order = 300
    add_to_admin_menu = True

class NoticePageListingViewSet(PageListingViewSet):
    model = NoticePage
    icon = 'warning'
    menu_label = 'Official Notices'
    menu_order = 310
    add_to_admin_menu = True

class GovtOrderPageListingViewSet(PageListingViewSet):
    model = GovtOrderPage
    icon = 'doc-full'
    menu_label = 'Government Orders'
    menu_order = 320
    add_to_admin_menu = True

@hooks.register('register_admin_viewset')
def register_news_page_listing_viewset():
    return NewsPageListingViewSet('news_articles')

@hooks.register('register_admin_viewset')
def register_notice_page_listing_viewset():
    return NoticePageListingViewSet('official_notices')

@hooks.register('register_admin_viewset')
def register_govt_order_page_listing_viewset():
    return GovtOrderPageListingViewSet('govt_orders')

