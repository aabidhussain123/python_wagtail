from django import template
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
