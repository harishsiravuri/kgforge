from typing import List

from kgforge.data_models import Prompt


class KGConfig:
    """A configuration object."""

    DEFAULT_CONCEPTS: List[str] = ["contribution", "methods", "datasets", "findings"]

    DEFAULT_PROMPTS: List[Prompt] = [
        Prompt(
            concept="contribution",
            question="What is the main contribution of this paper?",
        ),
        Prompt(concept="methods", question="What methods were used?"),
        Prompt(concept="datasets", question="What datasets were used?"),
        Prompt(concept="findings", question="What are the key findings?"),
    ]
