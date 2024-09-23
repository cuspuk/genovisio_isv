import enum
import re
from dataclasses import dataclass, field

from isv.src import cnv_region, constants


class CNVType(enum.StrEnum):
    LOSS = "loss"
    GAIN = "gain"


@dataclass
class CNVRegion:
    chr: str
    start: int
    end: int
    cnv_type: CNVType
    length: int = field(init=False)

    def __post_init__(self) -> None:
        self.length = self.end - self.start

    @property
    def name(self) -> str:
        return f"{self.chr}_{self.start}_{self.end}_{self.cnv_type}"


def build_from_str(input_str: str) -> CNVRegion:
    match = re.match(r"(chr[\dXY]+):(\d+)-(\d+)/(\w+)", input_str)
    cnv_type_map = {"del": "loss", "dup": "gain", "gain": "gain", "loss": "loss", "aoh": "loss"}
    if (
        not match
        or match.group(4).lower() not in cnv_type_map.keys()
        or match.group(1) not in constants.ALLOWED_CHROMOSOMES
    ):
        raise ValueError(
            f'Input format must be "chr1:10000-20000/del". CNV type should be {"/".join(cnv_type_map.keys())}. '
            f'Chromosome should be {"/".join(constants.ALLOWED_CHROMOSOMES)}'
        )

    return cnv_region.CNVRegion(
        chr=match.group(1),
        start=int(match.group(2)),
        end=int(match.group(3)),
        cnv_type=cnv_region.CNVType(cnv_type_map[match.group(4).lower()]),
    )
