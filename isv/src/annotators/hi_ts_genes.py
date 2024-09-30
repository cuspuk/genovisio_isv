import sys
from dataclasses import dataclass
from typing import Any

from isv.src.dict_utils import iterate_sv_info

_INVALID_HI_GENE_VALUES = [40, 0, "", "nan"]


@dataclass
class HIandTSGenes:
    hi_genes: int
    hi_genes_list: list[str]
    ts_genes_list: list[str]

    def to_dict_for_prediction(self) -> dict[str, int]:
        return {
            "hi_genes": self.hi_genes,
        }

    def to_dict_for_annotation(self) -> dict[str, list[str] | int]:
        return {
            "TS_genes": self.ts_genes_list,
            "HI_genes": self.hi_genes_list,
            "HI_genes_count": len(self.hi_genes_list),
            "TS_genes_count": len(self.ts_genes_list),
        }


def count_hi_genes(hi_gene_data: list[dict[str, Any]], element_type: str) -> HIandTSGenes:
    cnv_types_dict_HI_genes = iterate_sv_info(hi_gene_data, element_type)
    print(f"{cnv_types_dict_HI_genes=}", file=sys.stderr)

    cnv_types_dict_HI_genes = {k: v for k, v in cnv_types_dict_HI_genes.items() if k not in _INVALID_HI_GENE_VALUES}

    hi_genes_list: list[str] = []
    ts_genes_list: list[str] = []
    if len(hi_gene_data) > 0:
        for i, hi_gene in enumerate(hi_gene_data):
            hi_score = hi_gene_data[i]["Haploinsufficiency Score"]
            ts_score = hi_gene_data[i]["Triplosensitivity Score"]

            if hi_score == 1 or hi_score == 2 or hi_score == 3 or hi_score == 30:
                hi_genes_list.append(hi_gene_data[i]["Gene Symbol"])

            if ts_score == "1" or ts_score == "2" or ts_score == "3" or ts_score == "30":
                ts_genes_list.append(hi_gene_data[i]["Gene Symbol"])

    return HIandTSGenes(
        hi_genes=sum(cnv_types_dict_HI_genes.values()),
        hi_genes_list=hi_genes_list,
        ts_genes_list=ts_genes_list,
    )
