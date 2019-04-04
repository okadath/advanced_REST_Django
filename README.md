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
	serializer_class=PostSerializer
```
agregar al `blog_project/urls.py`:

```python
    path('api-auth/',include('rest_framework.urls')),
```
y esto nos permite logearnos desd eel restdjangofw

pero cualquier usuario aun puede editar info privada por que asi lo configuramos
```python
REST_FRAMEWORK={
	'DEFAULT_PERMISSION_CLASSES':[
		'rest_framework.permissions.AllowAny',
	]
}
```

queremos restingirlo, se puede hacer a nivel de este proyecto, nivel vistas o nivel objeto
como solo tenemos dos vistas lo ahremos primero a nivel vista
#### View_level
editar `posts/views.py` y agregar los `permission_clases`:
```python
from rest_framework import generics, permissions
from .models import Post
from .serializers import PostSerializer

class PostList(generics.ListAPIView):
	permission_classes=(permissions.IsAuthenticated,)
	queryset=Post.objects.all()
	serializer_class=PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
	permission_classes=(permissions.IsAuthenticated,)
	queryset=Post.objects.all()
	serializer_class=PostSerializer
```
peeero si el proyecto crece no conviene hacerlo por vistas

#### Project_level
REST fw tiene muchas configuraciones d epermisos
+ AllowAny: cualquiera accede
+ IsAuthenticated: solo autenticados
+ IsAdminUser:solo admin/superusers
+ IsAuthenticatedOrReadOnly:usuarios noauth pueden ver pero solo auth pueden hacer CRUD

entonces probaremos el IsAuthenticated:
```python
REST_FRAMEWORK={
	'DEFAULT_PERMISSION_CLASSES':[
		'rest_framework.permissions.IsAuthenticated',
	]
}
```
y dejamos el `posts/views.py` como estaba originalmente
```python
from rest_framework import generics
from .models import Post
from .serializers import PostSerializer

class PostList(generics.ListAPIView):
	queryset=Post.objects.all()
	serializer_class=PostSerializer

class PostDetail(generics.RetrieveUpdateDestroyAPIView):
	queryset=Post.objects.all()
	serializer_class=PostSerializer
```

#### Custom permissions(nivel objeto)
queremos que solo el autor de un blog sea quien hace update/delete si no solo lo lee
los superusers editaran todo pero los normales solo los suyos

internamente RESTFW posee una clase BasePermission en el cual le sobreescribiremos el metodo has_object_permission

crear `posts/permissions.py`:

```python
from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):

  def has_object_permission(self, request, view, obj):
    # Read-only permissions are allowed for any request
    if request.method in permissions.SAFE_METHODS:
      return True
    return obj.author == request.user
```

debemos importarlo desde el `posts/views.py`:
```python
from rest_framework import generics

from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer


class PostList(generics.ListCreateAPIView):
  queryset = Post.objects.all()
  serializer_class = PostSerializer


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
  permission_classes = (IsAuthorOrReadOnly,)
  queryset = Post.objects.all()
  serializer_class = PostSerializer

```
este permiso solo devuelve un valor, para filtrado nivel objeto en listas para colecciones o instancias, se debe hacer un overriding the initial queryset


### User auth
lo anterior era autorizacion, ahora haremos autenticacion(sign up log in/out)
django normalmente usa un pattern session-bassed cookie

en las SPI le pasamos un identificador por request, RESTFW permite 4 tipos de....
y ademas muchos ofrecen json webtokens JWT

#### Basic Auth
el cliente es forzado a enviar sus credenciales
```
cliente		server
	----->
	get /http

	<-----
	http 401 no auth
	wwwauth:basic

	----->
	get http/header:auth: basic 123qweas

	<-----
	http 200 OK
```

las credenciales enviadas son una version unencrypted base64 encoded de username:password
es ineficiente por que se pasa esto sin cifrar y se tiene que verificar siempre si est alogeado o no, solo usarlo con https

#### Session auth

django usa una mezcla de sessions/cookies
el cliente se autentica y recibe un sessionID del server que se almacena en una cookie, el sessionID es pasado como cbecera en las httprequest


esto es stateful por que se mandiene almacenado en ambos, server/cliente
 el defecto es que esto depende del navegador y las cookies no trabajan en multiples dominios, como apps
 cuando hay muchos servers es dificil manejar la autenticacion de un solo cliente actualizada
 esto no sirve con APIs de multiple frontend

#### Token auth
es el mas comun por las SPA, es stateless, el cliente manda sus credenciales al server, este enera un token que se almacena en local o como cookie

este token se pasa como header en cada request y el server lo usa para verificar si esta autenticado, pero no lo almacena, solo verifica si es valido o no
las cookies estan creadas para leer info del lado del server y se envian en cada http request
el almacenamiento local esta dise;ado para informacion del cliente, almacena mas y no es mandada por default en cada httprequest

ambos tokens son vulnerables al XSSattack
por ello las cookies deben ir con las banderas `httpOnly` y `Secure`
```
cliente		server
	----->
	get /http

	<-----
	http 401 no auth
	wwwauth:token

	----->
	get http/header:auth: token 123qweas

	<-----
	http 200 OK
