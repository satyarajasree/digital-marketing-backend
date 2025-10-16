from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'posts', BlogPostViewSet, basename='post')

urlpatterns = [
    path('api/contact/', ContactAPIView.as_view(), name='contact-api'),
    path('api/blog/', include(router.urls)),
    path('api/blog/featured-posts/', featured_posts, name='featured-posts'),
    path('api/blog/categories-with-counts/', categories_with_counts, name='categories-with-counts'),

    # Job listing & detail
    path("api/jobs/", JobRequirementListView.as_view(), name="job-list"),
    path("api/jobs/<int:pk>/", JobRequirementDetailView.as_view(), name="job-detail"),

    # Apply for specific job
    path("api/apply/", JobApplicationCreateView.as_view(), name="job-apply"),

    # Open (general) application
    path("api/open-application/", OpenApplicationCreateView.as_view(), name="open-application"),
]
