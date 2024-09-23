from dataclasses import dataclass
from typing import Any
from isv.src.dict_utils import count_or_append_types
import enum


class GenesDBAnnotatedTypes(enum.StrEnum):
    """Annotated types in the GenesDB database."""
    OMIM_MORBID_GENE = "omim_morbid_gene"
    OMIM_PHENOTYPE = "omim_phenotype"

@dataclass
class GenesDBAnnotatedSVCounter:
    morbid_genes: int
    disease_associated_genes: int

    def to_dict(self) -> dict[str, int]:
        return {
            "morbid_genes": self.morbid_genes,
            "disease_associated_genes": self.disease_associated_genes,
        }

def count_annotated_sv(sv_data: list[dict[str, Any]], element_type: str) -> GenesDBAnnotatedSVCounter:
    morbid_genes_dict = {}
    omim_phenotypes_dict = {}

    for doc in sv_data:
        if GenesDBAnnotatedTypes.OMIM_MORBID_GENE in doc[element_type].keys():
            morbid_genes_dict = count_or_append_types(
                doc[element_type][GenesDBAnnotatedTypes.OMIM_MORBID_GENE], morbid_genes_dict
            )

        if GenesDBAnnotatedTypes.OMIM_PHENOTYPE in doc[element_type].keys():
            omim_phenotypes_dict = count_or_append_types(
                doc[element_type][GenesDBAnnotatedTypes.OMIM_PHENOTYPE], omim_phenotypes_dict
            )

    return GenesDBAnnotatedSVCounter(
        morbid_genes=morbid_genes_dict.get("yes", 0),
        disease_associated_genes=sum(omim_phenotypes_dict.values())
    )
