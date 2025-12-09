"""
Utility functions for lessons app.
"""
from io import BytesIO
from django.template.loader import render_to_string


def stringify_items(items):
    """
    Convert list items to strings, handling both strings and dicts.
    
    Args:
        items: List of items (strings or dicts)
        
    Returns:
        List of strings
    """
    result = []
    for item in items:
        if isinstance(item, dict):
            # If it's a dict, try to get a meaningful string representation
            if 'text' in item:
                result.append(str(item['text']))
            elif 'title' in item:
                result.append(str(item['title']))
            elif 'name' in item:
                result.append(str(item['name']))
            else:
                result.append(str(item))
        else:
            result.append(str(item))
    return result


def generate_lesson_pdf(lesson):
    """
    Generate a PDF from a Lesson instance.
    
    Args:
        lesson: Lesson model instance
        
    Returns:
        BytesIO object containing the PDF data
        
    Raises:
        ImportError: If WeasyPrint or its dependencies are not installed
        OSError: If WeasyPrint system dependencies are missing
    """
    # Lazy import to avoid startup errors if dependencies aren't installed
    try:
        from weasyprint import HTML
        from weasyprint.text.fonts import FontConfiguration
    except ImportError as e:
        raise ImportError(
            "WeasyPrint is not installed. Install it with: pip install WeasyPrint"
        ) from e
    except OSError as e:
        raise OSError(
            "WeasyPrint system dependencies are missing. "
            "On macOS, install with: brew install cairo pango gdk-pixbuf libffi gobject-introspection"
        ) from e
    
    # Prepare context for template
    context = {
        'lesson': lesson,
        'activities': stringify_items(lesson.get_activities_list()),
        'questions': stringify_items(lesson.get_questions_list()),
        'image_urls': lesson.get_image_urls_list(),
        'video_links': lesson.get_video_links_list(),
    }
    
    # Render HTML template
    html_string = render_to_string('lessons/lesson_pdf.html', context)
    
    # Generate PDF
    font_config = FontConfiguration()
    pdf_file = HTML(string=html_string).write_pdf(font_config=font_config)
    
    # Return as BytesIO
    return BytesIO(pdf_file)

