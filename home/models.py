from django.db import models            #database layer
from django.utils.safestring import mark_safe       #for render HTML string and for XSS protection
from wagtail.models import Page, Orderable          #orderable-->for Sorting items
from wagtail.fields import RichTextField, StreamField   #StreamField-->for page builder(+add block)
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, Panel
from wagtail.search import index
from wagtail import blocks          #collection of StreamFields
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting    #for site-wide settings and for register settings to wagtail admin
from wagtail.snippets.models import register_snippet        #for reusable content(decorator)
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey
from wagtail.snippets.blocks import SnippetChooserBlock

from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField, FORM_FIELD_CHOICES
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.panels import FormSubmissionsPanel
from django import forms                #for form fields


# --- PAGE BUILDER WIDGET BLOCKS ---


#For Display Position and Styling
class BlockStyleStructBlock(blocks.StructBlock):        
    placement = blocks.ChoiceBlock(             #position of block on the page (top, bottom, after heading, etc.)
        choices=[
            ('in stream', 'In page builder order (default)'),
            ('before heading', 'Top of page (before page title)'),
            ('after heading', 'After page heading (before dynamic content)'),
            ('after main_content', 'After main / dynamic content'),
            ('above footer', 'Above footer'),
        ],
        default='in_stream',
        required=False,
        label='Display Position',           #title
        help_text=(
            'Where to show THIS section only. Other sections keep their own positions. '
            'On listing pages (Govt Orders, News, Notices, RTI, ROP): '
            '"After page heading" puts it above the dynamic list; '
            '"In page builder order" keeps it below the list with other builder blocks.'
        ),
    )
    margin_top = blocks.ChoiceBlock(choices=[
        ('mt-0', 'None'),
        ('mt-2', 'Small(.5rem)'),
        ('mt-4', 'Medium(1.5rem)'),
        ('mt-5', 'Large(3rem)'),
    ], default='mt-4', label="Margin Top")
    
    margin_bottom = blocks.ChoiceBlock(choices=[
        ('mb-0', 'None'),
        ('mb-2', 'Small(.5rem)'),
        ('mb-4', 'Medium(1.5rem)'),
        ('mb-5', 'Large(3rem)'),
    ], default='mb-4', label="Margin Bottom")
    
    padding_top = blocks.ChoiceBlock(choices=[
        ('pt-0', 'None'),
        ('pt-2', 'Small(.5rem)'),
        ('pt-4', 'Medium(1.5rem)'),
        ('pt-5', 'Large(3rem)'),
    ], default='pt-0', label="Padding Top")
    
    padding_bottom = blocks.ChoiceBlock(choices=[
        ('pb-0', 'None'),
        ('pb-2', 'Small(.5rem)'),
        ('pb-4', 'Medium(1.5rem)'),
        ('pb-5', 'Large(3rem)'),
    ], default='pb-0', label="Padding Bottom")
    
    custom_class = blocks.CharBlock(required=False, label="Custom CSS Class Name", help_text="Add custom CSS class name for styling")
    custom_css = blocks.TextBlock(required=False, label="Custom CSS Styles", help_text="Write custom CSS properties here")
    
    render_below_content = blocks.BooleanBlock(
        required=False,
        default=False,
        label="(Legacy) Render Below Page Content",
        help_text="Deprecated — use Display Position → Above footer instead.",
    )

#For Image Carousel Slider
class SlideBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    title = blocks.CharBlock(required=False, help_text="Title overlay on the slide")
    subtitle = blocks.CharBlock(required=False, help_text="Subtitle overlay on the slide")
    link = blocks.PageChooserBlock(required=False, help_text="Optional page link when slide is clicked")

#For Image Carousel Slider
class SliderBlock(blocks.StructBlock):
    slides = blocks.ListBlock(SlideBlock(), label="Slides Carousel")
    container_width = blocks.ChoiceBlock(choices=[
        ('container', 'Boxed Width (container)'),
        ('container-fluid', 'Full Width (container-fluid)'),
    ], default='container-fluid', label="Container Width", help_text="Choose whether the slider should be full width or boxed width.")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/slider_block.html'
        icon = 'image'
        label = 'Image Carousel Slider'


class HeroBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    subtitle = blocks.TextBlock(required=False)
    background_image = ImageChooserBlock(required=False)
    cta_text = blocks.CharBlock(required=False, label="CTA Button Text")
    cta_link = blocks.PageChooserBlock(required=False, label="CTA Link Page")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/hero_block.html'
        icon = 'home'
        label = 'Hero Banner'


class FeaturedPageCardBlock(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=True)
    custom_title = blocks.CharBlock(required=False, help_text="Optional: Overrides page title in card")
    custom_description = blocks.TextBlock(required=False, help_text="Optional: Overrides page summary in card")
    custom_image = ImageChooserBlock(required=False, help_text="Optional: Overrides page image in card")


class FeaturedPagesBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="Header for this sections grid")
    cards = blocks.ListBlock(FeaturedPageCardBlock(), label="Pages Grid Cards")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/featured_pages_block.html'
        icon = 'folder-open'
        label = 'Featured Page Grid'


class FeaturedCardBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False, help_text="Card image")
    heading = blocks.CharBlock(required=True, help_text="Card heading/title")
    subheading = blocks.TextBlock(required=False, help_text="Card description/subheading")
    link_page = blocks.PageChooserBlock(required=False, help_text="Link to an internal page")
    link_url = blocks.URLBlock(required=False, help_text="Or enter an external URL")

    class Meta:
        icon = 'doc-full'
        label = 'Featured Card'


class FeaturedCardsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, help_text="Optional section header/title")
    cards = blocks.ListBlock(FeaturedCardBlock(), label="Featured Cards Grid")
    cards_in_row = blocks.ChoiceBlock(choices=[
        ('3', '3 Cards'),
        ('4', '4 Cards'),
        ('5', '5 Cards'),
        ('6', '6 Cards'),
    ], default='4', label="Cards in a Row", help_text="Select number of cards to display in a row on large screens")
    custom_css = blocks.TextBlock(required=False, label="Custom CSS for Section", help_text="Write custom CSS rules specifically for this section.")
    custom_js = blocks.TextBlock(required=False, label="Custom JS for Section", help_text="Write custom JavaScript behaviors for this section.")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/featured_cards_block.html'
        icon = 'grid'
        label = 'Featured Cards Grid'


class ContentSectionBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    body = blocks.RichTextBlock(required=True)
    image = ImageChooserBlock(required=False)
    image_alignment = blocks.ChoiceBlock(choices=[
        ('left', 'Image on Left'),
        ('right', 'Image on Right')
    ], default='left')
    bg_color = blocks.ChoiceBlock(choices=[
        ('white', 'White Background'),
        ('light', 'Light Gray Background'),
        ('primary-light', 'Light Blue Background')
    ], default='white')
    custom_css = blocks.TextBlock(required=False, label="Custom CSS for Section", help_text="Write custom CSS rules specifically for this section.")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/content_section_block.html'
        icon = 'doc-full'
        label = 'Content Section Columns'


class NewsNoticeLatestBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, default="News & Notices", help_text="Header for this section")
    news_count = blocks.IntegerBlock(default=3, min_value=1, max_value=10, label="Number of News Items")
    notice_count = blocks.IntegerBlock(default=5, min_value=1, max_value=10, label="Number of Notices")
    govt_order_count = blocks.IntegerBlock(default=5, min_value=1, max_value=10, label="Number of Government Orders")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from home.models import NewsPage, NoticePage, GovtOrderPage, NewsIndexPage, NoticeIndexPage, GovtOrderIndexPage
        context['news_pages'] = NewsPage.objects.live().public().order_by('-date')[:value.get('news_count', 3)]
        context['notice_pages'] = NoticePage.objects.live().public().order_by('-date')[:value.get('notice_count', 5)]
        context['govt_orders'] = GovtOrderPage.objects.live().public().order_by('-order_date')[:value.get('govt_order_count', 5)]
        context['news_index'] = NewsIndexPage.objects.live().public().first()
        context['notice_index'] = NoticeIndexPage.objects.live().public().first()
        context['govt_order_index'] = GovtOrderIndexPage.objects.live().public().first()
        return context

    class Meta:
        template = 'home/blocks/news_notice_latest_block.html'
        icon = 'list-ul'
        label = 'Dynamic News & Notices Section'


class QuickLinkItemBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, help_text="Upload/Select the icon for the quick link")
    title = blocks.CharBlock(required=True, max_length=100, help_text="Text displayed below the icon")
    link_page = blocks.PageChooserBlock(required=False, help_text="Optional internal page link")
    link_url = blocks.URLBlock(required=False, help_text="Optional external URL link")
    border_color = blocks.ChoiceBlock(choices=[
        ('blue', 'Theme Blue'),
        ('orange', 'Theme Orange'),
        ('green', 'Theme Green'),
        ('red', 'Theme Red'),
    ], default='orange', label="Circle Border Color")


class QuickLinksCarouselBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label="Section Title", help_text="Optional title for this section")
    links = blocks.ListBlock(QuickLinkItemBlock(), label="Quick Links List")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/quick_links_carousel_block.html'
        icon = 'link'
        label = 'Quick Links Carousel (Circular)'


class QuickButtonItemBlock(blocks.StructBlock):
    text = blocks.CharBlock(required=True, max_length=100, label="Button Text", help_text="Text displayed on the button")
    link_page = blocks.PageChooserBlock(required=False, label="Link to Page", help_text="Select a page to link to")
    link_url = blocks.URLBlock(required=False, label="Link to URL", help_text="Or paste an external website URL")


class QuickButtonsBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label="Section Title", help_text="Optional title for this section")
    buttons = blocks.ListBlock(QuickButtonItemBlock(), label="Buttons List")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/quick_buttons_block.html'
        icon = 'link'
        label = 'Quick Buttons Row'


class PdfBannerItemBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label="Banner Image", help_text="Upload/Select the banner image")
    document = DocumentChooserBlock(required=True, label="PDF Document", help_text="Upload/Select the PDF document to open when clicked")
    caption = blocks.CharBlock(required=False, label="Caption/Title", help_text="Optional text title/caption for screen readers or hover display")


class PdfBannersBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label="Section Title", help_text="Optional section header title")
    banners = blocks.ListBlock(PdfBannerItemBlock(), label="PDF Banners")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/pdf_banners_block.html'
        icon = 'doc-full'
        label = 'PDF Banners Grid'


class LogoItemBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True, label="Logo Image", help_text="Upload/Select the logo image")
    link_url = blocks.URLBlock(required=False, label="External URL Link", help_text="Optional external link URL")
    link_page = blocks.PageChooserBlock(required=False, label="Internal Page Link", help_text="Or select an internal page to link to")
    title = blocks.CharBlock(required=False, label="Logo Title", help_text="Title / alt text for the logo")


class LogoCarouselBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label="Section Title", help_text="Optional title for this section")
    logos = blocks.ListBlock(LogoItemBlock(), label="Logos List")
    custom_css = blocks.TextBlock(required=False, label="Custom CSS for Section", help_text="Write custom CSS rules specifically for this section.")
    custom_js = blocks.TextBlock(required=False, label="Custom JS for Section", help_text="Write custom JavaScript behaviors for this section.")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/logo_carousel_block.html'
        icon = 'image'
        label = 'Logo Carousel Slider'


class SharedLogoSliderBlock(blocks.StructBlock):
    logo_slider = SnippetChooserBlock('home.LogoSlider', label="Select Logo Slider")
    # Legacy top-level placement (kept for existing pages). Prefer style.placement.
    placement = blocks.ChoiceBlock(
        choices=[
            ('in_stream', 'In page builder order (default)'),
            ('before_heading', 'Top of page (before page title)'),
            ('after_heading', 'After page heading (before dynamic content)'),
            ('after_main_content', 'After main / dynamic content'),
            ('above_footer', 'Above footer'),
        ],
        default='in_stream',
        required=False,
        label='Display Position (legacy)',
        help_text='Prefer Display Position under Advanced Styling Settings. Kept for older pages.',
    )
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/shared_logo_slider_block.html'
        icon = 'image'
        label = 'Shared Logo Slider'


class SharedQuickLinksCarouselBlock(blocks.StructBlock):
    quick_links = SnippetChooserBlock(
        'home.QuickLinksCarousel',
        required=True,
        label="Select Quick Links Carousel",
        help_text=(
            "Choose a Quick Links Carousel from the admin sidebar "
            "(Quick Links Carousel). Create/edit the circle links there once, "
            "then reuse this block on any page."
        ),
    )
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/shared_quick_links_carousel_block.html'
        icon = 'link'
        label = 'Shared Quick Links Carousel'



class NewsListingBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, default="Latest News", help_text="Section Title")
    news_count = blocks.IntegerBlock(default=6, min_value=1, max_value=24, label="Number of News Items")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from home.models import NewsPage, NewsIndexPage
        context['news_pages'] = NewsPage.objects.live().public().order_by('-date')[:value.get('news_count', 6)]
        context['news_index'] = NewsIndexPage.objects.live().public().first()
        return context

    class Meta:
        template = 'home/blocks/news_listing_block.html'
        icon = 'list-ul'
        label = 'News Listing Section'


class NoticeListingBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, default="Official Notices", help_text="Section Title")
    notice_count = blocks.IntegerBlock(default=5, min_value=1, max_value=25, label="Number of Notices")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from home.models import NoticePage, NoticeIndexPage
        context['notice_pages'] = NoticePage.objects.live().public().order_by('-date')[:value.get('notice_count', 5)]
        context['notice_index'] = NoticeIndexPage.objects.live().public().first()
        return context

    class Meta:
        template = 'home/blocks/notice_listing_block.html'
        icon = 'list-ul'
        label = 'Notice Listing Section'


class GovtOrderListingBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, default="Government Orders", help_text="Section Title")
    order_count = blocks.IntegerBlock(default=10, min_value=1, max_value=50, label="Number of Orders")
    show_filters = blocks.BooleanBlock(default=True, required=False, label="Show Search and Department Filters")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from home.models import GovtOrderPage, GovtOrderIndexPage
        orders = GovtOrderPage.objects.live().public().order_by('-order_date')

        request = parent_context.get('request') if parent_context else None
        dept = ""
        q = ""
        if request:
            dept = request.GET.get('department', '')
            if dept:
                orders = orders.filter(department=dept)

            q = request.GET.get('q', '')
            if q:
                orders = orders.filter(
                    models.Q(title__icontains=q) |
                    models.Q(order_number__icontains=q) |
                    models.Q(subject__icontains=q)
                )

        context['orders'] = orders[:value.get('order_count', 10)]
        context['departments'] = GovtOrderPage.DEPARTMENT_CHOICES
        context['selected_dept'] = dept
        context['q'] = q
        context['govt_order_index'] = GovtOrderIndexPage.objects.live().public().first()
        return context

    class Meta:
        template = 'home/blocks/govt_order_listing_block.html'
        icon = 'list-ul'
        label = 'Government Orders Listing Section'