```
como se almacenan en el cliente escalar los servers sin actualizar la sesion es facil y se pueden usar muchos frontends
el mismo token representa el usuario en web o en mobil
problema: pueden crecer mucho, ya que llevan toda la info del cliente, no solo el id


las implementaciones varian, pero RESTFW posee un TokenAuthentication, que no posee expiracion(hay que implementarla)
solo genera un token por usuario(web/mobil usan el mismo)por lo cual puede haber problemas de mantenimiento y actualizacion de 2 conjuntos de informacion de un cliente

JWTson versiones nuevas de tokens que se agregan por paquetes de terceros como auth0
poseen token expiration y pueden generar unique tokens clients

**Default auth***

actualizar el `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
}
```
usamos 2 metodos, por que las sesiones son usadas para la API de navegador(y su log in/out)
Basic es para pasar el sessionID en als cabeceras para la API misma


**Implementar Token auth**

actualizar el `settings.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES':[
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication'
    ],
}
```
aun necesitamos el session para testing
necesitamos agregar la app:
```python
INSTALLED_APPS = [
		...
    'posts',
    'rest_framework',
    'rest_framework.authtoken',
]
```
hacer migraciones y correr el server, si vamos al admin y vemos en tokens no hay ninguno
estos solo se generan despues de un login(aunque antes hubiese usuarios!!!)

para los logins necesitamos crear endpoints 
podriamos crear una app users para esto y agregar sus urls,views y serializers, pero aqui no queremos errores, para esto ya hay librerias
como django-rest-auth combinada con django-allauth

```
pip install django-rest-auth
```
```python
INSTALLED_APPS = [
		...
    'posts',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
]
```
actualizamos el `blog_project/urls.py` con el paquete rest_auth, sus urls las pondremos en `api/v1/rest_auth`, agregando:
```python
    path('api/v1/rest-auth/',include('rest_auth.urls'))
```
y con esto ya tenemos nuevos endpoints para login
```
http://127.0.0.1:8000/api/v1/rest-auth/login/
http://127.0.0.1:8000/api/v1/rest-auth/logout/
http://127.0.0.1:8000/api/v1/rest-auth/password/reset
http://127.0.0.1:8000/api/v1/rest-auth/password/reset/confirm/
```
ahora implementaremos el registro de usuarios (signup)
ni django ni djangoRSTFW lo traen por default lo cual puede ser riesgoso
usaremos django-allauth que tambien provee autenticacion via face twitter google ,etc
si agregamos rest_auth.registration de django-rest-auth tendremos endpoints de registro de usuario

```
 pip install django-allauth
```
 y editaremos el `settings.py` para agregar toda la configuracion necesaria:
```python
INSTALLED_APPS = [
		...
    'posts',
    'rest_framework',
    'rest_framework.authtoken',
    'rest_auth',
    #nuevas
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth.registration',
    
]
...

EMAIL_BACKEND='django.core.mail.backends.console.EmailBackend'
SITE_ID=1

```
es necesario configurar el email para que el usuario confirme su nueva cuenta

pero creo que solo los desplegaremos :/

checar pagina 122,140,152, en django for beginners muestra como mandar correos

Site_id es parte de django, nos permite tener multiples webs en el mismo proyecto, aqui solo tendremos uno que trabaja con allauth

migramos y agregamos nuevas urls en `blog_project/urls.py`:
```python
  path('api/v1/rest-auth/registration',include('rest_auth.registration.urls'))
```
corremos el servidor y abrimos
```
http://127.0.0.1:8000/api/v1/rest-auth/registration/
```
si registramos un usuario nos manda por consola un mensaje de registro y en pantalla muestra el nuevo token, desde la consola de admins ya hay tokens

una vez logeados con el neuvo usuario nos devuelve el token
este debe ser manejado y almacenado como cookie o en local

ya lo logea despues de mandar el correo...pero no verifica el correo, hay que checar en allauth como hacerlo, sospecho que debe de ser desde el email enn el mundo real :/

para el paso de urls a path :

https://consideratecode.com/2018/05/02/django-2-0-url-to-path-cheatsheet/

https://django.cowhite.com/blog/working-with-url-get-post-parameters-in-django/

literal para ahcer la autenticacion y el logeo solo editamos el settings y el views :O!
### viewsets y routing

un viewset remplasa muchas vistas relacionadas

user endpoints:

ya tenemos un modelo de usuarios
solo lo enlazaremos con endpoints:
+ agregar el serializer al modelo de clases
+ nuevas vistas por cada endpoint
+ nuevas rutas de urls por cada endpoint

agregar a `posts/serializers.py`:

```python
from django.contrib.auth import get_user_model

