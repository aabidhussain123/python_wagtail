from django.db import models
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.search import index
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting
from wagtail.snippets.models import register_snippet
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey


# --- PAGE BUILDER WIDGET BLOCKS ---

class BlockStyleStructBlock(blocks.StructBlock):
    margin_top = blocks.ChoiceBlock(choices=[
        ('mt-0', 'None'),
        ('mt-2', 'Small'),
        ('mt-4', 'Medium'),
        ('mt-5', 'Large'),
    ], default='mt-4', label="Margin Top")
    margin_bottom = blocks.ChoiceBlock(choices=[
        ('mb-0', 'None'),
        ('mb-2', 'Small'),
        ('mb-4', 'Medium'),
        ('mb-5', 'Large'),
    ], default='mb-4', label="Margin Bottom")
    padding_top = blocks.ChoiceBlock(choices=[
        ('pt-0', 'None'),
        ('pt-2', 'Small'),
        ('pt-4', 'Medium'),
        ('pt-5', 'Large'),
    ], default='pt-0', label="Padding Top")
    padding_bottom = blocks.ChoiceBlock(choices=[
        ('pb-0', 'None'),
        ('pb-2', 'Small'),
        ('pb-4', 'Medium'),
        ('pb-5', 'Large'),
    ], default='pb-0', label="Padding Bottom")
    custom_class = blocks.CharBlock(required=False, label="Custom CSS Class Name", help_text="Add custom CSS class name for styling")
    custom_css = blocks.TextBlock(required=False, label="Custom CSS Styles", help_text="Write custom CSS properties here (e.g. background-color: red; color: white;)")


class SlideBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    title = blocks.CharBlock(required=False, help_text="Title overlay on the slide")
    subtitle = blocks.CharBlock(required=False, help_text="Subtitle overlay on the slide")
    link = blocks.PageChooserBlock(required=False, help_text="Optional page link when slide is clicked")


class SliderBlock(blocks.StructBlock):
    slides = blocks.ListBlock(SlideBlock(), label="Slides Carousel")
    container_width = blocks.ChoiceBlock(choices=[
        ('container', 'Boxed Width (container)'),
        ('container-fluid', 'Full Width (container-fluid)'),
    ], default='container-fluid', label="Container Width", help_text="Choose whether the slider should be full width or boxed width.")
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

    class Meta:
        template = 'home/blocks/slider_block.html'
        icon = 'image'
        label = 'Image Carousel Slider'


class HeroBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    subtitle = blocks.TextBlock(required=False)
    background_image = ImageChooserBlock(required=False)
    cta_text = blocks.CharBlock(required=False, label="CTA Button Text")
    cta_link = blocks.PageChooserBlock(required=False, label="CTA Link Page")
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

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
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

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
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

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
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

    class Meta:
        template = 'home/blocks/content_section_block.html'
        icon = 'doc-full'
        label = 'Content Section Columns'


class NewsNoticeLatestBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False, default="News & Notices", help_text="Header for this section")
    news_count = blocks.IntegerBlock(default=3, min_value=1, max_value=10, label="Number of News Items")
    notice_count = blocks.IntegerBlock(default=5, min_value=1, max_value=10, label="Number of Notices")
    govt_order_count = blocks.IntegerBlock(default=5, min_value=1, max_value=10, label="Number of Government Orders")
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        from home.models import NewsPage, NoticePage, GovtOrderPage
        context['news_pages'] = NewsPage.objects.live().public().order_by('-date')[:value.get('news_count', 3)]
        context['notice_pages'] = NoticePage.objects.live().public().order_by('-date')[:value.get('notice_count', 5)]
        context['govt_orders'] = GovtOrderPage.objects.live().public().order_by('-order_date')[:value.get('govt_order_count', 5)]
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
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

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
    style = BlockStyleStructBlock(label="Advanced Styling Settings", required=False)

    class Meta:
        template = 'home/blocks/quick_buttons_block.html'
        icon = 'link'
        label = 'Quick Buttons Row'


PAGE_BUILDER_BLOCKS = [
    ('hero', HeroBlock()),
    ('slider', SliderBlock()),
    ('featured_pages', FeaturedPagesBlock()),
    ('featured_cards', FeaturedCardsBlock()),
    ('content_section', ContentSectionBlock()),
    ('news_notice_latest', NewsNoticeLatestBlock()),
    ('quick_links_carousel', QuickLinksCarouselBlock()),
    ('quick_buttons', QuickButtonsBlock()),
    ('rich_text', blocks.RichTextBlock()),
    ('raw_html', blocks.RawHTMLBlock(label="Raw HTML")),
]



# --- SITE SETTINGS ---

@register_setting
class HeaderFooterSettings(BaseGenericSetting):
    # Header Fields
    site_title = models.CharField(max_length=255, default="DEPARTMENT OF PUBLIC ADMINISTRATION", verbose_name="Site Title")
    site_subtitle = models.CharField(max_length=255, default="Government Content Management System Portal", verbose_name="Site Subtitle")
    site_title_line_1 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 1 (e.g. Hindi)")
    site_title_line_2 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 2 (e.g. English Main)")
    site_title_line_3 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 3 (e.g. Urdu)")
    site_title_line_4 = models.CharField(max_length=255, blank=True, verbose_name="Site Title Line 4 (e.g. Subtitle)")
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
        verbose_name="Right Site Logo",
        help_text="Upload/Select an optional right-side logo image"
    )
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
            FieldPanel('logo'),
            FieldPanel('right_logo'),
            FieldPanel('site_title'),
            FieldPanel('site_subtitle'),
            FieldPanel('site_title_line_1'),
            FieldPanel('site_title_line_2'),
            FieldPanel('site_title_line_3'),
            FieldPanel('site_title_line_4'),
            FieldPanel('header_css'),
            FieldPanel('header_js'),
        ], heading="Header Customization"),

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



# --- CUSTOM SNIPPETS ---

@register_snippet
class Menu(ClusterableModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        InlinePanel('menu_items', label="Menu Items")
    ]

    def __str__(self):
        return self.title


class MenuItem(Orderable):
    menu = ParentalKey(Menu, related_name='menu_items')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name="Parent Menu Item",
        help_text="Select a parent menu item if this is a submenu item (supports up to 3 levels)."
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

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
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


class NoticeIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
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
        FieldPanel('document'),
    ]


class GovtOrderIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
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
        FieldPanel('document'),
    ]
