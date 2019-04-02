```
startproject blog_project
startapp posts
```
` pip install django djangorestframework `


agregar las apps `rest_framework` y `posts`al settings y migrar

en el settings agregar:
```python
REST_FRAMEWORK={
	'DEFAULT_PERMISSION_CLASSES':[
		'rest_framework.permissions.AllowAny',
	]
}
```

editar el modelo `posts/models.py`

```python
from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Post(models.Model):
	author=models.ForeignKey(User, on_delete=models.CASCADE)
	title=models.CharField(max_length=50)
	body=models.TextField()
	created_at=models.DateTimeField(auto_now_add=True)
	updated_at=models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.title#buena practica
```

```
python manage.py makemigrations posts
python manage.py migrate
```

creamos en posts/admin

```python
from django.contrib import admin

# Register your models here.

from . models import Post
admin.site.register(Post)
```

y creamos superuser
 luego creamos un post

en `posts/test.py`:


```python
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
```

y correr con `python manage.py test`

### REST

hay tres pasos principales
+ urls.py para las rutas de urls
+ derializers.py para convertir datos en JSON
+ views.py para aplicar la logica de cada API endpoint

en blog_project/urls.py para configurar los endpoints:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/',include('posts.urls')),
]
```
se le pone v1 por que es buena practica un versionado de apis(no borrar las anteriores :v)
si hubiera muchas apps quiza convendria meter sus rutas en una `API` app 

crear un `posts/url.py`:
```python
from django.urls import path
from .views import PostList, PostDetail

urlpatterns=[
	path('',PostList.as_view()),
	path('<int:pk>/',PostDetail.as_view()),
]
```

hasta aqui todas las urls seran api/v1/#

creamos un `posts/serializers.py`

aqui incluiremos apra la api el Id por default de django pero no el updated_at

```python
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
	class Meta:
		fields=('id','author','title','body','created_at',)
		model=Post
```

en el `posts/views.py`
el ListAPIView nos da un solo lectura endpoint
el RetriveAPIView nos da un solo item solo lectura

para crear debemos usar ListCreateAPIView ytambien el RetriveUpdateDestroyAPIView:
```python
from rest_framework import generics
from .models import Post
from .serializers import PostSerializer

class PostList(generics.ListCreateAPIView):
	queryset=Post.objects.all()
	serializer_class=PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset=Post.objects.all()
	serializer_class=
	```










