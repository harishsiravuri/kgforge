import logging
import os
from typing import List

import transformers
from transformers import pipeline

from kgforge.config import KGConfig
from kgforge.data_models import Prompt, PromptResponse, ResearchArtifact

logger = logging.getLogger(__name__)


class KnowledgeGraphConfig:
    """Configuration for KnowledgeGraph

    Attributes:
        email (str): Email address of the user.
        prompts (List[str]): List of prompts to be used in the construction of the KG.
        model_name (str): Name of the model to be used for answering questions.
    """

    def __init__(
        self,
        email: str = None,
        prompts: List[Prompt] = None,
        model_name: str = "deepset/roberta-base-squad2",
    ) -> None:
        """Initializes KnowledgeGraphConfig

        Usage example:
        >>>config = KnowledgeGraphConfig()
        >>>config.email = "sample-email"
        >>>config.prompts = [Prompt(concept="author", question="Who is the author of this text?")]
        >>>config.model_name = "deepset/roberta-base-squad2"

        Args:
            email (str): Email address of the user.
            prompts (List[Prompt]): List of prompts to be used in the construction of the KG.

        Returns:
            None: Initializes KnowledgeGraphConfig
        """
        if prompts is None:
            self.prompts = KGConfig.DEFAULT_PROMPTS
        else:
            self.prompts = prompts
        self.email = email or os.environ.get("OPEN_ALEX_EMAIL", None)
        self.model_name = model_name


class KnowledgeGraph:
    """Knowledge graph built using Documents"""

    artifacts: List[ResearchArtifact] = []

    def __init__(
        self,
        config: KnowledgeGraphConfig = None,
        artifacts: List[ResearchArtifact] = None,
    ):
        self.config = config or KnowledgeGraphConfig()
        self.artifacts = artifacts

    def clear_prompts(self) -> None:
        """Clears the list of prompts used in the construction of this KG

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.clear_prompts()

        Args:

        Returns:
            None

        Raises:
            None
        """
        self.config.prompts = None

    def update_prompts(self, new_prompts: List[Prompt]) -> None:
        """Appends new prompts to existing prompts

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.update_prompts([Prompt(concept="author", question="Who is the author of this text?")]

        Args:
            new_prompts (List[Prompt]): New prompts to be appended to existint prompts

        Returns:
            None: Appends prompts to existing prompts

        Raises:
            None
        """
        if self.config.prompts is None:
            self.config.prompts = new_prompts
        elif len(new_prompts) > 0:
            self.config.prompts.extend(new_prompts)

    def answer_question(
        self, artifact: ResearchArtifact, prompt: Prompt
    ) -> PromptResponse:
        """Answers questions based on context.

        Usage example:
        >>>artifacts = ResearchArtifact()
        >>>kg = KnowledgeGraph()
        >>>kg.answer_question(artifact, Prompt(concept="author", question="Who is the author of this text?"))

        Args:
            artifact (ResearchArtifact): Artifact to be used for answering the question.
            prompt (Prompt): Question to be answered.

        Returns:
            PromptResponse: Answer to the question.

        Raises:
            ValueError: If no text is found in the question.
        """
        if artifact is None:
            logger.info("Artifact is needed to answer the question.")
            return PromptResponse(concept=prompt.concept, prompt_response="Unavailable")
        if artifact.full_text is None:
            logger.info("Full text not found.")
            return PromptResponse(concept=prompt.concept, prompt_response="Unavailable")
        if prompt.question == "":
            raise ValueError("Question cannot be empty")
        try:
            nlp = pipeline(task="question-answering", model=self.config.model_name)
            res = nlp(question=prompt.question, context=artifact.full_text)
            return PromptResponse(concept=prompt.concept, prompt_response=res)
        except transformers.pipelines.base.PipelineException:
            logger.error("Error while answering question")
            return PromptResponse(concept=prompt.concept, prompt_response="Unavailable")

    def construct_kg(self):
        """Constructs knowledge graph using the list of documents

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.construct_kg()

        Args:

        Returns:
            None: Builds a knowledge graph

        Raises:
            ValueError: If no text is found in the document or the question.
        """

        if self.artifacts is None:
            raise ValueError("Artifacts are needed to construct the knowledge graph.")

        processed_artifacts = []
        for artifact in self.artifacts:
            res = []
            for prompt in self.config.prompts:
                res.append(self.answer_question(artifact=artifact, prompt=prompt))
            processed_artifacts.append(res)

        logger.info(processed_artifacts)
        return processed_artifacts