class HomePdfBannersBlock(blocks.StructBlock):
    style = BlockStyleStructBlock(required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        homepage = HomePage.objects.live().public().first()
        if homepage:
            for block in homepage.body:
                if block.block_type == 'pdf_banners':
                    context['shared_value'] = block.value
                    break
        return context

    class Meta:
        template = 'home/blocks/home_pdf_banners_block.html'
        icon = 'image'
        label = 'Shared Homepage PDF Banners Grid'


class HomeLogoCarouselBlock(blocks.StructBlock):
    style = BlockStyleStructBlock(required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        homepage = HomePage.objects.live().public().first()
        if homepage:
            for block in homepage.body:
                if block.block_type == 'logo_carousel':
                    context['shared_value'] = block.value
                    break
        return context

    class Meta:
        template = 'home/blocks/home_logo_carousel_block.html'
        icon = 'image'
        label = 'Shared Homepage Logo Carousel'


class HomeQuickLinksCarouselBlock(blocks.StructBlock):
    style = BlockStyleStructBlock(required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        homepage = HomePage.objects.live().public().first()
        if homepage:
            for block in homepage.body:
                if block.block_type == 'quick_links_carousel':
                    context['shared_value'] = block.value
                    break
        return context

    class Meta:
        template = 'home/blocks/home_quick_links_carousel_block.html'
        icon = 'link'
        label = 'Shared Homepage Quick Links Carousel'


class GenericDataRowStructBlock(blocks.StructBlock):
    cell_values = blocks.ListBlock(
        blocks.CharBlock(label="Cell Value"), 
        label="Row Cells (matching Column headers in order: Col 1, Col 2, ...)"
    )
    badge_text = blocks.CharBlock(required=False, label="Status Badge Text (e.g. Active, NEW, Closed)")
    badge_color = blocks.ChoiceBlock(
        choices=[
            ('danger', 'Red Badge'),
            ('warning', 'Saffron Badge'),
            ('success', 'Green Badge'),
            ('secondary', 'Grey Badge'),
        ],
        default='danger',
        required=False,
        label="Badge Color"
    )
    attachment = DocumentChooserBlock(required=False, label="PDF / File Attachment")

    class Meta:
        label = "Table Row"
        icon = "list-ul"


class GenericDataTableBlock(BlockStyleStructBlock):
    table_title = blocks.CharBlock(required=False, default="", label="Table Section Title (Optional, leave blank to hide top card header)")
    table_subtitle = blocks.CharBlock(required=False, label="Table Subtitle / Note (Optional)")
    show_serial_no = blocks.BooleanBlock(required=False, default=True, label="Show Serial Number (#) Column Automatically")
    show_row_totals = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Calculate Row Totals (Horizontal Sum Column)",
        help_text="Adds a 'Total' column at the end calculating the horizontal sum of numerical cells for each row."
    )
    show_column_totals = blocks.BooleanBlock(
        required=False,
        default=False,
        label="Calculate Column Totals (Vertical Sum Bottom Row)",
        help_text="Adds a 'Total' summary row at the bottom of the table calculating vertical column sums."
    )
    row_total_label = blocks.CharBlock(required=False, default="Total", label="Row Total Column Header Label")
    column_total_label = blocks.CharBlock(required=False, default="Total", label="Bottom Total Row Label")
    columns = blocks.ListBlock(
        blocks.CharBlock(label="Column Title"),
        required=False,
        default=[],
        label="Table Column Headers (Col 1, Col 2, Col 3, ...)"
    )
    rows = blocks.ListBlock(
        GenericDataRowStructBlock(),
        label="Table Rows Data"
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        raw_rows = value.get('rows', [])
        columns = list(value.get('columns', []))

        def parse_number(val):
            if val is None:
                return None
            s = str(val).strip().replace(',', '').replace(' ', '').replace('₹', '').replace('$', '')
            if not s:
                return None
            try:
                return float(s) if '.' in s else int(s)
            except ValueError:
                return None

        def format_num(n):
            if n is None:
                return ""
            if isinstance(n, float):
                return f"{n:,.2f}".rstrip('0').rstrip('.')
            return f"{n:,}"

        num_cols = len(columns)
        col_sums = [0 for _ in range(num_cols)]
        col_has_number = [False] * num_cols
        grand_total = 0
        has_any_num = False

        processed_rows = []
        for row in raw_rows:
            cells = list(row.get('cell_values', []))
            row_sum = 0
            row_has_num = False

            for col_idx, cell in enumerate(cells):
                num = parse_number(cell)
                if num is not None:
                    row_sum += num
                    row_has_num = True
                    has_any_num = True
                    if col_idx < num_cols:
                        col_sums[col_idx] += num
                        col_has_number[col_idx] = True

            row_dict = {
                'cell_values': cells,
                'badge_text': row.get('badge_text'),
                'badge_color': row.get('badge_color', 'danger'),
                'attachment': row.get('attachment'),
                'row_total': format_num(row_sum) if row_has_num else "—"
            }
            if row_has_num:
                grand_total += row_sum
            processed_rows.append(row_dict)

        column_totals = []
        for idx in range(num_cols):
            if col_has_number[idx]:
                column_totals.append(format_num(col_sums[idx]))
            else:
                column_totals.append("")

        context['processed_rows'] = processed_rows
        context['column_totals'] = column_totals
        context['grand_total'] = format_num(grand_total) if has_any_num else "0"
        context['has_attachments'] = any(bool(row.get('attachment')) for row in raw_rows)
        return context

    class Meta:
        template = 'home/blocks/generic_data_table_block.html'
        icon = 'table'
        label = 'Generic Dynamic Data Table (Pattern 2)'


def get_custom_data_record_categories():
    try:
        from home.models import CustomDataRecord
        cats = CustomDataRecord.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()
        unique_cats = sorted(set(c.strip() for c in cats if c and c.strip()))
        choices = [('', '— All Categories / Auto Match Page Title —')]
        for c in unique_cats:
            choices.append((c, c))
        return choices
    except Exception:
        return [('', '— All Categories / Auto Match Page Title —')]


class CustomDataRecordsBlock(BlockStyleStructBlock):
    category_select = blocks.ChoiceBlock(
        choices=get_custom_data_record_categories,
        required=False,
        default="",
        label="Select Category from Existing Records",
        help_text="Select a category from the dropdown (automatically populated from your Custom Data Records snippets)."
    )
    category_filter = blocks.CharBlock(
        required=False,
        default="",
        label="Or Type Custom Category Filter",
        help_text="Optional: Type category name manually if not in dropdown or to filter by custom keyword."
    )
    section_title = blocks.CharBlock(
        required=False,
        default="",
        label="Section Title / Heading (Optional)",
        help_text="Custom heading to display above the table. If left blank, category name is used."
    )
    section_subtitle = blocks.CharBlock(required=False, label="Section Subtitle")

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from home.models import CustomDataRecord

        cat_filter = (value.get('category_select') or value.get('category_filter') or '').strip()
        all_records = list(CustomDataRecord.objects.all().order_by('-created_at'))

        matched = []
        active_cat = ""

        if not cat_filter or cat_filter.lower() == 'all':
            # Check if any match page title or slug exactly (case-insensitive)
            if parent_context and 'page' in parent_context:
                page = parent_context['page']
                page_title = (page.title or '').strip().lower()
                page_slug = (page.slug or '').strip().lower().replace('-', ' ')
                matched_page = [
                    r for r in all_records
                    if r.category and (r.category.strip().lower() == page_title or r.category.strip().lower() == page_slug)
                ]
                if matched_page:
                    matched = matched_page
                    active_cat = matched_page[0].category if matched_page else ""
                else:
                    matched = all_records
            else:
                matched = all_records
        else:
            # STRICT MATCHING: Exact case-insensitive match only
            target_cat = cat_filter.strip().lower()
            matched = [
                r for r in all_records
                if r.category and r.category.strip().lower() == target_cat
            ]
            active_cat = cat_filter

        # Collect distinct dynamic column headers in the order they appear
        columns = []
        for r in matched:
            if r.extra_fields:
                for block in r.extra_fields:
                    val = block.value
                    fn = (val.get('field_name') or '').strip()
                    if fn and fn not in columns:
                        columns.append(fn)

        # For each record, create dynamic_cells aligned with columns
        for r in matched:
            attr_map = {}
            if r.extra_fields:
                for block in r.extra_fields:
                    val = block.value
                    fn = (val.get('field_name') or '').strip()
                    ft = val.get('field_type') or 'text'
                    fv = val.get('field_value') or ''
                    if fn:
                        attr_map[fn] = {'type': ft, 'value': fv}
            r.dynamic_cells = [attr_map.get(col, {'type': 'text', 'value': '—'}) for col in columns]

        context['columns'] = columns
        context['records'] = matched
        context['active_category'] = active_cat
        context['has_extra_fields'] = bool(len(columns) > 0)
        return context

    class Meta:
        template = 'home/blocks/custom_data_records_block.html'
        icon = 'folder-open-inverse'
        label = 'Admin Custom Data Records Block'


class FourContainerBoxItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, label="Title", help_text="Title displayed inside the box")
    link_page = blocks.PageChooserBlock(required=False, label="Add Page to Redirect", help_text="Select the page to redirect to when this box is clicked")
    link_url = blocks.URLBlock(required=False, label="Or External URL", help_text="Optional external URL if redirecting outside the site")
    open_in_new_tab = blocks.BooleanBlock(required=False, default=False, label="Open in New Tab")

    class Meta:
        icon = 'doc-full'
        label = 'Container Box'


class FourContainersBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, label="Section Title", help_text="Optional heading displayed above the 4 containers")
    boxes = blocks.ListBlock(FourContainerBoxItemBlock(), label="Boxes / Containers")
    custom_css = blocks.TextBlock(required=False, label="Custom CSS for Section", help_text="Write custom CSS rules specifically for this section.")
    custom_js = blocks.TextBlock(required=False, label="Custom JS for Section", help_text="Write custom JavaScript behaviors for this section.")
    style = BlockStyleStructBlock(label="Display Position & Styling", required=False)

    class Meta:
        template = 'home/blocks/four_containers_block.html'
        icon = 'grid'
        label = '4 Containers Box Grid'


PAGE_BUILDER_BLOCKS = [
    ('hero', HeroBlock()),
    ('slider', SliderBlock()),
    ('featured_pages', FeaturedPagesBlock()),
    ('featured_cards', FeaturedCardsBlock()),
    ('four_containers', FourContainersBlock()),
    ('content_section', ContentSectionBlock()),
    ('news_notice_latest', NewsNoticeLatestBlock()),
    ('news_listing', NewsListingBlock()),
    ('notice_listing', NoticeListingBlock()),
    ('govt_order_listing', GovtOrderListingBlock()),
    ('quick_links_carousel', QuickLinksCarouselBlock()),
    ('quick_buttons', QuickButtonsBlock()),
    ('pdf_banners', PdfBannersBlock()),
    ('logo_carousel', LogoCarouselBlock()),
    ('generic_data_table', GenericDataTableBlock()),
    ('custom_data_records_block', CustomDataRecordsBlock()),
    ('rich_text', blocks.RichTextBlock()),
    ('raw_html', blocks.RawHTMLBlock(label="Raw HTML")),
    ('home_pdf_banners', HomePdfBannersBlock()),
    ('home_logo_carousel', HomeLogoCarouselBlock()),
    ('home_quick_links', HomeQuickLinksCarouselBlock()),
    ('shared_logo_slider', SharedLogoSliderBlock()),
    ('shared_quick_links', SharedQuickLinksCarouselBlock()),
]



# --- SITE SETTINGS ---

@register_setting
class HeaderFooterSettings(BaseGenericSetting):
    # Top Bar Fields
    topbar_show_portal_badge = models.BooleanField(default=True, verbose_name="Show 'Official Portal' Badge")
    topbar_home_text = models.CharField(max_length=100, default="Home", blank=True, verbose_name="Home Link Text")
    topbar_home_url = models.CharField(max_length=255, default="/", blank=True, verbose_name="Home Link URL")
    topbar_sitemap_text = models.CharField(max_length=100, default="Sitemap", blank=True, verbose_name="Sitemap Link Text")
    topbar_sitemap_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Sitemap Link URL (Optional)")
    topbar_feedmap_text = models.CharField(max_length=100, default="Feedmap", blank=True, verbose_name="Feedmap Link Text")
    topbar_feedmap_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Feedmap Link URL (Optional)")
    topbar_feedback_text = models.CharField(max_length=100, default="Feedback", blank=True, verbose_name="Feedback Link Text")
    topbar_feedback_url = models.CharField(max_length=255, default="", blank=True, verbose_name="Feedback Link URL (Optional)")
    topbar_tollfree = models.CharField(
        max_length=255,
        default="",
        blank=True,
        verbose_name="Toll Free / Helpline (Center, Optional)",
        help_text="Optional helpline banner shown in center of top bar (e.g. 'Toll Free: 104 / 1800-180-1104')."
    )

    # Social Media Channels (Optional, shown in Header & Footer if configured)
    facebook_url = models.URLField(blank=True, default="", verbose_name="Facebook Page URL", help_text="e.g. https://facebook.com/nhm")
    twitter_url = models.URLField(blank=True, default="", verbose_name="Twitter / X URL", help_text="e.g. https://twitter.com/nhm")
    youtube_url = models.URLField(blank=True, default="", verbose_name="YouTube Channel URL", help_text="e.g. https://youtube.com/@nhm")
    instagram_url = models.URLField(blank=True, default="", verbose_name="Instagram URL", help_text="e.g. https://instagram.com/nhm")
    linkedin_url = models.URLField(blank=True, default="", verbose_name="LinkedIn URL", help_text="e.g. https://linkedin.com/company/nhm")

    # Header Fields
    site_title = models.CharField(max_length=255, default="DEPARTMENT OF PUBLIC ADMINISTRATION", verbose_name="Site Title (Fallback)")
    site_subtitle = models.CharField(max_length=255, default="Government Content Management System Portal", verbose_name="Site Subtitle (Fallback)")
    site_title_line_1 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 1 (e.g. Hindi: राष्ट्रीय स्वास्थ्य मिशन)")
    site_title_line_2 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 2 (e.g. English Main: National Health Mission)")
    site_title_line_3 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 3 (e.g. Urdu: قومی صحت مشن)")
    site_title_line_4 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 4 (e.g. State Health Society, Health & Family Welfare)")
    site_title_line_5 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 5 (e.g. Department Government of J&K)")
    site_title_line_6 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 6 (Optional Additional Line)")
    
    logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Left Site Logo",
        help_text="Upload/Select your main left logo image"
    )
    right_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Right Site Logo (Emblem)",
        help_text="Upload/Select an emblem or right-side logo (displayed on the far right after search)"
    )

    # Search Bar Settings
    enable_header_search = models.BooleanField(default=True, verbose_name="Enable Header Search Bar")
    header_search_placeholder = models.CharField(max_length=100, default="Search Portal...", verbose_name="Search Placeholder Text")

    header_css = models.TextField(
        blank=True,
        verbose_name="Header CSS Customization",
        help_text="Write custom CSS rules specifically for the header section."
    )
    header_js = models.TextField(
        blank=True,
        verbose_name="Header JS Customization",
        help_text="Write custom JavaScript behaviors for the header section."
    )

    # Footer Fields
    footer_about_title = models.CharField(max_length=255, default="GovCMS Portal", verbose_name="Footer Section Title")
    footer_about_text = models.TextField(
        blank=True,
        default="This is the official content management portal for disseminating public orders, notices, news, and official announcements. Designed to ensure transparency.",
        verbose_name="Footer About Text"
    )
    footer_address = models.CharField(max_length=255, default="Secretariat Complex, Block A", verbose_name="Office Address")
    footer_email = models.EmailField(default="support-govsite@example.com", verbose_name="Support Email")
    footer_phone = models.CharField(max_length=50, default="+11-2345-6789", verbose_name="Support Phone")
    copyright_text = models.CharField(max_length=255, default="Department of Public Administration. All rights reserved.", verbose_name="Copyright Text")

    # Advanced HTML Overrides
    custom_header_html = models.TextField(
        blank=True,
        verbose_name="Custom Header HTML",
        help_text="Raw HTML injected in the header (overrides standard header if supplied)."
    )
    custom_footer_html = models.TextField(
        blank=True,
        verbose_name="Custom Footer HTML",
        help_text="Raw HTML injected in the footer (overrides standard footer if supplied)."
    )
    additional_css = models.TextField(
        blank=True,
        verbose_name="Additional CSS",
        help_text="Global custom CSS styles (loaded inside a stylesheet block in the page head)."
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('topbar_show_portal_badge'),
            FieldPanel('topbar_home_text'),
            FieldPanel('topbar_home_url'),
            FieldPanel('topbar_sitemap_text'),
            FieldPanel('topbar_sitemap_url'),
            FieldPanel('topbar_feedmap_text'),
            FieldPanel('topbar_feedmap_url'),
            FieldPanel('topbar_feedback_text'),
            FieldPanel('topbar_feedback_url'),
            FieldPanel('topbar_tollfree'),
        ], heading="Top Bar Navigation & Helpline Settings"),

        MultiFieldPanel([
            FieldPanel('facebook_url'),
            FieldPanel('twitter_url'),
            FieldPanel('youtube_url'),
            FieldPanel('instagram_url'),
            FieldPanel('linkedin_url'),
        ], heading="Social Media Channels (Displayed in Header & Footer if configured)"),

        MultiFieldPanel([
            FieldPanel('logo'),
            FieldPanel('right_logo'),
            FieldPanel('site_title_line_1'),
            FieldPanel('site_title_line_2'),
            FieldPanel('site_title_line_3'),
            FieldPanel('site_title_line_4'),
            FieldPanel('site_title_line_5'),
            FieldPanel('site_title_line_6'),
            FieldPanel('site_title'),
            FieldPanel('site_subtitle'),
        ], heading="Header Branding & Content Lines"),

        MultiFieldPanel([
            FieldPanel('enable_header_search'),
            FieldPanel('header_search_placeholder'),
            FieldPanel('header_css'),
            FieldPanel('header_js'),
        ], heading="Header Search & Custom Scripts"),

        MultiFieldPanel([
            FieldPanel('footer_about_title'),
            FieldPanel('footer_about_text'),
            FieldPanel('footer_address'),
            FieldPanel('footer_email'),
            FieldPanel('footer_phone'),
            FieldPanel('copyright_text'),
        ], heading="Footer Customization"),

        MultiFieldPanel([
            FieldPanel('custom_header_html'),
            FieldPanel('custom_footer_html'),
            FieldPanel('additional_css'),
        ], heading="Advanced HTML/CSS Overrides"),
    ]


