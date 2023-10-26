from kgforge.config import KGConfig
from kgforge.data_models import ResearchArtifact
from kgforge.kg import KnowledgeGraph
from kgforge.utils import OpenAlexUtil, TextLoader


def test_answer_question() -> None:
    oa_util = OpenAlexUtil()
    oa_resp = oa_util.search_works("digital+libraries")
    artifacts = [ResearchArtifact.model_validate(_) for _ in oa_resp]
    full_text_artifacts = list(map(lambda x: x.get_full_text(), artifacts))
    assert len(full_text_artifacts) > 0

    kg = KnowledgeGraph(artifacts=full_text_artifacts)
    kg.clear_prompts()
    assert kg.config.prompts is None

    new_prompts = KGConfig.DEFAULT_PROMPTS
    assert new_prompts is not None

    kg.update_prompts(new_prompts=new_prompts)
    assert kg.config.prompts is not None

    res = kg.construct_kg()
    assert res is not None


def test_read_pdf() -> None:
    sample_obj = TextLoader()
    path = "tests/test_data/example.pdf"
    resp = sample_obj._read_pdf(path=path)
    assert len(resp) > 0
