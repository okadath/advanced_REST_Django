from django.test import TestCase

# Create your tests here.
from django.contrib.auth.models import User

from . models import Post
class BlogTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		testuser1=User.objects.create_user(username='testuser1', password='abc123')
		testuser1.save()
		testpost=Post.objects.create(author=testuser1, title='blog', body='bodycontent')
		testpost.save()

	def test_blog_content(self):
		post=Post.objects.get(id=1)
		print(post)
		expected_author=str(post.author)
		expected_title=str(post.title)#f"{post.title}"
		expected_body=str(post.body)#f"{post.body}"
		self.assertEquals(expected_author,'testuser1')
		self.assertEquals(expected_title,'blog')
		self.assertEquals(expected_body,'bodycontent')