@register_setting
class AdminBrandingSettings(BaseGenericSetting):
    logo_left = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Admin Left Logo",
        help_text="Upload/Select logo for the left side of the Wagtail admin sidebar."
    )
    logo_right = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Admin Right Logo (Optional)",
        help_text="Upload/Select logo for the right side of the Wagtail admin header."
    )
    custom_css = models.TextField(
        blank=True,
        verbose_name="Custom CSS Styles",
        help_text="Write custom CSS rules to beautify the admin dashboard."
    )
    custom_js = models.TextField(
        blank=True,
        verbose_name="Custom JS Script",
        help_text="Write custom JavaScript behaviors for the admin dashboard."
    )

    panels = [
        FieldPanel('logo_left'),
        FieldPanel('logo_right'),
        FieldPanel('custom_css'),
        FieldPanel('custom_js'),
    ]



# ---------------------------------------------------------------------------
# THEME PRESETS & ThemeSettings
# ---------------------------------------------------------------------------

THEME_PRESETS = {
    'saffron_navy': {
        'primary':            '#003366',
        'secondary':          '#f39c12',
        'navbar_bg':          '#003366',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#f39c12',
        'navbar_hover_text':  '#000000',
        'card_header_bg':     '#f39c12',
        'card_header_text':   '#000000',
        'table_header_bg':    '#f39c12',
        'table_header_text':  '#000000',
        'btn_bg':             '#f39c12',
        'btn_text':           '#000000',
        'btn_border':         '#d38307',
        'footer_bg':          '#111827',
    },
    'royal_blue': {
        'primary':            '#1a237e',
        'secondary':          '#ffd600',
        'navbar_bg':          '#1a237e',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#ffd600',
        'navbar_hover_text':  '#000000',
        'card_header_bg':     '#ffd600',
        'card_header_text':   '#000000',
        'table_header_bg':    '#ffd600',
        'table_header_text':  '#000000',
        'btn_bg':             '#ffd600',
        'btn_text':           '#000000',
        'btn_border':         '#c8a800',
        'footer_bg':          '#0d1547',
    },
    'emerald_green': {
        'primary':            '#1b5e20',
        'secondary':          '#4caf50',
        'navbar_bg':          '#1b5e20',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#4caf50',
        'navbar_hover_text':  '#ffffff',
        'card_header_bg':     '#4caf50',
        'card_header_text':   '#ffffff',
        'table_header_bg':    '#4caf50',
        'table_header_text':  '#ffffff',
        'btn_bg':             '#4caf50',
        'btn_text':           '#ffffff',
        'btn_border':         '#388e3c',
        'footer_bg':          '#0a1f0d',
    },
    'digital_slate': {
        'primary':            '#283593',
        'secondary':          '#00838f',
        'navbar_bg':          '#283593',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#00838f',
        'navbar_hover_text':  '#ffffff',
        'card_header_bg':     '#00838f',
        'card_header_text':   '#ffffff',
        'table_header_bg':    '#00838f',
        'table_header_text':  '#ffffff',
        'btn_bg':             '#00838f',
        'btn_text':           '#ffffff',
        'btn_border':         '#006064',
        'footer_bg':          '#0d1226',
    },
    'maroon_gold': {
        'primary':            '#880e4f',
        'secondary':          '#f9a825',
        'navbar_bg':          '#880e4f',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#f9a825',
        'navbar_hover_text':  '#000000',
        'card_header_bg':     '#f9a825',
        'card_header_text':   '#000000',
        'table_header_bg':    '#f9a825',
        'table_header_text':  '#000000',
        'btn_bg':             '#f9a825',
        'btn_text':           '#000000',
        'btn_border':         '#c17900',
        'footer_bg':          '#1a0010',
    },
    'clean_light': {
        'primary':            '#455a64',
        'secondary':          '#607d8b',
        'navbar_bg':          '#455a64',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#607d8b',
        'navbar_hover_text':  '#ffffff',
        'card_header_bg':     '#607d8b',
        'card_header_text':   '#ffffff',
        'table_header_bg':    '#607d8b',
        'table_header_text':  '#ffffff',
        'btn_bg':             '#607d8b',
        'btn_text':           '#ffffff',
        'btn_border':         '#455a64',
        'footer_bg':          '#263238',
    },
    'custom': {
        'primary':            '#003366',
        'secondary':          '#f39c12',
        'navbar_bg':          '#003366',
        'navbar_text':        '#ffffff',
        'navbar_hover_bg':    '#f39c12',
        'navbar_hover_text':  '#000000',
        'card_header_bg':     '#f39c12',
        'card_header_text':   '#000000',
        'table_header_bg':    '#f39c12',
        'table_header_text':  '#000000',
        'btn_bg':             '#f39c12',
        'btn_text':           '#000000',
        'btn_border':         '#d38307',
        'footer_bg':          '#111827',
    },
}

