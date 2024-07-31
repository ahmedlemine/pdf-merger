import os
import uuid

from pypdf import PdfWriter
from pypdf.errors import PdfReadError, PyPdfError
from django.conf import settings

from .exceptions import MergeException

merger = PdfWriter()


def merge_pdf_files(pdf_files):
    """
    merges a list of pdf files using pypdf and returns the path
    for the merged PDF file.
    :param list pdf_files: a list of PDF files to merge.
    """

    with merger:
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
        except (FileNotFoundError, PdfReadError, PyPdfError):
            raise MergeException

    if os.path.isfile(merged_path):
        return merged_path
    return None
