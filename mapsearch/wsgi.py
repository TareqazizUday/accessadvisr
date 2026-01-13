"""
WSGI config for mapsearch project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys

# Fix for Python 3.14 compatibility with Django 4.2.7
def _patch_django_context():
    """Patch Django's Context.__copy__ for Python 3.14 compatibility"""
    if sys.version_info >= (3, 14):
        try:
            import django.template.context
            _original_copy = getattr(django.template.context.Context, '__copy__', None)
            if _original_copy and not hasattr(_original_copy, '_patched'):
                def _patched_copy(self):
                    try:
                        return _original_copy(self)
                    except AttributeError:
                        # Fallback for Python 3.14
                        from django.template.context import Context
                        new_context = Context()
                        if hasattr(self, 'dicts'):
                            new_context.dicts = list(self.dicts) if self.dicts else []
                        if hasattr(self, 'autoescape'):
                            new_context.autoescape = self.autoescape
                        if hasattr(self, 'render_context'):
                            new_context.render_context = self.render_context
                        return new_context
                _patched_copy._patched = True
                django.template.context.Context.__copy__ = _patched_copy
        except:
            pass

_patch_django_context()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapsearch.settings')

application = get_wsgi_application()

# Re-apply patch after Django is loaded
_patch_django_context()
