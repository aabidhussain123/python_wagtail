from django import template
from django.utils.safestring import mark_safe
from home.models import Menu

register = template.Library()

VALID_PLACEMENTS = {
    'in_stream',
    'before_heading',
    'after_heading',
    'after_main_content',
    'above_footer',
}


@register.simple_tag
def get_menu(slug):
    return Menu.objects.filter(slug=slug).first()


@register.simple_tag
def unique_id():
    import uuid
    return uuid.uuid4().hex[:8]


def _get_style_value(block):
    try:
        block_value = block.value
    except (AttributeError, ValueError):
        return None
    style = None
    try:
        style = block_value.style
    except AttributeError:
        try:
            if hasattr(block_value, 'get'):
                style = block_value.get('style')
        except (AttributeError, TypeError):
            pass
    if style is None:
        try:
            style = block_value['style']
        except (AttributeError, TypeError, KeyError):
            pass
    return style


def _get_field(value, key, default=None):
    if value is None:
        return default
    try:
        if hasattr(value, 'get'):
            found = value.get(key, default)
            if found is not None:
                return found
    except (AttributeError, TypeError):
        pass
    try:
        return value[key]
    except (AttributeError, TypeError, KeyError):
        return default


def _style_render_below(style):
    return bool(_get_field(style, 'render_below_content', False))


@register.filter
def block_placement(block):
    """
    Return where a stream block should render:
    in_stream | before_heading | after_heading | after_main_content | above_footer

    Applies to EVERY page-builder block that has Advanced Styling → Display Position.
    Only that block moves; other sections keep their own placement.
    """
    value = getattr(block, 'value', None)
    style = _get_style_value(block)

    # 1) Shared Logo Slider legacy top-level placement field
    if getattr(block, 'block_type', None) == 'shared_logo_slider':
        legacy = _get_field(value, 'placement', None)
        if legacy in VALID_PLACEMENTS and legacy != 'in_stream':
            return legacy

    # 2) Shared Display Position on Advanced Styling (all blocks)
    placement = _get_field(style, 'placement', None)
    if placement in VALID_PLACEMENTS and placement != 'in_stream':
        return placement

    # 3) Legacy checkbox → above footer
    if _style_render_below(style):
        return 'above_footer'

    return 'in_stream'


@register.filter
def placement_is(block, placement):
    return block_placement(block) == placement


@register.filter
def render_below_content(block):
    return block_placement(block) == 'above_footer'


@register.filter
def not_render_below_content(block):
    """True when the block should render in the normal page-builder stream."""
    return block_placement(block) == 'in_stream'


@register.inclusion_tag('home/partials/stream_blocks_at.html', takes_context=True)
def stream_blocks_at(context, body, placement):
    """Render only stream blocks that match the given placement slot."""
    return {
        'blocks': body or [],
        'placement': placement,
        'request': context.get('request'),
        'page': context.get('page'),
    }


@register.simple_tag
def get_in_stream_blocks(body):
    """Return list of blocks placed in_stream."""
    return [block for block in (body or []) if block_placement(block) == 'in_stream']


@register.simple_tag(takes_context=True)
def get_breadcrumbs(context, page):
    """Return list of breadcrumb dicts: [{'title': '...', 'url': '...'}]"""
    if not page or getattr(page, 'slug', '') == 'home':
        return []

    breadcrumbs = [{'title': 'Home', 'url': '/'}]

    # 1. Prioritize Navigation Menu Snippet Hierarchy
    matched_from_menu = False
    try:
        from home.models import MenuItem
        menu_item = MenuItem.objects.filter(link_page=page).order_by('-id').first()
        if menu_item and menu_item.parent:
            chain = []
            curr = menu_item.parent
            visited = set()
            while curr and curr.id not in visited:
                visited.add(curr.id)
                # Exclude duplicate 'Home' or root links if already started with Home
                if curr.link_text.strip().lower() not in ('home', 'root') and curr.link_url != '/':
                    parent_url = curr.link_page.url if curr.link_page else (curr.link_url or '')
                    chain.insert(0, {'title': curr.link_text, 'url': parent_url})
                curr = curr.parent
            if chain:
                breadcrumbs.extend(chain)
                matched_from_menu = True
    except Exception:
        pass

    # 2. Fallback to Page Tree Ancestors if not found in menu snippet
    if not matched_from_menu:
        try:
            from wagtail.models import Page
            home_page = Page.objects.filter(slug='home').first()
            home_depth = home_page.depth if home_page else 3
            tree_ancestors = [
                a for a in page.get_ancestors() 
                if a.depth > home_depth and a.slug != 'home' and (a.title or '').strip().lower() != 'home'
            ]
            for ancestor in tree_ancestors:
                try:
                    url = ancestor.url
                except Exception:
                    url = '#'
                breadcrumbs.append({'title': ancestor.title, 'url': url})
        except Exception:
            pass

    breadcrumbs.append({'title': page.title, 'url': None})
    return breadcrumbs