THEME_CHOICES = [
    ('saffron_navy',   '🟠 Saffron & Navy Blue (Official Portal - Default)'),
    ('royal_blue',     '🔵 Royal Government Blue & Gold'),
    ('emerald_green',  '🟢 Emerald Health & Forest Green'),
    ('digital_slate',  '🟣 Digital Indigo & Slate Teal'),
    ('maroon_gold',    '🔴 Heritage Maroon & Gold'),
    ('clean_light',    '⚪ Clean Minimalist Light Slate'),
    ('custom',         '🎨 Custom Colors (Configured Below)'),
]


@register_setting
class ThemeSettings(BaseGenericSetting):
    active_theme = models.CharField(
        max_length=50,
        choices=THEME_CHOICES,
        default='saffron_navy',
        verbose_name='Active Theme Preset',
        help_text='Select a pre-designed government theme preset. All colors across the portal will instantly update.',
    )

    # Custom color overrides (only used when active_theme == 'custom')
    custom_primary          = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Primary Color', help_text='e.g. #003366')
    custom_secondary        = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Secondary / Accent Color', help_text='e.g. #f39c12')
    custom_navbar_bg        = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Navbar Background', help_text='e.g. #003366')
    custom_navbar_text      = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Navbar Text Color', help_text='e.g. #ffffff')
    custom_card_header_bg   = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Card / Table Header Color', help_text='e.g. #f39c12')
    custom_card_header_text = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Header Text Color', help_text='e.g. #000000')
    custom_footer_bg        = models.CharField(max_length=20, blank=True, default='', verbose_name='Custom Footer Background', help_text='e.g. #111827')

    panels = [
        MultiFieldPanel([
            FieldPanel('active_theme'),
        ], heading='Theme Preset'),
        MultiFieldPanel([
            FieldPanel('custom_primary'),
            FieldPanel('custom_secondary'),
            FieldPanel('custom_navbar_bg'),
            FieldPanel('custom_navbar_text'),
            FieldPanel('custom_card_header_bg'),
            FieldPanel('custom_card_header_text'),
            FieldPanel('custom_footer_bg'),
        ], heading='Custom Colors (Only when "Custom Colors" preset is selected)'),
    ]

    def get_css_variables(self):
        """Return a dict of CSS variable values for the active theme."""
        if self.active_theme == 'custom':
            preset = THEME_PRESETS['custom'].copy()
            overrides = {
                'primary':          self.custom_primary,
                'secondary':        self.custom_secondary,
                'navbar_bg':        self.custom_navbar_bg,
                'navbar_text':      self.custom_navbar_text,
                'card_header_bg':   self.custom_card_header_bg,
                'card_header_text': self.custom_card_header_text,
                'footer_bg':        self.custom_footer_bg,
            }
            for k, v in overrides.items():
                if v:
                    preset[k] = v
            # Sync table/btn from card_header/secondary if not explicitly overridden
            if 'table_header_bg' not in overrides or not self.custom_card_header_bg:
                preset['table_header_bg'] = preset['card_header_bg']
            if 'table_header_text' not in overrides or not self.custom_card_header_text:
                preset['table_header_text'] = preset['card_header_text']
            preset['btn_bg'] = preset['secondary']
            preset['btn_text'] = preset['card_header_text']
            preset['btn_border'] = preset['secondary']
            preset['navbar_hover_bg'] = preset['secondary']
            preset['navbar_hover_text'] = preset['card_header_text']
            return preset
        return THEME_PRESETS.get(self.active_theme, THEME_PRESETS['saffron_navy'])

    def __str__(self):
        return f'Theme Settings — {self.get_active_theme_display()}'

    class Meta:
        verbose_name = 'Theme Settings'
        verbose_name_plural = 'Theme Settings'


