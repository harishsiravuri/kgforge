import logging
from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from kgforge.utils import TextLoader

logger = logging.getLogger(__name__)


class Prompt(BaseModel):
    """Prompt to be used in the construction of a KG.

    Attributes:
        concept (str): The concept/key that the answer to the prompt is classified as.
        question (str): The actual prompt/question to be used.
    """

    concept: str
    question: str


class PromptResponse(BaseModel):
    """Prompt to be used in the construction of a KG.

    Attributes:
        concept (str): The concept/key that the answer to the prompt is classified as.
        prompt_response (str): Response to the prompt/question used.
    """

    concept: str
    score: float
    prompt_response: str


class ArtifactID(BaseModel):
    openalex: Optional[str] = None
    doi: Optional[str] = None
    mag: Optional[str] = None


class ArtifactSource(BaseModel):
    source_id: Optional[str] = Field(alias="id", default=None)
    display_name: Optional[str] = None
    issn_l: Optional[str] = None
    issn: Optional[List[str]] = None
    is_oa: Optional[bool] = None
    is_in_doaj: Optional[bool] = None
    host_organization: Optional[str] = None
    host_organization_name: Optional[str] = None
    host_organization_lineage: Optional[List[str]] = None
    host_organization_lineage_names: Optional[List[str]] = None
    source_type: Optional[str] = Field(alias="type", default=None)


class ArtifactLocation(BaseModel):
    is_oa: Optional[bool] = None
    landing_page_url: Optional[str] = None
    pdf_url: Optional[str] = None
    source: Optional[ArtifactSource] = None
    license: Optional[str] = None
    version: Optional[str] = None
    is_accepted: Optional[bool] = None
    is_published: Optional[bool] = None


class OpenAccess(BaseModel):
    is_oa: Optional[bool] = None
    oa_status: Optional[str] = None
    oa_url: Optional[str] = None
    any_repository_has_fulltext: Optional[bool] = None


class Author(BaseModel):
    author_id: Optional[str] = Field(alias="id", default=None)
    display_name: Optional[str] = None
    orcid: Optional[str] = None


# class Institution(BaseModel):


class Authorship(BaseModel):
    author_position: Optional[str] = None
    author: Optional[Author] = None
    institutions: Optional[List[Any]] = None
    countries: Optional[List[str]] = None
    is_corresponding: Optional[bool] = None
    raw_author_name: Optional[str] = None
    raw_affiliation_string: Optional[str] = None
    raw_affiliation_strings: Optional[List[str]] = None


class APC(BaseModel):
    value: Optional[int] = None
    currency: Optional[str] = None
    value_usd: Optional[int] = None
    provenance: Optional[str] = None


class Biblio(BaseModel):
    volume: Optional[str] = None
    issue: Optional[str] = None
    first_page: Optional[str] = None
    last_page: Optional[str] = None


class Concept(BaseModel):
    concept_id: Optional[str] = Field(alias="id", default=None)
    wikidata: Optional[str] = None
    display_name: Optional[str] = None
    level: Optional[int] = None
    score: Optional[float] = None


class Goal(BaseModel):
    goal_id: Optional[str] = Field(alias="id", default=None)
    display_name: Optional[str] = None
    score: Optional[float] = None


class CountByYear(BaseModel):
    year: Optional[int] = None
    cited_by_count: Optional[int] = None


class ResearchArtifact(BaseModel):
    artifact_id: Optional[str] = Field(alias="id", default=None)
    title: Optional[str] = None
    display_name: Optional[str] = None
    publication_year: Optional[int] = None
    publication_date: Optional[date] = None
    ids: Optional[ArtifactID] = None
    language: Optional[str] = None
    primary_location: Optional[ArtifactLocation] = None
    artifact_type: Optional[str] = Field(alias="type", default=None)
    type_crossref: Optional[str] = None
    open_access: Optional[OpenAccess] = None
    authorships: Optional[List[Authorship]] = None
    countries_distinct_count: Optional[int] = None
    institutions_distinct_count: Optional[int] = None
    corresponding_author_ids: Optional[List[str]] = None
    corresponding_institution_ids: Optional[List[str]] = None
    apc_list: Optional[APC] = None
    apc_paid: Optional[APC] = None
    has_fulltext: Optional[bool] = None
    cited_by_count: Optional[int] = None
    biblio: Optional[Biblio] = None
    is_retracted: Optional[bool] = None
    is_paratext: Optional[bool] = None
    concepts: Optional[List[Concept]] = None
    mesh: Optional[List[Any]] = None
    locations_count: Optional[int] = None
    locations: Optional[List[ArtifactLocation]] = None
    best_oa_location: Optional[ArtifactLocation] = None
    sustainable_development_goals: Optional[List[Goal]] = None
    grants: Optional[List[Any]] = None
    referenced_works_count: Optional[int] = None
    referenced_works: Optional[List[str]] = None
    related_works: Optional[List[str]] = None
    ngrams_url: Optional[str] = None
    abstract_inverted_index: Optional[dict] = None
    cited_by_api_url: Optional[str] = None
    counts_by_year: Optional[List[CountByYear]] = None
    updated_date: Optional[datetime] = None
    created_date: Optional[date] = None
    full_text: Optional[str] = None
    extracted_concepts: Optional[List[PromptResponse]] = None

    def _get_pdf_url(self) -> str | None:
        """Returns the PDF URL of the artifact.

        Usage example:
        >>>artifact = ResearchArtifact()
        >>>artifact._get_pdf_url()

        Args:

        Returns:
            str: PDF URL of the artifact.

        Raises:
            None
        """
        if self.open_access.is_oa:
            if self.best_oa_location.pdf_url is None:
                return self.open_access.oa_url
            else:
                return self.best_oa_location.pdf_url
        else:
            return None

    def referenced_works_ids(self):
        return [_.split("/")[-1] for _ in self.referenced_works]

    def get_full_text(self):
        if self.full_text is not None:
            logger.info("Full text already available.")
        else:
            try:
                url = self._get_pdf_url()
                if url is not None:
                    text_loader = TextLoader()
                    full_text_pull = text_loader.read_pdf_from_url(url=url)
                    if full_text_pull is not None:
                        self.full_text = "\n".join(
                            text_loader.read_pdf_from_url(self.best_oa_location.pdf_url)
                        )
                else:
                    logger.info("PDF URL not found.")
            except Exception as e:
                logger.info("Error while pulling full text. " + str(e))


class CitationEdge(BaseModel):
    cited_by: ResearchArtifact
    cites: ResearchArtifact