@register.simple_tag(takes_context=True)
def get_theme_css(context):
    from home.models import ThemeSettings, THEME_PRESETS
    request = context.get('request')
    user_theme = None
    if request:
        user_theme = request.session.get('user_theme') or request.COOKIES.get('user_theme')

    try:
        settings = ThemeSettings.load()
        if user_theme and user_theme in THEME_PRESETS:
            v = THEME_PRESETS[user_theme]
        else:
            v = settings.get_css_variables()
    except Exception:
        if user_theme and user_theme in THEME_PRESETS:
            v = THEME_PRESETS[user_theme]
        else:
            v = THEME_PRESETS['saffron_navy']

    primary = v.get('primary', '#003366')
    secondary = v.get('secondary', '#f39c12')
    navbar_bg = v.get('navbar_bg', '#003366')
    navbar_text = v.get('navbar_text', '#ffffff')
    navbar_hover_bg = v.get('navbar_hover_bg', '#f39c12')
    navbar_hover_text = v.get('navbar_hover_text', '#000000')
    card_header_bg = v.get('card_header_bg', '#f39c12')
    card_header_text = v.get('card_header_text', '#000000')
    table_header_bg = v.get('table_header_bg', '#f39c12')
    table_header_text = v.get('table_header_text', '#000000')
    btn_bg = v.get('btn_bg', '#f39c12')
    btn_text = v.get('btn_text', '#000000')
    btn_border = v.get('btn_border', '#d38307')
    footer_bg = v.get('footer_bg', '#111827')

    css = f"""
    <style id="portal-dynamic-theme">
        :root {{
            --theme-primary: {primary};
            --theme-secondary: {secondary};
            --theme-navbar-bg: {navbar_bg};
            --theme-navbar-text: {navbar_text};
            --theme-navbar-hover-bg: {navbar_hover_bg};
            --theme-navbar-hover-text: {navbar_hover_text};
            --theme-card-header-bg: {card_header_bg};
            --theme-card-header-text: {card_header_text};
            --theme-table-header-bg: {table_header_bg};
            --theme-table-header-text: {table_header_text};
            --theme-btn-bg: {btn_bg};
            --theme-btn-text: {btn_text};
            --theme-btn-border: {btn_border};
            --theme-footer-bg: {footer_bg};
        }}
        /* Dynamic Theme Navigation Bar */
        .gov-custom-navbar,
        nav.gov-custom-navbar,
        nav.navbar.gov-custom-navbar,
        nav.navbar,
        nav.navbar-dark,
        nav.bg-dark,
        .navbar-expand-md.gov-custom-navbar {{
            background-color: var(--theme-navbar-bg) !important;
            border-top: 1px solid var(--theme-secondary) !important;
            border-bottom: 3px solid var(--theme-secondary) !important;
        }}
        .gov-custom-navbar .container,
        .gov-custom-navbar .container-fluid,
        .gov-custom-navbar .navbar-collapse {{
            background-color: transparent !important;
        }}
        .gov-custom-navbar .navbar-nav .nav-link,
        nav.navbar .navbar-nav .nav-link,
        nav.gov-custom-navbar a.nav-link,
        .navbar-dark .navbar-nav .nav-link {{
            color: var(--theme-navbar-text) !important;
            font-weight: 600 !important;
        }}
        .gov-custom-navbar .navbar-nav .nav-item:hover > .nav-link,
        .gov-custom-navbar .navbar-nav .nav-item.active > .nav-link,
        .gov-custom-navbar .navbar-nav .nav-item.show > .nav-link,
        .gov-custom-navbar .navbar-nav .nav-link:hover,
        .gov-custom-navbar .navbar-nav .nav-link.active,
        nav.navbar .navbar-nav .nav-item:hover > .nav-link,
        nav.navbar .navbar-nav .nav-item.active > .nav-link,
        nav.gov-custom-navbar a.nav-link:hover,
        .navbar-dark .navbar-nav .nav-link:hover, 
        .navbar-dark .navbar-nav .nav-link.active {{
            background-color: var(--theme-navbar-hover-bg) !important;
            color: var(--theme-navbar-hover-text) !important;
            font-weight: 700 !important;
        }}
        .gov-custom-navbar .dropdown-menu {{
            background-color: var(--theme-card-header-bg) !important;
            border-top: 3px solid var(--theme-secondary) !important;
            border-bottom: 2px solid var(--theme-btn-border) !important;
        }}
        .gov-custom-navbar .dropdown-item {{
            color: var(--theme-card-header-text) !important;
        }}
        .gov-custom-navbar .dropdown-item:hover,
        .gov-custom-navbar .dropdown-item:focus,
        .gov-custom-navbar .dropdown-item.active,
        .gov-custom-navbar .dropdown-submenu:hover > .dropdown-item {{
            background-color: var(--theme-primary) !important;
            color: #ffffff !important;
            font-weight: 700 !important;
        }}

        /* Card Headers & Banner Highlights */
        .bg-gov-saffron,
        .card-header.bg-gov-saffron,
        .card-header.bg-warning,
        .card-header[style*="#f39c12"] {{
            background-color: var(--theme-card-header-bg) !important;
            color: var(--theme-card-header-text) !important;
        }}
        .bg-gov-saffron *,
        .card-header.bg-gov-saffron *,
        .card-header[style*="#f39c12"] * {{
            color: var(--theme-card-header-text) !important;
        }}

        /* Global Table Headings */
        table thead,
        table thead tr,
        table thead th,
        .table-dark,
        .table-dark th,
        .table-primary,
        .table-primary th,
        .table-gov-header tr,
        thead tr[style*="#f39c12"],
        th[style*="#f39c12"] {{
            background-color: var(--theme-table-header-bg) !important;
            color: var(--theme-table-header-text) !important;
            border-bottom: 2px solid var(--theme-btn-border) !important;
        }}
        table thead th *,
        .table-gov-header th * {{
            color: var(--theme-table-header-text) !important;
        }}

        /* Global Buttons */
        .btn-primary,
        .btn-warning,
        .btn-gov,
        .quick-button-link,
        .table .btn,
        .table a.btn,
        button.btn-warning {{
            background-color: var(--theme-btn-bg) !important;
            border-color: var(--theme-btn-border) !important;
            color: var(--theme-btn-text) !important;
        }}

        /* Buttons Hover */
        .btn-primary:hover,
        .btn-warning:hover,
        .btn-gov:hover,
        .quick-button-link:hover,
        .table .btn:hover,
        .table a.btn:hover,
        button.btn-warning:hover {{
            background-color: var(--theme-primary) !important;
            border-color: var(--theme-primary) !important;
            color: #ffffff !important;
        }}

        /* Footer */
        .gov-footer {{
            background-color: var(--theme-footer-bg) !important;
            border-top: 4px solid var(--theme-secondary) !important;
        }}

        /* Badges & Accents */
        .badge-gov,
        .badge.bg-warning {{
            background-color: var(--theme-secondary) !important;
            color: var(--theme-btn-text) !important;
        }}
        .text-warning {{
            color: var(--theme-secondary) !important;
        }}
    </style>
    """
    return mark_safe(css)


@register.simple_tag(takes_context=True)
def get_current_theme_key(context):
    from home.models import ThemeSettings, THEME_PRESETS
    request = context.get('request')
    if request:
        user_theme = request.session.get('user_theme') or request.COOKIES.get('user_theme')
        if user_theme and user_theme in THEME_PRESETS:
            return user_theme
    try:
        settings = ThemeSettings.load()
        return settings.active_theme or 'saffron_navy'
    except Exception:
        return 'saffron_navy'


@register.simple_tag
def get_available_theme_presets():
    from home.models import THEME_PRESETS
    return THEME_PRESETS
