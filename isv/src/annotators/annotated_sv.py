import enum
import sys
from dataclasses import dataclass
from typing import Any

from isv.src.dict_utils import count_or_append_types


class GenesDBAnnotatedTypes(enum.StrEnum):
    """Annotated types in the GenesDB database."""

    OMIM_MORBID_GENE = "omim_morbid_gene"
    OMIM_PHENOTYPE = "omim_phenotype"
    GENE_NAME = "gene_name"
    ASSOCIATED = "associated_gene_with_disease"


@dataclass
class GenesDBAnnotatedSVCounter:
    morbid_genes: int
    disease_associated_genes: int
    morbid_genes_list: list[str]
    disease_associated_genes_list: list[str]

    def to_dict_for_prediction(self) -> dict[str, int]:
        return {
            "morbid_genes": self.morbid_genes,
            "disease_associated_genes": self.disease_associated_genes,
        }

    def to_dict_for_annotation(self) -> dict[str, list[str] | int]:
        return {
            "morbid_genes_list": self.morbid_genes_list,
            "disease_associated_genes_list": self.disease_associated_genes_list,
            "morbid_genes_count": len(self.morbid_genes_list),
            "disease_associated_genes_count": len(self.disease_associated_genes_list),
        }


def count_annotated_sv(annot_sv_data: list[dict[str, Any]], element_type: str) -> GenesDBAnnotatedSVCounter:
    morbid_genes_dict: dict[str, int] = {}
    omim_phenotypes_dict: dict[str, int] = {}
    morbid_genes_list: list[str] = []
    omim_phenotypes_list: list[str] = []

    print(f"{annot_sv_data=}", file=sys.stderr)
    for doc in annot_sv_data:
        if GenesDBAnnotatedTypes.OMIM_MORBID_GENE in doc[element_type].keys():
            morbid_genes_dict = count_or_append_types(
                doc[element_type][GenesDBAnnotatedTypes.OMIM_MORBID_GENE], morbid_genes_dict
            )
            morbid_genes_list.append(doc[GenesDBAnnotatedTypes.GENE_NAME])

        if GenesDBAnnotatedTypes.OMIM_PHENOTYPE in doc[element_type].keys():
            omim_phenotypes_dict = count_or_append_types(GenesDBAnnotatedTypes.OMIM_PHENOTYPE, omim_phenotypes_dict)
            omim_phenotypes_list.append(doc[GenesDBAnnotatedTypes.GENE_NAME])

    return GenesDBAnnotatedSVCounter(
        morbid_genes=morbid_genes_dict.get("yes", 0),
        disease_associated_genes=omim_phenotypes_dict.get(GenesDBAnnotatedTypes.ASSOCIATED, 0),
        morbid_genes_list=morbid_genes_list,
        disease_associated_genes_list=omim_phenotypes_list,
    )
