from django.urls import path
from .views import UserViewSet,PostViewSet
from rest_framework.routers import SimpleRouter

router=SimpleRouter()
router.register('users',UserViewSet,base_name='users')
router.register('',PostViewSet,base_name='posts')
urlpatterns=router.urls

# from django.urls import path
# from .views import UserList,UserDetail,PostList, PostDetail

# urlpatterns=[
# 	path('users/',UserList.as_view()),
# 	path('users/<int:pk>/',UserDetail.as_view()),
# 	path('',PostList.as_view()),
# 	path('<int:pk>/',PostDetail.as_view()),
# ]