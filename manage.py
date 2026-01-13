#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Fix for Python 3.14 compatibility with Django 4.2.7
def _patch_django_context():
    """Patch Django's Context.__copy__ for Python 3.14 compatibility"""
    import sys as sys_module
    if sys_module.version_info >= (3, 14):
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

# Apply patch before Django imports
_patch_django_context()

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapsearch.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    
    # Re-apply patch after Django is imported
    _patch_django_context()
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