# --- CUSTOM SNIPPETS ---

class MenuTreePreviewPanel(Panel):
    class BoundPanel(Panel.BoundPanel):
        def render_html(self, parent_context=None):
            if self.instance and self.instance.pk:
                return self.instance.get_tree_preview_html()
            return mark_safe("<div style='padding: 12px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; color: #64748b;'>Save this menu first to see tree hierarchy preview.</div>")


@register_snippet
class Menu(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def get_tree_preview_html(self):
        items = list(self.menu_items.all())
        if not items:
            return mark_safe("<div style='padding: 12px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; color: #64748b;'>No menu items added yet. Add items below and save to see tree hierarchy.</div>")

        children_map = {}
        top_level = []
        for item in items:
            p_id = item.parent_id
            if p_id is None:
                top_level.append(item)
            else:
                children_map.setdefault(p_id, []).append(item)

        def render_node(item, level=0):
            html = f"<li style='margin-bottom: 6px; list-style-type: none;'>"
            badge_bg = "#f39c12" if level == 0 else ("#2f2dd3" if level == 1 else "#059669")
            text_color = "#ffffff" if level > 0 else "#000000"
            level_name = "TOP MENU" if level == 0 else f"SUBMENU LEVEL {level}"
            html += f"<div style='display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>"
            html += f"<span style='padding: 2px 8px; background: {badge_bg}; color: {text_color}; border-radius: 4px; font-weight: 700; font-size: 11px; text-transform: uppercase;'>{level_name}</span>"
            html += f"<strong style='color: #0f172a; font-size: 14px;'>{item.link_text}</strong>"
            if item.link_url:
                html += f"<span style='color: #64748b; font-size: 12px;'>({item.link_url})</span>"
            elif item.link_page:
                html += f"<span style='color: #2563eb; font-size: 12px;'>📄 {item.link_page.title}</span>"
            html += "</div>"

            children = children_map.get(item.id, [])
            if children:
                html += f"<ul style='margin-left: 28px; padding-left: 12px; border-left: 2px dashed #94a3b8; margin-top: 8px; margin-bottom: 8px;'>"
                for child in children:
                    html += render_node(child, level + 1)
                html += "</ul>"
            html += "</li>"
            return html

        tree_html = "<div style='background: #f1f5f9; border: 1px solid #cbd5e1; border-radius: 8px; padding: 16px; margin-bottom: 20px;'>"
        tree_html += "<h4 style='margin-top: 0; margin-bottom: 12px; font-size: 14px; font-weight: 700; color: #0f172a; display: flex; align-items: center; gap: 6px;'>🌳 Menu Tree Hierarchy Preview</h4>"
        tree_html += "<ul style='padding-left: 0; margin-bottom: 0;'>"
        for top_item in top_level:
            tree_html += render_node(top_item, 0)
        tree_html += "</ul></div>"
        return mark_safe(tree_html)

    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        InlinePanel('menu_items', label="Menu Items")
    ]

    def __str__(self):
        return self.title


