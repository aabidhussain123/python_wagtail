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



# --- CUSTOM ADMIN MENUS FOR PORTAL CONTENT ---

from wagtail.admin.viewsets.base import ViewSetGroup
from wagtail.admin.viewsets.pages import PageListingViewSet
from wagtail.admin.viewsets.model import ModelViewSet
from wagtail.snippets.models import register_snippet
from home.models import (
    NewsPage, 
    NoticePage, 
    GovtOrderPage, 
    ProgramPlan, 
    RtiDisclosure, 
    Download,
    QuickLinksCarouselViewSet
)

class NewsPageListingViewSet(PageListingViewSet):
    model = NewsPage
    name = 'news_articles'
    icon = 'newspaper'
    menu_label = 'News Articles'
    menu_order = 10
    add_to_admin_menu = False

class NoticePageListingViewSet(PageListingViewSet):
    model = NoticePage
    name = 'official_notices'
    icon = 'warning'
    menu_label = 'Official Notices'
    menu_order = 20
    add_to_admin_menu = False

class GovtOrderPageListingViewSet(PageListingViewSet):
    model = GovtOrderPage
    name = 'govt_orders'
    icon = 'doc-full'
    menu_label = 'Government Orders'
    menu_order = 30
    add_to_admin_menu = False

class ProgramPlanViewSet(ModelViewSet):
    model = ProgramPlan
    name = 'program_plans'
    icon = 'doc-full'
    menu_label = 'Program Plans'
    menu_order = 40
    add_to_admin_menu = False
    list_display = ['title', 'document', 'created_at']
    search_fields = ['title']

class RtiDisclosureViewSet(ModelViewSet):
    model = RtiDisclosure
    name = 'rti_disclosures'
    icon = 'doc-full-inverse'
    menu_label = 'RTI Disclosures'
    menu_order = 50
    add_to_admin_menu = False
    list_display = ['title', 'document', 'created_at']
    search_fields = ['title']

class DownloadViewSet(ModelViewSet):
    model = Download
    name = 'downloads'
    icon = 'download'
    menu_label = 'Downloads'
    menu_order = 60
    add_to_admin_menu = False
    list_display = ['title', 'subtitle', 'category', 'document', 'created_at']
    list_filter = ['category']
    search_fields = ['title', 'subtitle', 'category']

class PortalContentViewSetGroup(ViewSetGroup):
    menu_label = 'Portal Content'
    menu_icon = 'folder-open-inverse'
    menu_order = 300
    items = (
        NewsPageListingViewSet,
        NoticePageListingViewSet,
        GovtOrderPageListingViewSet,
        ProgramPlanViewSet,
        RtiDisclosureViewSet,
        DownloadViewSet,
    )

@hooks.register('register_admin_viewset')
def register_portal_content_viewset_group():
    return PortalContentViewSetGroup()


register_snippet(QuickLinksCarouselViewSet)



