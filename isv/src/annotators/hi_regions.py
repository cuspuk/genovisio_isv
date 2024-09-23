
from isv.src.dict_utils import iterate_sv_info
from typing import Any

from dataclasses import dataclass

_INVALID_HI_REGIONS_VALUES = [40, 0, "", "nan"]

@dataclass
class HIRegionsCounter:
    regions_HI: int


def count_hi_regions(hi_regions_data: list[dict[str, Any]], element_type: str) -> HIRegionsCounter:
    cnv_types_dict_HI = iterate_sv_info(hi_regions_data, element_type)
    print("HI CNV TYPES")
    print(cnv_types_dict_HI)
    cnv_types_dict_HI = {
        k: v for k, v in cnv_types_dict_HI.items() if k not in _INVALID_HI_REGIONS_VALUES
    }
    return HIRegionsCounter(regions_HI=sum(cnv_types_dict_HI.values()))

