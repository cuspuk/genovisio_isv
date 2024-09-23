import enum
from dataclasses import dataclass, field


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
