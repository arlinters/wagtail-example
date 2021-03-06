from django import forms
from django.db import models
from django.db.models.deletion import SET_NULL
from django.db.models.fields import Field
from django.db.models.fields.related import ForeignKey

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from wagtail.snippets.models import register_snippet

@register_snippet
class BlogCategory(models.Model):
	name = models.CharField(max_length=255)
	icon = models.ForeignKey(
		'wagtailimages.Image', null=True, blank=True,
		on_delete=models.SET_NULL, related_name='+'
	)

	panels = [
		FieldPanel('name'),
		ImageChooserPanel('icon'),
	]

	def __str__(self):
		return self.name
	
	class Meta:
		verbose_name_plural = 'blog cateogires'

class BlogIndexPage(Page):
	intro = RichTextField(blank=True)

	def get_context(self, request, *args, **kwargs):
			# Update context to include only published posts, ordered by reverse-chron
			context = super().get_context(request)
			blogpages = self.get_children().live().order_by('-first_published_at')
			blogpages = blogpages.type(BlogPage)
			context['blogpages'] = blogpages
			return context

	content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")
	]

class BlogTagIndexPage(Page):

    def get_context(self, request):
        # Filter by tag
        tag = request.GET.get('tag')
        blogpages = BlogPage.objects.filter(tags__name=tag)
				
        # Update template context
        context = super().get_context(request)
        context['blogpages'] = blogpages
        return context

class BlogPageTag(TaggedItemBase):
	content_object = ParentalKey(
		'BlogPage',
		related_name='tagged_items',
		on_delete=models.CASCADE
	)

class BlogAuthor(Page):
	firstname = models.CharField(max_length=20)
	lastname = models.CharField(max_length=20)
	description =models.TextField(max_length=120)

	search_fields = Page.search_fields + [
		index.SearchField('firstname'),
		index.SearchField('lastname'),
	]

	content_panels = Page.content_panels + [
		FieldPanel('firstname'),
		FieldPanel('lastname'),
		FieldPanel('description'),
	]

class BlogPage(Page):
	# Database fields
	date = models.DateField("Post date")
	intro = models.CharField(max_length=250)
	body = RichTextField(blank=True)
	tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
	categories = ParentalManyToManyField('blog.BlogCategory', blank=True)
	author = models.ForeignKey('blog.BlogAuthor', on_delete=SET_NULL, null=True)

	def main_image(self):
		gallery_item = self.gallery_images.first()
		if gallery_item:
			return gallery_item.image
		else:
			return None

	# Search index configuration
	search_fields = Page.search_fields + [
			index.SearchField('intro'),
			index.SearchField('body'),
	]

	# Editor panel configuration
	content_panels = Page.content_panels + [
			MultiFieldPanel([
				FieldPanel('date'),
				FieldPanel('tags'),
				FieldPanel('categories', widget=forms.CheckboxSelectMultiple),
				FieldPanel('author')
			], heading="Blog Information"),
			InlinePanel('gallery_images', label='Gallery images'),
			FieldPanel('intro'),
			FieldPanel('body', classname="full"),
	]

class BlogPageGalleryImage(Orderable):
	page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
	image = models.ForeignKey(
		'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
	)
	caption=models.CharField(blank=True,max_length=125)
	panels = [
		ImageChooserPanel('image'),
		FieldPanel('caption')
	]
