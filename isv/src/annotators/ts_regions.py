
from isv.src.dict_utils import iterate_sv_info
from typing import Any

from dataclasses import dataclass

_INVALID_TS_REGIONS_VALUES = [40, 0, "Not yet evaluated"]

@dataclass
class TSRegionsCounter:
    ts_regions: int

    def to_dict(self) -> dict[str, int]:
        return {
            "ts_regions": self.ts_regions,
        }

def count_ts_regions(ts_regions_data: list[dict[str, Any]], element_type: str) -> TSRegionsCounter:
    cnv_types_dict_TS = iterate_sv_info(ts_regions_data, element_type)
    cnv_types_dict_TS = {
        k: v for k, v in cnv_types_dict_TS.items() if k not in _INVALID_TS_REGIONS_VALUES
    }
    return TSRegionsCounter(ts_regions=sum(cnv_types_dict_TS.values()))


