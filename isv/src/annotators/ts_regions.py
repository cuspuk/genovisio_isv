import sys
from dataclasses import dataclass
from typing import Any

from isv.src.dict_utils import iterate_sv_info

_INVALID_TS_REGIONS_VALUES = [40, 0, "Not yet evaluated"]


@dataclass
class TSRegionsCounter:
    regions_TS: int


def count_ts_regions(ts_regions_data: list[dict[str, Any]], element_type: str) -> TSRegionsCounter:
    cnv_types_dict_TS = iterate_sv_info(ts_regions_data, element_type)
    print(f"{cnv_types_dict_TS=}", file=sys.stderr)

    cnv_types_dict_TS = {k: v for k, v in cnv_types_dict_TS.items() if k not in _INVALID_TS_REGIONS_VALUES}
    return TSRegionsCounter(regions_TS=sum(cnv_types_dict_TS.values()))
