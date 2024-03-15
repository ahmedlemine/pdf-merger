import os
import uuid
from PyPDF2 import PdfMerger
from PyPDF2.errors import PdfReadError, PyPdfError
from django.conf import settings

from .exceptions import MergeException


def merge_pdf_files(pdf_files):
    ''' merge a list of pdf files using PyPDF2 and returns the path
        for the merged PDF file.
    '''
    merger = PdfMerger()
    for f in pdf_files:
        try:
            merger.append(f.file)
        except FileNotFoundError:
            raise MergeException

    merged_path = os.path.join(
        settings.MEDIA_ROOT, f"merged_pdfs/merged_pdf_{uuid.uuid4()}.pdf"
    )

    try:
        merger.write(merged_path)
    except FileNotFoundError:
        raise MergeException
    except PdfReadError:
        raise MergeException
    except PyPdfError:
        raise MergeException

    merger.close()

    if os.path.isfile(merged_path):
        return merged_path
    return None