class UserSerializer(serializers.ModelSerializer):

	class Meta:
		model=get_user_model()
		fields=('id','username')
```
crearemos una clase UserList qe despliega todos y UserDetails que solo muestra uno
por lo cual solo usaremos ListAPIView y RetrieveAPIView
 en `posts/views.py`:
 ```python
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

class UserList(generics.ListAPIView):
	queryset=get_user_model().objects.all()
	serializer_class=UserSerializer

class UserDetail(generics.RetrieveAPIView):
	queryset=get_user_model().objects.all()
	serializer_class=UserSerializer

```

en el `posts/urls.py` importaremos nuestras nuevas clases:
```python
from django.urls import path
from .views import UserList,UserDetail,PostList, PostDetail

urlpatterns=[
	path('users/',UserList.as_view()),
	path('users/<int:pk>/',UserDetail.as_view()),
	path('',PostList.as_view()),
	path('<int:pk>/',PostDetail.as_view()),
]
```
viewsets:
combina la logica de multiples clases en una sola clase
problemas:se pierde legibilidad para developers que no los manejan

editamos `el posts/views.py`:
```python
from django.contrib.auth import get_user_model
from rest_framework import viewsets

from .models import Post
from .permissions import IsAuthorOrReadOnly
from .serializers import PostSerializer,UserSerializer

class PostViewSet(viewsets.ModelViewSet):
	permission_classes = (IsAuthorOrReadOnly,)
	queryset=Post.objects.all()
	serializer_class=PostSerializer

class UserViewSet(viewsets.ModelViewSet):
	permission_classes = (IsAuthorOrReadOnly,)
	queryset=get_user_model().objects.all()
	serializer_class=UserSerializer
```
asi no repetimos vistas como arriba :D
**Routers***
sirven para condensar tambien las urls asi como los viewsets
DRF posee 2:SimpleRouter y DefaultRouter
usaremos el simple pero es posible crear routers customizados 
en `posts/urls.py`reescribimos casi todo:

```python
from django.urls import path
from .views import UserViewSet,PostViewSet
from rest_framework.routers import SimpleRouter

router=SimpleRouter()
router.register('users',UserViewSet,base_name='users')
router.register('',PostViewSet,base_name='posts')
urlpatterns=router.urls
```
aqui registramos cada viewset al router
usar viewsts y routers cuando la app crezca


http://127.0.0.1:8000/api/v1/rest-auth/registration/account-confirm-email/Mw:1hBohc:TMS_GlbCDSATrHd5pwGrZC9_s9o/


para que solo el mismo usuario edite su nombre yo agregue a permissions
```python
class IsUserOrReadOnly(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.method in permissions.SAFE_METHODS:
			return True
		print(obj)
		return obj == request.user
```
y a `post/views.py`:
```python
class UserViewSet(viewsets.ModelViewSet):
	permission_classes = (IsUserOrReadOnly,)
	queryset=get_user_model().objects.all()
	serializer_class=UserSerializer
```

## Docs
un schema es un documento legible por la maquina que lista los endpoints
la documentacion es texto agegado a el schema para los humanos

usaremos CoreAPI para generar el schema, es independiente del formato 
```python
pip install coreapi pyyaml
```
y agregamos a `blog_project/urls.py`

```python
...
from rest_framework.schemas import get_schema_view
from rest_framework.documentation import include_docs_urls
API_TITLE="Blog API"
API_DESCRIPTION='A web API for create blogs'
schema_view=get_schema_view(title=API_TITLE)

urlpatterns = [
 		...
    path('schema/',schema_view),
    path('docs/',include_docs_urls(title='Blog API', description=API_DESCRIPTION)),
    ]
```
si corremos el server la url `localhost/schema`
ya nos muestra informacion, y al oprimir el boton interact se puede ver el resultado

tambien esta la libreria django-rest-swagger
```python
pip install django-rest-swagger
```
editamos el settings.py:
```python
INSTALLED_APPS = [
...
'rest_framework_swagger',
]
```
y editamos el `blog_project/urls.py`:
```python
...
from rest_framework_swagger.views import get_swagger_view

API_TITLE="Blog API"
API_DESCRIPTION='A web API for create blogs'
schema_view=get_swagger_view(title=API_TITLE)

urlpatterns = [
		...
    #path('schema/',schema_view),
    path('swagger-docs/',schema_view),
    path('docs/',include_docs_urls(title='Blog API', description=API_DESCRIPTION)),
]

```
y vemos en la vista `localhost/swagger-docs/` la nueva documentacion













