from django.db import models
from wagtail.core.models import Page
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.search import index

# Create your models here.
class DepartmentIndexPage(Page):
	body = RichTextField(blank=True)
	content_panels= Page.content_panels + [
			FieldPanel('body',classname="full")
	]

class Department(Page):
	description = models.CharField(max_length=50)
	location = models.CharField(max_length=50)

	search_fields = Page.search_fields + [
		index.SearchField('location')
	]

	content_panels = Page.content_panels + [
		FieldPanel('description', classname='description'),
		FieldPanel('location')
	]