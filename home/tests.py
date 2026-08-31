from home.models import HomePage

from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase


class HomeSetUpTests(WagtailPageTestCase):
    """
    Tests for basic page structure setup and HomePage creation.
    """

    def test_root_create(self):
        root_page = Page.objects.get(pk=1)
        self.assertIsNotNone(root_page)

    def test_homepage_create(self):
        root_page = Page.objects.get(pk=1)
        homepage = HomePage(title="Home")
        root_page.add_child(instance=homepage)
        self.assertTrue(HomePage.objects.filter(title="Home").exists())


class HomeTests(WagtailPageTestCase):
    """
    Tests for homepage functionality and rendering.
    """

    def setUp(self):
        """
        Create a homepage instance for testing.
        """
        root_page = Page.get_first_root_node()
        Site.objects.create(hostname="testsite", root_page=root_page, is_default_site=True)
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)

    def test_homepage_is_renderable(self):
        self.assertPageIsRenderable(self.homepage)

    def test_homepage_template_used(self):
        response = self.client.get(self.homepage.url)
        self.assertTemplateUsed(response, "home/home_page.html")


from home.models import ProgramImplementationPlanPage, ProgramPlan
from wagtail.documents.models import Document
from django.core.files.uploadedfile import SimpleUploadedFile

class ProgramImplementationPlanTests(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        # Clean up any existing default sites to prevent multi-default-site conflicts
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", port=80, root_page=root_page, is_default_site=True)
        
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        
        self.plan_page = ProgramImplementationPlanPage(title="Program Implementation Plan")
        self.homepage.add_child(instance=self.plan_page)
        
        # Create a dummy document
        dummy_file = SimpleUploadedFile("test_plan.pdf", b"pdf content", content_type="application/pdf")
        self.document = Document.objects.create(title="Test Plan Doc", file=dummy_file)
        
        # Create a program plan snippet
        self.plan = ProgramPlan.objects.create(title="Test Program Plan", document=self.document)

    def test_plan_page_is_renderable(self):
        self.assertPageIsRenderable(self.plan_page)

    def test_plan_page_renders_plans(self):
        response = self.client.get(self.plan_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Program Plan")
        self.assertContains(response, self.document.url)

    def test_plan_page_renders_custom_css_js(self):
        self.plan_page.custom_css = "body { background-color: purple; }"
        self.plan_page.custom_js = "console.log('test-plan-js');"
        self.plan_page.save()
        response = self.client.get(self.plan_page.url)
        self.assertContains(response, "body { background-color: purple; }")
        self.assertContains(response, "console.log('test-plan-js');")


from home.models import RtiPage, RtiDisclosure

class RtiPageTests(WagtailPageTestCase):
    def setUp(self):
        root_page = Page.get_first_root_node()
        Site.objects.all().delete()
        Site.objects.create(hostname="localhost", port=80, root_page=root_page, is_default_site=True)
        
        self.homepage = HomePage(title="Home")
        root_page.add_child(instance=self.homepage)
        
        self.rti_page = RtiPage(title="RTI Disclosures under Sec 4")
        self.homepage.add_child(instance=self.rti_page)
        
        # Create a dummy document
        dummy_file = SimpleUploadedFile("test_rti.pdf", b"rti content", content_type="application/pdf")
        self.document = Document.objects.create(title="Test RTI Doc", file=dummy_file)
        
        # Create an RTI disclosure snippet
        self.disclosure = RtiDisclosure.objects.create(title="Test RTI Disclosure Section 4(1)(b)(i)", document=self.document)

    def test_rti_page_is_renderable(self):
        self.assertPageIsRenderable(self.rti_page)

    def test_rti_page_renders_disclosures(self):
        response = self.client.get(self.rti_page.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test RTI Disclosure Section 4(1)(b)(i)")
        self.assertContains(response, self.document.url)

    def test_rti_page_renders_custom_css_js(self):
        self.rti_page.custom_css = "body { background-color: pink; }"
        self.rti_page.custom_js = "console.log('test-rti-js');"
        self.rti_page.save()
        response = self.client.get(self.rti_page.url)
        self.assertContains(response, "body { background-color: pink; }")
        self.assertContains(response, "console.log('test-rti-js');")



