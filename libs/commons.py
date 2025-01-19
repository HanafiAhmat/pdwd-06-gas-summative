import docx
import markdown
import PyPDF2
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

def send_email(recipient_email, email_subject, email_body):
    fromEmail = settings.DEFAULT_FROM_EMAIL
    msg = EmailMultiAlternatives(email_subject, email_body['text'], fromEmail, [recipient_email])
    if email_body['html'] is not None:
        msg.attach_alternative(email_body['html'], "text/html")

    result = '';
    try:
        result = msg.send()
    except Exception as e:
        result = str(e)

    return result

def build_pagination_data(request, totalRecords, limit, pageUrl):
    pageNum = request.GET.get('page', 1)
    pageNum = int(pageNum)
    stop = pageNum * limit
    start = stop - limit

    pages = round(totalRecords / limit)
    if (pages > 5):
        if (pageNum < 4):
            pagesRange = range(1, 6)
        elif (pageNum > 3):
            if (pageNum < pages - 2):
                pagesRange = range(pageNum - 2, pageNum + 3)
            else:
                pagesRange = range(pageNum - 2, pages + 1)
    else:
        pagesRange = range(1, pages + 1);

    pagination = {
        'totalRecords': totalRecords,
        'pages': pages,
        'pagesList': pagesRange,
        'currentPage': pageNum,
        'previousPage': pageNum - 1,
        'nextPage': pageNum + 1,
        'showGoBack': True if pageNum != 1 else False,
        'showGoFirst': True if pageNum > 3 else False,
        'showGoNext': True if pageNum != pages else False,
        'showGoLast': True if pageNum + 2 < pages else False,
        'pageUrl': pageUrl,
        'start': start + 1,
        'stop': stop,
    }

    return pagination

def convert_markdown_to_html(markdown_text):
    """Convert Markdown text to HTML."""
    html = markdown.markdown(markdown_text)
    return html

def strip_markdown(markdown_text):
    html = markdown_text.replace('```html','').replace('```','')
    return html

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text
