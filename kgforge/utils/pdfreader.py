import io
import logging
from typing import List

import requests
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

logger = logging.getLogger(__name__)


class TextLoader:
    """Reads text from a variety of sources."""

    @staticmethod
    def _read_pdf(path: str) -> List[str]:
        """Reads text from a PDF file.

        Usage example:
        >>> loader = TextLoader()
        >>> loader._read_pdf("path/to/file.pdf")

        Args:
            path (str): Path to the PDF file.

        Returns:
            List[str]: List of strings, each string representing a column in the PDF.

        Raises:
            FileNotFoundError: If the file does not exist.
            Exception: If an error occurs while reading the PDF.
        """
        try:
            resource_manager = PDFResourceManager()
            file_handle = io.StringIO()
            converter = TextConverter(
                resource_manager, file_handle, laparams=LAParams()
            )
            page_interpreter = PDFPageInterpreter(resource_manager, converter)

            with open(path, "rb") as file:
                for page in PDFPage.get_pages(
                    file, caching=True, check_extractable=True
                ):
                    page_interpreter.process_page(page)
                text = file_handle.getvalue()

            if text.find("\n\n") == -1:
                logger.info("Single column PDF detected.")
                columns = [text]
            else:
                logger.info("Multi column PDF detected.")
                columns = text.split("\n\n")

            converter.close()
            file_handle.close()

            return columns
        except FileNotFoundError:
            logger.error("File not found.")
            raise FileNotFoundError
        except Exception as e:
            logger.error("Error occurred while reading PDF. " + str(e))
            raise e

    @staticmethod
    def read_pdf_from_url(url: str = None) -> List[str]:
        """Reads PDF file from an online URL.

        Usage example:
        >>> loader = TextLoader()
        >>> loader.read_pdf_from_url("https://arxiv.org/pdf/2106.01558.pdf")

        Args:
            url (str): URL of the PDF file.

        Returns:
            List[str]: Text from the PDF file.

        Raises:
            ValueError: If no URL is provided.
        """

        if url is None:
            raise ValueError("URL cannot be empty")
        try:
            response = requests.get(url)
            resource_manager = PDFResourceManager()
            file_handle = io.StringIO()
            converter = TextConverter(
                resource_manager, file_handle, laparams=LAParams()
            )
            page_interpreter = PDFPageInterpreter(resource_manager, converter)

            for page in PDFPage.get_pages(
                io.BytesIO(response.content), caching=True, check_extractable=True
            ):
                page_interpreter.process_page(page)
            text = file_handle.getvalue()

            if text.find("\n\n") == -1:
                logger.info("Single column PDF detected.")
                columns = [text]
            else:
                logger.info("Multi column PDF detected.")
                columns = text.split("\n\n")

            converter.close()
            file_handle.close()

            return columns

        except Exception as e:
            logger.error("Error occurred while reading PDF. " + str(e))
            return None
