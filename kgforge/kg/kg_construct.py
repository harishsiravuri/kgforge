import errno
import logging
import os
from typing import List

import matplotlib.pyplot as plt
import networkx as nx
import transformers
from transformers import pipeline
import pickle
import json

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
        self.graph = nx.DiGraph()

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
            return PromptResponse(
                concept=prompt.concept, score=0, prompt_response="Unavailable"
            )
        if artifact.full_text is None:
            logger.info("Full text not found.")
            return PromptResponse(
                concept=prompt.concept, score=0, prompt_response="Unavailable"
            )
        if prompt.question == "":
            raise ValueError("Question cannot be empty")
        try:
            nlp = pipeline(task="question-answering", model=self.config.model_name)
            res = nlp(question=prompt.question, context=artifact.full_text)
            return PromptResponse(
                concept=prompt.concept,
                score=res.get("score", 0),
                prompt_response=res.get("answer", "Unavailable"),
            )
        except transformers.pipelines.base.PipelineException:
            logger.error("Error while answering question")
            return PromptResponse(
                concept=prompt.concept, score=0, prompt_response="Unavailable"
            )

    def construct_kg(self) -> None:
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
            logger.info("Artifacts are needed to construct the knowledge graph.")

        try:
            processed_artifacts = []
            for artifact in self.artifacts:
                self.graph.add_node(artifact.artifact_id)
                res = []
                for prompt in self.config.prompts:
                    prompt_res = self.answer_question(artifact=artifact, prompt=prompt)
                    res.append(prompt_res)
                    self.graph.add_node(prompt_res.prompt_response)
                    if prompt in ["contribution", "findings"]:
                        self.graph.add_edge(
                            artifact.artifact_id, prompt_res.prompt_response
                        )
                    else:
                        self.graph.add_edge(
                            prompt_res.prompt_response, artifact.artifact_id
                        )
                processed_artifacts.append(res)

            logger.info("Knowledge Graph constructed successfully.")
        except Exception as e:
            logger.info("Error while constructing the knowledge graph: " + str(e))

    def read_graph(self, path: str) -> None:
        """Reads the graph from a file

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.read_graph("kg.pickle")

        Args:
            path (str): Path to the file where the graph is to be read from

        Returns:
            None: Reads the graph from a file

        Raises:
            ValueError: If the path is empty
            FileNotFoundError: If the file is not found
        """
        if path is None:
            raise ValueError("Path cannot be empty")
        else:
            if not os.path.isfile(path):
                raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)
            else:
                with open(path, "rb") as f:
                    self.graph = pickle.load(f)

    def write_graph(self, path: str) -> None:
        """Writes the graph to a file

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.write_graph("kg.pickle")

        Args:
            path (str): Path to the file where the graph is to be written

        Returns:
            None: Writes the graph to a file

        Raises:
            ValueError: If the path is empty
        """
        try:
            node_arr = []
            edge_arr = []

            for node in list(self.graph.nodes(data=True)):
                node_arr.append(node)

            for edge in list(self.graph.edges()):
                edge_arr.append(edge)

            graph_dict = {"nodes": node_arr, "edges": edge_arr}
            with open(path, "w") as f:
                json.dump(graph_dict, f, indent=4)
        except:
            pass
        # if path is not None and self.graph is not None:
        #     with open(path, "wb") as f:
        #         pickle.dump(self.graph, f)
        # else:
        #     raise ValueError("Path cannot be empty")

    def visualize_kg(self, file_path: str = "graph.png"):
        """Visualizes the knowledge graph

        Usage example:
        >>>kg = KnowledgeGraph()
        >>>kg.visualize_kg()

        Args:

        Returns:
            None: Visualizes the knowledge graph

        Raises:
            None
        """
        pos = nx.spring_layout(self.graph, k=0.7, iterations=50)
        nx.draw(self.graph, pos=pos, with_labels=False, font_weight="bold")
        ax = plt.gca()
        ax.set_aspect('equal')
        ax.set_axis_off()

        plt.savefig(file_path, format="PNG")
