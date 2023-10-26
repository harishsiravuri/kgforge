from typing import List

from kgforge.data_models import Prompt


class KGConfig:
    """A configuration object."""

    DEFAULT_PROMPTS: List[Prompt] = [
        Prompt(concept="author", question="Who is the author of this text?"),
        Prompt(concept="title", question="What is the title of this text?"),
        Prompt(concept="year", question="What year was this text published?"),
    ]
