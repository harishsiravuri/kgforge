from kgforge.documents import Document
from typing import List


class KnowledgeGraph:
    """Knowledge graph built using Documents
    """

    documents: List[Document]
    knowledge_graph = ""
    prompts: List[str] = []

    def clear_prompts(self) -> None:
        """Clears the list of prompts used in the construction of this KG

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.clear_prompts()

        Args:
            None

        Returns:
            None

        Raises:
            None
        """
        self.prompts = []

    def update_prompts(self, new_prompts: List[str]) -> None:
        """Appends new prompts to existing prompts

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.update_prompts(["Who is the author of this text?"])

        Args:
            new_prompts (List[str]): New prompts to be appended to existint prompts

        Returns:
            None: Appends prompts to existing prompts

        Raises:
            None
        """
        if len(new_prompts) > 0:
            self.prompts.append(new_prompts)

    def construct_kg(self):
        """Constructs knowledge graph using the list of documents

        Usage example:
        >>>doc = Document()
        >>>doc.full_text = "sample-text"
        >>>doc.answer_question("text")

        Args:

        Returns:
            None: Builds a knowledge graph

        Raises:
            ValueError: If no text is found in the document or the question.
        """

        for doc in self.documents:
            res = []
            for prompt in self.prompts:
                res.append(doc.answer_question(question=prompt))
