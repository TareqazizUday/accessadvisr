from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Blog, BlogComment, BlogCommentReply


@method_decorator(csrf_exempt, name='dispatch')
class SubmitBlogCommentView(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]
    """API endpoint to submit a comment on a blog post"""
    
    def post(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required. Please login to submit a comment.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            # DRF automatically parses JSON when JSONParser is used
            data = request.data if hasattr(request, 'data') else {}
            
            blog_id = data.get('blog_id')
            author_name = data.get('author_name', '').strip()
            author_email = data.get('author_email', '').strip()
            comment_text = data.get('comment_text', '').strip()
            save_info = data.get('save_info', False)
            
            if not blog_id:
                return Response(
                    {'error': 'Blog ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not comment_text:
                return Response(
                    {'error': 'Comment text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                blog = Blog.objects.get(id=blog_id, status='published')
            except Blog.DoesNotExist:
                return Response(
                    {'error': 'Blog not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Create comment (auto-approved)
            comment = BlogComment.objects.create(
                blog=blog,
                author_name=author_name,
                author_email=author_email,
                comment_text=comment_text,
                save_info=save_info,
                is_approved=True,  # Auto-approved
                is_active=True
            )
            
            return Response({
                'success': True,
                'message': 'Comment submitted successfully!',
                'comment_id': comment.id
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class SubmitBlogCommentReplyView(APIView):
    parser_classes = [JSONParser]
    permission_classes = [IsAuthenticated]
    """API endpoint to submit a reply to a blog comment"""
    
    def post(self, request):
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required. Please login to submit a reply.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        try:
            # DRF automatically parses JSON when JSONParser is used
            data = request.data if hasattr(request, 'data') else {}
            
            comment_id = data.get('comment_id')
            parent_reply_id = data.get('parent_reply_id')
            author_name = data.get('author_name', '').strip()
            author_email = data.get('author_email', '').strip()
            reply_text = data.get('reply_text', '').strip()
            
            if not comment_id:
                return Response(
                    {'error': 'Comment ID is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_name:
                return Response(
                    {'error': 'Name is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not author_email:
                return Response(
                    {'error': 'Email is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not reply_text:
                return Response(
                    {'error': 'Reply text is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                comment = BlogComment.objects.get(id=comment_id, is_active=True)
            except BlogComment.DoesNotExist:
                return Response(
                    {'error': 'Comment not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            parent_reply = None
            if parent_reply_id:
                try:
                    parent_reply = BlogCommentReply.objects.get(id=parent_reply_id, is_active=True, comment=comment)
                except BlogCommentReply.DoesNotExist:
                    return Response(
                        {'error': 'Parent reply not found'},
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            reply = BlogCommentReply.objects.create(
                comment=comment,
                parent_reply=parent_reply,
                author_name=author_name,
                author_email=author_email,
                reply_text=reply_text,
                is_approved=True,  # Auto-approve replies so they show immediately
                is_active=True
            )
            
            return Response({
                'success': True,
                'message': 'Reply submitted successfully!',
                'reply_id': reply.id
            }, status=status.HTTP_201_CREATED)
            
        except json.JSONDecodeError:
            return Response(
                {'error': 'Invalid JSON data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

