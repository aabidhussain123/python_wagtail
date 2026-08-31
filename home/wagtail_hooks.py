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
        /* Custom scrollbar and scroll behavior for the Wagtail admin sidebar */
        #wagtail-sidebar, [data-sidebar], .w-sidebar {
            scrollbar-width: thin !important;
        }
        #wagtail-sidebar::-webkit-scrollbar, [data-sidebar]::-webkit-scrollbar, .w-sidebar::-webkit-scrollbar {
            width: 6px;
        }
        #wagtail-sidebar::-webkit-scrollbar-thumb, [data-sidebar]::-webkit-scrollbar-thumb, .w-sidebar::-webkit-scrollbar-thumb {
            background-color: rgba(255, 255, 255, 0.2);
            border-radius: 3px;
        }
        #wagtail-sidebar::-webkit-scrollbar-track, [data-sidebar]::-webkit-scrollbar-track, .w-sidebar::-webkit-scrollbar-track {
            background: transparent;
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
    
    default_js = """
    <script>
        // Disable automatic scroll restoration by the browser
        if ('scrollRestoration' in history) {
            history.scrollRestoration = 'manual';
        }
        window.addEventListener("load", function() {
            setTimeout(function() {
                window.scrollTo(0, 0);
                if (document.documentElement) document.documentElement.scrollTop = 0;
                if (document.body) document.body.scrollTop = 0;
            }, 20);
        });
    </script>
    """
    if js:
        return mark_safe(default_js + f"<script>{js}</script>")
    return mark_safe(default_js)



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


from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet
from home.models import ProgramPlan

class ProgramPlanViewSet(SnippetViewSet):
    model = ProgramPlan
    icon = 'doc-full'
    menu_label = 'Program Plans'
    menu_name = 'program_plans'
    menu_order = 330
    add_to_admin_menu = True

register_snippet(ProgramPlanViewSet)


from home.models import RtiDisclosure

class RtiDisclosureViewSet(SnippetViewSet):
    model = RtiDisclosure
    icon = 'doc-full-inverse'
    menu_label = 'RTI Disclosures'
    menu_name = 'rti_disclosures'
    menu_order = 340
    add_to_admin_menu = True

register_snippet(RtiDisclosureViewSet)


from home.models import QuickLinksCarouselViewSet

register_snippet(QuickLinksCarouselViewSet)
