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

        /* --- Generic Dynamic Data Table (Pattern 2) Admin Numbering & Badges --- */
        
        /* 1. Columns List */
        [data-structblock-child="columns"] [data-streamfield-list-container],
        [data-contentpath="columns"] [data-streamfield-list-container] {
            counter-reset: gdt-col-counter;
        }
        [data-structblock-child="columns"] [data-streamfield-list-container] > [data-streamfield-child],
        [data-contentpath="columns"] [data-streamfield-list-container] > [data-streamfield-child] {
            counter-increment: gdt-col-counter;
        }
        [data-structblock-child="columns"] [data-streamfield-list-container] > [data-streamfield-child] .c-sf-block__type::before,
        [data-contentpath="columns"] [data-streamfield-list-container] > [data-streamfield-child] .c-sf-block__type::before {
            content: "Col #" counter(gdt-col-counter) " — ";
            font-weight: 700;
            color: #1d4ed8;
        }
        [data-structblock-child="columns"] [data-streamfield-list-container] > [data-streamfield-child] .w-field__label::before,
        [data-contentpath="columns"] [data-streamfield-list-container] > [data-streamfield-child] .w-field__label::before {
            content: "Column #" counter(gdt-col-counter) ": ";
            font-weight: 700;
            color: #1d4ed8;
        }

        /* 2. Rows List */
        [data-structblock-child="rows"] > div > [data-streamfield-list-container],
        [data-structblock-child="rows"] > [data-streamfield-list-container],
        [data-contentpath="rows"] > div > [data-streamfield-list-container],
        [data-contentpath="rows"] > [data-streamfield-list-container] {
            counter-reset: gdt-row-counter;
        }
        [data-structblock-child="rows"] > div > [data-streamfield-list-container] > [data-streamfield-child],
        [data-structblock-child="rows"] > [data-streamfield-list-container] > [data-streamfield-child],
        [data-contentpath="rows"] > div > [data-streamfield-list-container] > [data-streamfield-child],
        [data-contentpath="rows"] > [data-streamfield-list-container] > [data-streamfield-child] {
            counter-increment: gdt-row-counter;
        }
        [data-structblock-child="rows"] > div > [data-streamfield-list-container] > [data-streamfield-child] > .w-panel > .w-panel__header .c-sf-block__type::before,
        [data-structblock-child="rows"] > [data-streamfield-list-container] > [data-streamfield-child] > .w-panel > .w-panel__header .c-sf-block__type::before,
        [data-contentpath="rows"] > div > [data-streamfield-list-container] > [data-streamfield-child] > .w-panel > .w-panel__header .c-sf-block__type::before,
        [data-contentpath="rows"] > [data-streamfield-list-container] > [data-streamfield-child] > .w-panel > .w-panel__header .c-sf-block__type::before {
            content: "Row #" counter(gdt-row-counter) " — ";
            font-weight: 700;
            color: #047857;
        }

        /* 3. Row Cells List */
        [data-structblock-child="cell_values"] [data-streamfield-list-container],
        [data-contentpath="cell_values"] [data-streamfield-list-container] {
            counter-reset: gdt-cell-counter;
        }
        [data-structblock-child="cell_values"] [data-streamfield-list-container] > [data-streamfield-child],
        [data-contentpath="cell_values"] [data-streamfield-list-container] > [data-streamfield-child] {
            counter-increment: gdt-cell-counter;
        }
        [data-structblock-child="cell_values"] [data-streamfield-list-container] > [data-streamfield-child] .c-sf-block__type::before,
        [data-contentpath="cell_values"] [data-streamfield-list-container] > [data-streamfield-child] .c-sf-block__type::before {
            content: "Col #" counter(gdt-cell-counter) " — ";
            font-weight: 700;
            color: #b45309;
        }
        [data-structblock-child="cell_values"] [data-streamfield-list-container] > [data-streamfield-child] .w-field__label::before,
        [data-contentpath="cell_values"] [data-streamfield-list-container] > [data-streamfield-child] .w-field__label::before {
            content: "Column #" counter(gdt-cell-counter) " Value: ";
            font-weight: 700;
            color: #b45309;
        }

        /* Helper pill badge for dynamic column name display on row cells */
        .gdt-cell-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 3px 10px;
            border-radius: 6px;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 6px;
            line-height: 1.4;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .gdt-badge--info {
            background-color: #eff6ff;
            color: #1e40af;
            border: 1px solid #bfdbfe;
        }
        .gdt-badge--info strong {
            color: #1e3a8a;
            font-weight: 700;
        }
        .gdt-badge--warning {
            background-color: #fef2f2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        .gdt-badge--warning strong {
            color: #7f1d1d;
            font-weight: 700;
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

        // --- Generic Dynamic Data Table (Pattern 2) Dynamic Numbering & Column Labeling ---
        function updateGenericDataTables() {
            var rowsElements = document.querySelectorAll('[data-structblock-child="rows"], [data-contentpath="rows"]');
            rowsElements.forEach(function(rowsElem) {
                var tableContainer = rowsElem.closest('[data-streamfield-child], .w-panel__content, fieldset, form') || rowsElem.parentElement;
                if (!tableContainer) return;

                // 1. Gather column definitions
                var columnsElem = tableContainer.querySelector('[data-structblock-child="columns"], [data-contentpath="columns"]');
                var columnNames = [];
                if (columnsElem) {
                    var colItems = columnsElem.querySelectorAll('[data-streamfield-list-container] > [data-streamfield-child]');
                    colItems.forEach(function(colItem, idx) {
                        var colNum = idx + 1;
                        var input = colItem.querySelector('input[type="text"]');
                        var val = input ? (input.value || '').trim() : '';
                        columnNames.push(val || ('Column ' + colNum));

                        var headingText = colItem.querySelector('[data-panel-heading-text]');
                        if (headingText) {
                            var disp = val ? ('Col #' + colNum + ': ' + val) : ('Col #' + colNum);
                            if (headingText.textContent !== disp) {
                                headingText.textContent = disp;
                            }
                        }

                        if (input && !input.dataset.gdtBound) {
                            input.dataset.gdtBound = "true";
                            input.addEventListener('input', function() {
                                updateGenericDataTables();
                            });
                        }
                    });
                }

                // 2. Process each Row
                var rowItems = rowsElem.querySelectorAll('[data-streamfield-list-container] > [data-streamfield-child]');
                rowItems.forEach(function(rowItem, rIdx) {
                    var rowNum = rIdx + 1;
                    var firstVal = '';

                    var cellsElem = rowItem.querySelector('[data-structblock-child="cell_values"], [data-contentpath="cell_values"]');
                    if (cellsElem) {
                        var cellItems = cellsElem.querySelectorAll('[data-streamfield-list-container] > [data-streamfield-child]');
                        cellItems.forEach(function(cellItem, cIdx) {
                            var colNum = cIdx + 1;
                            var colName = columnNames[cIdx];
                            var cellInput = cellItem.querySelector('input[type="text"]');
                            if (cIdx === 0 && cellInput) {
                                firstVal = (cellInput.value || '').trim();
                            }

                            if (cellInput && !cellInput.dataset.gdtBound) {
                                cellInput.dataset.gdtBound = "true";
                                cellInput.addEventListener('input', function() {
                                    if (cIdx === 0) updateGenericDataTables();
                                });
                            }

                            var badge = cellItem.querySelector('.gdt-cell-badge');
                            if (!badge) {
                                badge = document.createElement('div');
                                badge.className = 'gdt-cell-badge';
                                var target = cellItem.querySelector('.w-field, label');
                                if (target && target.parentNode) {
                                    target.parentNode.insertBefore(badge, target);
                                } else {
                                    cellItem.prepend(badge);
                                }
                            }

                            if (colName) {
                                badge.className = 'gdt-cell-badge gdt-badge--info';
                                badge.innerHTML = '🏷️ <strong>Col #' + colNum + ':</strong> ' + escapeHtml(colName);
                            } else {
                                badge.className = 'gdt-cell-badge gdt-badge--warning';
                                badge.innerHTML = '⚠️ <strong>Extra Cell #' + colNum + ':</strong> (Table only has ' + columnNames.length + ' columns defined)';
                            }

                            var cellHeading = cellItem.querySelector('[data-panel-heading-text]');
                            if (cellHeading) {
                                var cellDisp = colName ? ('Col #' + colNum + ' (' + colName + ')') : ('Col #' + colNum + ' (Extra)');
                                if (cellHeading.textContent !== cellDisp) {
                                    cellHeading.textContent = cellDisp;
                                }
                            }
                        });
                    }

                    var rowHeading = rowItem.querySelector('> .w-panel > .w-panel__header [data-panel-heading-text]');
                    if (rowHeading) {
                        var rowSummary = firstVal ? (' — ' + firstVal) : '';
                        var rowDisp = 'Row #' + rowNum + rowSummary;
                        if (rowHeading.textContent !== rowDisp) {
                            rowHeading.textContent = rowDisp;
                        }
                    }
                });
            });
        }

        function escapeHtml(str) {
            var d = document.createElement('div');
            d.textContent = str;
            return d.innerHTML;
        }

        var gdtTimeout = null;
        function scheduleGdtUpdate() {
            if (gdtTimeout) clearTimeout(gdtTimeout);
            gdtTimeout = setTimeout(updateGenericDataTables, 50);
        }

        document.addEventListener('DOMContentLoaded', scheduleGdtUpdate);
        window.addEventListener('load', scheduleGdtUpdate);

        if (window.MutationObserver) {
            var observer = new MutationObserver(function(mutations) {
                var needsUpdate = false;
                for (var i = 0; i < mutations.length; i++) {
                    if (mutations[i].addedNodes.length || mutations[i].removedNodes.length) {
                        needsUpdate = true;
                        break;
                    }
                }
                if (needsUpdate) scheduleGdtUpdate();
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }

        if (document.readyState === 'complete' || document.readyState === 'interactive') {
            scheduleGdtUpdate();
        }
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
    CustomDataRecord,
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

class CustomDataRecordViewSet(ModelViewSet):
    model = CustomDataRecord
    name = 'custom_data_records'
    icon = 'table'
    menu_label = 'Custom Data Records'
    menu_order = 70
    add_to_admin_menu = False
    list_display = ['title', 'category', 'subtitle', 'document', 'created_at']
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
        CustomDataRecordViewSet,
    )

@hooks.register('register_admin_viewset')
def register_portal_content_viewset_group():
    return PortalContentViewSetGroup()


register_snippet(QuickLinksCarouselViewSet)



