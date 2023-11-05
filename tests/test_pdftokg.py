import os

from kgforge.config import KGConfig
from kgforge.data_models import ResearchArtifact
from kgforge.kg import KnowledgeGraph
from kgforge.utils import OpenAlexUtil, TextLoader


def test_get_full_text() -> None:
    oa_util = OpenAlexUtil()
    oa_resp = oa_util.search_works(search_query="machine+learning", results_limit=1)
    artifacts = [ResearchArtifact.model_validate(_) for _ in oa_resp]
    artifacts[0].get_full_text()
    assert len(artifacts[0].full_text) > 0


def test_answer_question() -> None:
    oa_util = OpenAlexUtil()
    oa_resp = oa_util.search_works(search_query="machine+learning", results_limit=10)
    artifacts = [ResearchArtifact.model_validate(_) for _ in oa_resp]
    [_.get_full_text() for _ in artifacts]
    assert len(artifacts) > 0

    kg = KnowledgeGraph(artifacts=artifacts)
    kg.clear_prompts()
    assert kg.config.prompts is None

    new_prompts = KGConfig.DEFAULT_PROMPTS
    assert new_prompts is not None

    kg.update_prompts(new_prompts=new_prompts)
    assert kg.config.prompts is not None

    kg.construct_kg()
    kg.visualize_kg("tests/test_data/test_graph.png")
    os.remove("tests/test_data/test_graph.png")


def test_kg() -> None:
    oa_util = OpenAlexUtil()
    oa_resp = oa_util.search_works(search_query="machine+learning", results_limit=10)
    artifacts = [ResearchArtifact.model_validate(_) for _ in oa_resp]
    [_.get_full_text() for _ in artifacts]
    kg = KnowledgeGraph(artifacts=artifacts)
    kg.construct_kg()
    kg.visualize_kg("tests/test_data/test_graph.png")
    os.remove("tests/test_data/test_graph.png")
    assert True


def test_read_pdf() -> None:
    sample_obj = TextLoader()
    path = "tests/test_data/example.pdf"
    resp = sample_obj._read_pdf(path=path)
    assert len(resp) > 0
