import enum
from dataclasses import dataclass

class CNVType(enum.StrEnum):
    LOSS = 'loss'
    GAIN = 'gain'

@dataclass
class CNVRegion:
    chr: str
    start: int
    end: int
    cnv_type: CNVType

    @property
    def length(self)-> int:
        return self.end - self.start

    @property
    def name(self):
        return f"{self.chr}_{self.start}_{self.end}_{self.cnv_type}"
