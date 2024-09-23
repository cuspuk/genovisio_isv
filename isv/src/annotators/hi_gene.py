import sys
from dataclasses import dataclass
from typing import Any

from isv.src.dict_utils import iterate_sv_info

_INVALID_HI_GENE_VALUES = [40, 0, "", "nan"]


@dataclass
class HIGenesCounter:
    hi_genes: int


def count_hi_genes(hi_gene_data: list[dict[str, Any]], element_type: str) -> HIGenesCounter:
    cnv_types_dict_HI_genes = iterate_sv_info(hi_gene_data, element_type)
    print(f"{cnv_types_dict_HI_genes=}", file=sys.stderr)

    cnv_types_dict_HI_genes = {k: v for k, v in cnv_types_dict_HI_genes.items() if k not in _INVALID_HI_GENE_VALUES}
    return HIGenesCounter(hi_genes=sum(cnv_types_dict_HI_genes.values()))