class MenuItem(Orderable):
    menu = ParentalKey(Menu, related_name='menu_items')

    def __str__(self):
        return self.link_text

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Parent Menu Item",
        help_text="Select a parent menu item if this is a submenu item (supports up to 5 levels)."
    )
    link_text = models.CharField(max_length=50)
    link_url = models.CharField(max_length=255, blank=True, help_text="For external links or paths (e.g., https://google.com or /contact/)")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='+'
    )
    open_in_new_tab = models.BooleanField(default=False)

    panels = [
        FieldPanel('link_text'),
        FieldPanel('parent'),
        FieldPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('open_in_new_tab'),
    ]

    @property
    def url(self):
        if self.link_page:
            page_url = self.link_page.url
            if page_url:
                return page_url
        return self.link_url or '#'


# --- PAGES MODELS ---

class HomePage(Page):
    subpage_types = [
        'home.StandardPage',
        'home.CustomHTMLPage',
        'home.NewsIndexPage',
        'home.NoticeIndexPage',
        'home.GovtOrderIndexPage',
        'home.ProgramImplementationPlanPage',
        'home.RtiPage',
        'home.DownloadsPage',
        'home.FormPage',
    ]
    parent_page_types = ['wagtailcore.Page']

    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # Dynamic feeds for home page
        context['news_pages'] = NewsPage.objects.live().public().order_by('-date')[:3]
        context['notice_pages'] = NoticePage.objects.live().public().order_by('-date')[:5]
        context['govt_orders'] = GovtOrderPage.objects.live().public().order_by('-order_date')[:5]
        # Resolve index pages dynamically
        context['news_index'] = NewsIndexPage.objects.live().public().first()
        context['notice_index'] = NoticeIndexPage.objects.live().public().first()
        context['govt_order_index'] = GovtOrderIndexPage.objects.live().public().first()
        return context


class StandardPage(Page):
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]


class CustomHTMLPage(Page):
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]


class NewsIndexPage(Page):
    intro = RichTextField(blank=True)
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['news_pages'] = NewsPage.objects.child_of(self).live().public().order_by('-date')
        return context


class NewsPage(Page):
    date = models.DateField("Post date")
    intro = models.CharField(max_length=250, blank=True)
    body = RichTextField(blank=True)
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body'),
        FieldPanel('image'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('document'),
    ]


class NoticeIndexPage(Page):
    intro = RichTextField(blank=True)
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['notice_pages'] = NoticePage.objects.child_of(self).live().public().order_by('-date')
        return context


class NoticePage(Page):
    date = models.DateField("Notice Date")
    expiry_date = models.DateField("Expiry Date", null=True, blank=True)
    body = RichTextField(blank=True)
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('expiry_date'),
        FieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('document'),
    ]


class GovtOrderIndexPage(Page):
    intro = RichTextField(blank=True)
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('body'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        orders = GovtOrderPage.objects.child_of(self).live().public().order_by('-order_date')

        # Filter by department
        dept = request.GET.get('department', '')
        if dept:
            orders = orders.filter(department=dept)

        # Filter by search query
        q = request.GET.get('q', '')
        if q:
            orders = orders.filter(
                models.Q(title__icontains=q) |
                models.Q(order_number__icontains=q) |
                models.Q(subject__icontains=q)
            )

        context['orders'] = orders
        context['departments'] = GovtOrderPage.DEPARTMENT_CHOICES
        context['selected_dept'] = dept
        context['q'] = q
        return context


class GovtOrderPage(Page):
    DEPARTMENT_CHOICES = [
        ('finance', 'Department of Finance'),
        ('education', 'Department of Education'),
        ('health', 'Department of Health & Family Welfare'),
        ('home', 'Department of Home Affairs'),
        ('it', 'Department of Information Technology'),
        ('general', 'General Administration Department'),
    ]

    order_number = models.CharField("Order/Notification Number", max_length=100)
    order_date = models.DateField("Issue Date")
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='general')
    subject = models.TextField("Subject / Short Description")
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    search_fields = Page.search_fields + [
        index.SearchField('order_number'),
        index.SearchField('subject'),
    ]

    content_panels = Page.content_panels + [
        FieldPanel('order_number'),
        FieldPanel('order_date'),
        FieldPanel('department'),
        FieldPanel('subject'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('document'),
    ]


class ProgramPlan(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the plan")
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload/Select the plan document (PDF/Word/etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('document'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Program Plan"
        verbose_name_plural = "Program Plans"


class ProgramImplementationPlanPage(Page):
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)
    custom_css = models.TextField(blank=True, verbose_name="Page Global Custom CSS", help_text="Write custom CSS styles specific to this page.")
    custom_js = models.TextField(blank=True, verbose_name="Page Global Custom JS", help_text="Write custom JavaScript specific to this page.")

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('custom_css'),
        FieldPanel('custom_js'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['plans'] = ProgramPlan.objects.all().order_by('-created_at')
        return context


class RtiDisclosure(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the disclosure document")
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload/Select the RTI document (PDF/Word/etc.)"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('document'),
    ]

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "RTI Disclosure"
        verbose_name_plural = "RTI Disclosures"


class RtiPage(Page):
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)
    custom_css = models.TextField(blank=True, verbose_name="Page Global Custom CSS", help_text="Write custom CSS styles specific to this page.")
    custom_js = models.TextField(blank=True, verbose_name="Page Global Custom JS", help_text="Write custom JavaScript specific to this page.")

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('custom_css'),
        FieldPanel('custom_js'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context['disclosures'] = RtiDisclosure.objects.all().order_by('-created_at')
        return context


class LogoSlider(ClusterableModel):
    name = models.CharField(
        max_length=255, 
        blank=True,  # Add this
        null=True,   # Add this
        help_text="Name of this logo slider (for internal reference)"
    )

    panels = [
        FieldPanel('name'),
        InlinePanel('logos', label="Logos"),
    ]

    def __str__(self):
        return self.name or "Unnamed Logo Slider"  # Handle empty names

    class Meta:
        verbose_name = "Logo Slider"
        verbose_name_plural = "Logo Sliders"

class LogoSliderItem(Orderable):
    logo_slider = ParentalKey(LogoSlider, on_delete=models.CASCADE, related_name='logos')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Logo Image"
    )
    title = models.CharField(max_length=255, blank=True, help_text="Alt text / title for the logo")
    link_url = models.CharField(max_length=255, blank=True, help_text="Optional external link URL")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('title'),
        FieldPanel('link_url'),
        FieldPanel('link_page'),
    ]


from wagtail.snippets.views.snippets import SnippetViewSet

class LogoSliderViewSet(SnippetViewSet):
    model = LogoSlider
    icon = 'image'
    menu_label = 'Logo Sliders'
    menu_name = 'logo_sliders'
    menu_order = 350
    add_to_admin_menu = True

register_snippet(LogoSlider, viewset=LogoSliderViewSet)


class QuickLinksCarousel(ClusterableModel):
    name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Internal name for this carousel (e.g. Main Quick Links)",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional section title shown above the circles on the website",
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('title'),
        InlinePanel('links', label="Quick Links"),
    ]

    def __str__(self):
        return self.name or self.title or "Unnamed Quick Links Carousel"

    class Meta:
        verbose_name = "Quick Links Carousel"
        verbose_name_plural = "Quick Links Carousels"


class QuickLinksCarouselItem(Orderable):
    BORDER_COLORS = [
        ('blue', 'Theme Blue'),
        ('orange', 'Theme Orange'),
        ('green', 'Theme Green'),
        ('red', 'Theme Red'),
    ]

    carousel = ParentalKey(QuickLinksCarousel, on_delete=models.CASCADE, related_name='links')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        verbose_name="Icon Image",
    )
    title = models.CharField(max_length=100, help_text="Text displayed below the icon")
    link_url = models.CharField(max_length=255, blank=True, help_text="Optional external link URL")
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    border_color = models.CharField(
        max_length=20,
        choices=BORDER_COLORS,
        default='orange',
        verbose_name="Circle Border Color",
    )

    panels = [
        FieldPanel('image'),
        FieldPanel('title'),
        FieldPanel('link_url'),
        FieldPanel('link_page'),
        FieldPanel('border_color'),
    ]


