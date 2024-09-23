import enum
from dataclasses import dataclass
from isv.src.dict_utils import iterate_sv_info
from typing import Any

class GenesDBGeneTypes(enum.StrEnum):
    """Types of genes as stored in the GenesDB database."""
    PROTEIN_CODING = 'protein_coding'
    PSEUDOGENE = 'pseudogene'
    LINC_RNA = 'lncrna'
    R_RNA = 'rrna'
    S_NRNA = 'snrna'
    MIRNA = 'mirna'
    OTHER = 'other'

@dataclass
class GenesDBGeneTypesCounter:
    protein_coding : int = 0
    pseudogene : int = 0
    lncrna : int = 0
    rrna : int = 0
    snrna : int = 0
    mirna : int = 0
    gene_type_other : int = 0
    gencode_genes: int = 0


def count_gene_types(genes_data: list[dict[str, Any]], element_type: str) -> GenesDBGeneTypesCounter:
    cnv_types_dict = iterate_sv_info(genes_data, element_type)

    counter = GenesDBGeneTypesCounter()
    if GenesDBGeneTypes.PROTEIN_CODING in cnv_types_dict:
        counter.protein_coding = cnv_types_dict[GenesDBGeneTypes.PROTEIN_CODING]

    for gene_type in cnv_types_dict.keys():
        if GenesDBGeneTypes.PSEUDOGENE in gene_type:
            counter.pseudogene += 1
        elif GenesDBGeneTypes.LINC_RNA in gene_type:
            counter.lncrna += 1
        elif GenesDBGeneTypes.R_RNA in gene_type:
            counter.rrna += 1
        elif GenesDBGeneTypes.S_NRNA in gene_type:
            counter.snrna += 1
        elif GenesDBGeneTypes.MIRNA in gene_type:
            counter.mirna += 1
        else:
            counter.gene_type_other += 1

    counter.gencode_genes = sum(cnv_types_dict.values())
    return counter
