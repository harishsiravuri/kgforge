import io
import logging
from typing import List

import transformers
from transformers import pipeline

logger = logging.getLogger(__name__)


class Document:
    """Research Paper

    Attributes:
        title (str): Title of the research paper.
        authors (List[str]): List of authors of the research paper.
        full_text (str): Full text of the research paper.
        model_name (str): Name of the model to be used for answering questions.

    """

    title: str = ""
    authors: List[str] = []
    full_text: str = ""
    model_name: str = "deepset/roberta-base-squad2"

    def __init__(self):
        pass

    def answer_question(self, question: str) -> str:
        """Answers questions based on context.

        Usage example:
        >>>doc = Document()
        >>>doc.full_text = "sample-text"
        >>>doc.answer_question("text")

        Args:
            question (str): Question to be answered.

        Returns:
            str: Answer to the question.

        Raises:
            ValueError: If no text is found in the document or the question.
        """
        if self.full_text == "":
            raise ValueError("No text found in document")
        if question == "":
            raise ValueError("Question cannot be empty")
        try:
            nlp = pipeline(task="question-answering", model=self.model_name)
            res = nlp(question=question, context=self.full_text)
            return res
        except transformers.pipelines.base.PipelineException:
            logger.error("Error while answering question")
            return ""
