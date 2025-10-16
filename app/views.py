from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .serializers import ContactSerializer
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.utils import timezone
from .models import Category, Tag, BlogPost
from .serializers import *
from rest_framework import generics, permissions

class ContactAPIView(APIView):
    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()

            # 1️⃣ Send email to your team
            team_html = render_to_string('emails/team_email.html', {
                'fullname': contact.fullname,
                'mobile': contact.mobile,
                'email': contact.email,
                'subject': contact.subject,
                'message': contact.message,
            })
            team_email = EmailMessage(
                subject=f"New Contact: {contact.subject}",
                body=team_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
            )
            team_email.content_subtype = "html"  # Important: set content type to HTML
            team_email.send(fail_silently=False)

            # 2️⃣ Send confirmation email to the user
            user_html = render_to_string('emails/user_email.html', {
                'fullname': contact.fullname,
                'message': contact.message,
            })
            user_email = EmailMessage(
                subject="Thank you for contacting us!",
                body=user_html,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[contact.email],
            )
            user_email.content_subtype = "html"
            user_email.send(fail_silently=False)

            return Response({"message": "Contact submitted successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 100

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.annotate(post_count=Count('posts'))
    serializer_class = CategorySerializer
    lookup_field = 'slug'

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.annotate(post_count=Count('posts'))
    serializer_class = TagSerializer
    lookup_field = 'slug'

class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlogPostListSerializer
    pagination_class = StandardResultsSetPagination
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('category', 'author').prefetch_related('tags')
        
        # Filter by category
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag
        tag_slug = self.request.query_params.get('tag', None)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(excerpt__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__name__icontains=search)
            ).distinct()
        
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BlogPostDetailSerializer
        return BlogPostListSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.views += 1
        instance.save(update_fields=['views'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

# Function-based views for additional endpoints
@api_view(['GET'])
def featured_posts(request):
    """Get featured blog posts"""
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True,
        published_at__lte=timezone.now()
    )[:2]
    serializer = BlogPostListSerializer(featured_posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def categories_with_counts(request):
    """Get categories with post counts"""
    categories = Category.objects.annotate(
        post_count=Count('posts', filter=Q(posts__status='published'))
    )
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

# Job postings list for careers page
class JobRequirementListView(generics.ListAPIView):
    queryset = JobRequirement.objects.filter(is_active=True).order_by("-posted_on")
    serializer_class = JobRequirementSerializer
    permission_classes = [permissions.AllowAny]


# Job posting detail view
class JobRequirementDetailView(generics.RetrieveAPIView):
    queryset = JobRequirement.objects.filter(is_active=True)
    serializer_class = JobRequirementSerializer
    permission_classes = [permissions.AllowAny]


class JobApplicationCreateView(generics.CreateAPIView):
    queryset = JobApplication.objects.all()
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Save application
        application = serializer.save()

        # ✅ Send thank-you email to applicant
        try:
            html_message = render_to_string("emails/job_application_user.html", {
                "full_name": application.full_name,
                "job_title": application.job.title,
            })

            email = EmailMessage(
                subject=f"Thank You for Applying to {application.job.title}!",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[application.email],
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)

        except Exception as e:
            print(f"Error sending applicant email: {e}")


class OpenApplicationCreateView(generics.CreateAPIView):
    queryset = OpenApplication.objects.all()
    serializer_class = OpenApplicationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Save the open application
        application = serializer.save()

        # ✅ Send thank-you email to the applicant
        try:
            html_message = render_to_string("emails/open_application_user.html", {
                "full_name": application.full_name,
                "desired_position": application.desired_position or "the position you applied for",
            })

            email = EmailMessage(
                subject="Thank You for Your Application!",
                body=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[application.email],
            )
            email.content_subtype = "html"
            email.send(fail_silently=False)

        except Exception as e:
            print(f"Error sending applicant email: {e}")