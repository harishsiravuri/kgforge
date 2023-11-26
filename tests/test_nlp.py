import logging
import os

from kgforge.config import KGConfig
from kgforge.data_models import ResearchArtifact
from kgforge.kg import KnowledgeGraph
from kgforge.utils import OpenAlexUtil, TextLoader


logger = logging.getLogger(__name__)


def test_prompt_responses() -> None:
    oa_util = OpenAlexUtil()
    oa_resp = oa_util.search_works(search_query="machine+learning", results_limit=1)
    artifacts = [ResearchArtifact.model_validate(_) for _ in oa_resp]
    [_.get_full_text() for _ in artifacts]
    kg = KnowledgeGraph(artifacts=artifacts)

    prompts = KGConfig.DEFAULT_PROMPTS
    logger.info("Number of prompts: " + str(len(prompts)))
    for artifact in artifacts:
        for prompt in prompts:
            print("\n================")
            print("Concept: " + str(prompt.concept))
            print("Prompt: " + str(prompt.question))
            response = kg.answer_question(artifact=artifact, prompt=prompt)
            print("Response: " + str(response.prompt_response))
            print("================\n")

    assert True