class QuickLinksCarouselViewSet(SnippetViewSet):
    model = QuickLinksCarousel
    icon = 'link'
    menu_label = 'Quick Links Carousel'
    menu_name = 'quick_links_carousels'
    menu_order = 355
    add_to_admin_menu = True
    list_display = ['name', 'title']
    search_fields = ['name', 'title']


# Registered in home/wagtail_hooks.py (same pattern as Program Plans / RTI)
# so it appears in the main admin sidebar next to Logo Sliders.


class Download(models.Model):
    title = models.CharField(max_length=255, help_text="Title of the download")
    subtitle = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Subtitle / Short Description",
        help_text="Optional short description or subtitle for this document"
    )
    category = models.CharField(
        max_length=100,
        default='general',
        blank=True,
        verbose_name="Category / Key",
        help_text="Filter key/category to identify where this download belongs (e.g. 'general', 'reports', 'circulars'). Default is 'general'."
    )
    document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Upload/Select the PDF/Document file to download"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('subtitle'),
        FieldPanel('category'),
        FieldPanel('document'),
    ]

    def __str__(self):
        return f"{self.title} ({self.category})" if self.category else self.title

    class Meta:
        verbose_name = "Download"
        verbose_name_plural = "Downloads"


def get_download_categories():
    try:
        from home.models import Download
        cats = Download.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()
        unique_cats = sorted(set(c.strip() for c in cats if c and c.strip()))
        choices = [('', '— All Categories / Auto Match Page Title —')]
        for c in unique_cats:
            choices.append((c, c))
        return choices
    except Exception:
        return [('', '— All Categories / Auto Match Page Title —')]


class DownloadsPage(Page):
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)
    category_select = models.CharField(
        max_length=100,
        blank=True,
        default="",
        choices=get_download_categories,
        verbose_name="Select Category from Existing Downloads",
        help_text="Select a category from the dropdown (automatically populated from your Portal Content ➔ Downloads snippets)."
    )
    category_filter = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Or Type Custom Category Filter",
        help_text="Optional: Type category name manually if not in dropdown or to filter by custom keyword. Type 'all' to show every download."
    )
    custom_css = models.TextField(blank=True, verbose_name="Page Global Custom CSS", help_text="Write custom CSS styles specific to this page.")
    custom_js = models.TextField(blank=True, verbose_name="Page Global Custom JS", help_text="Write custom JavaScript specific to this page.")

    content_panels = Page.content_panels + [
        FieldPanel('category_select'),
        FieldPanel('category_filter'),
        FieldPanel('body'),
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('custom_css'),
        FieldPanel('custom_js'),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        all_downloads = list(Download.objects.all().order_by('-created_at'))

        cat_filter = (self.category_select or self.category_filter or '').strip()

        if not cat_filter or cat_filter.lower() == 'all':
            # Check if any match page title or slug exactly (case-insensitive)
            page_title = (self.title or '').strip().lower()
            page_slug = (self.slug or '').strip().lower().replace('-', ' ')
            matched_page = [
                d for d in all_downloads
                if d.category and (d.category.strip().lower() == page_title or d.category.strip().lower() == page_slug)
            ]
            if matched_page:
                context['downloads'] = matched_page
                context['active_category'] = matched_page[0].category if matched_page else ""
                return context
            context['downloads'] = all_downloads
            context['active_category'] = ""
            return context

        # STRICT MATCHING: Exact case-insensitive match only
        target_cat = cat_filter.strip().lower()
        matched = [
            d for d in all_downloads
            if d.category and d.category.strip().lower() == target_cat
        ]
        context['downloads'] = matched
        context['active_category'] = cat_filter
        return context


# --- DYNAMIC FORM BUILDER (PATTERN 1) ---

CUSTOM_FORM_FIELD_CHOICES = list(FORM_FIELD_CHOICES) + [
    ('file', 'File upload'),
]


class CustomFormBuilder(FormBuilder):
    def create_file_field(self, field, options):
        return forms.FileField(**options)


class FormField(AbstractFormField):
    page = ParentalKey('FormPage', on_delete=models.CASCADE, related_name='form_fields')
    field_type = models.CharField(
        verbose_name='field type',
        max_length=16,
        choices=CUSTOM_FORM_FIELD_CHOICES,
    )

    panels = [
        FieldPanel('label'),
        FieldPanel('help_text'),
        FieldPanel('required'),
        FieldPanel('field_type', widget=forms.Select(choices=CUSTOM_FORM_FIELD_CHOICES)),
        FieldPanel('choices'),
        FieldPanel('default_value'),
    ]


class FormPage(AbstractEmailForm):
    form_builder = CustomFormBuilder

    intro = RichTextField(blank=True, help_text="Text shown above the form")
    thank_you_text = RichTextField(blank=True, help_text="Text shown after form submission")
    body = StreamField(PAGE_BUILDER_BLOCKS, blank=True, use_json_field=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        InlinePanel('form_fields', label="Form Fields"),
        FieldPanel('thank_you_text'),
        FieldPanel('body'),
        FormSubmissionsPanel(),
    ]

    def process_form_submission(self, form):
        form_data = form.cleaned_data.copy()
        for field_name, value in form_data.items():
            if hasattr(value, 'name'):
                form_data[field_name] = value.name
        return self.get_submission_class().objects.create(
            form_data=form_data,
            page=self,
        )


# --- DYNAMIC ADMIN CUSTOM DATA RECORDS (PATTERN 3 ADMIN SIDEBAR) ---

class DynamicAttributeStructBlock(blocks.StructBlock):
    field_name = blocks.CharBlock(label="Field Name / Column Header", help_text="e.g. Closing Date, EMD Amount, Email, Designation, Budget, Phone")
    field_type = blocks.ChoiceBlock(
        choices=[
            ('text', 'Text (Normal string)'),
            ('number', 'Numerical (Numbers / Currency / Count)'),
            ('date', 'Date / Deadline'),
            ('email', 'Email Address (Clickable mailto link)'),
            ('url', 'Website / Link URL (Clickable link)'),
            ('phone', 'Phone / Mobile Number (Clickable tel link)'),
        ],
        default='text',
        label="Field Type / Input Type",
        help_text="Select input data type for formatting and interactive links"
    )
    field_value = blocks.CharBlock(label="Field Value")


@register_snippet
class CustomDataRecord(models.Model):
    title = models.CharField(max_length=255, help_text="Title or name of this record")
    category = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="Category / Group Key (e.g., Schemes, Tenders, Staff Directory, Projects, FAQs)"
    )
    subtitle = models.CharField(max_length=255, blank=True, help_text="Optional subtitle or reference number")
    document = models.ForeignKey(
        'wagtaildocs.Document',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        help_text="Optional PDF or file attachment"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    extra_fields = StreamField([
        ('attribute', DynamicAttributeStructBlock()),
    ], use_json_field=True, blank=True, help_text="Add dynamic custom fields specific to this record")

    panels = [
        FieldPanel('title'),
        FieldPanel('category'),
        FieldPanel('subtitle'),
        FieldPanel('document'),
        FieldPanel('extra_fields'),
    ]

    def __str__(self):
        return f"[{self.category}] {self.title}"

    class Meta:
        verbose_name = "Custom Data Record"
        verbose_name_plural = "Custom Data Records"



