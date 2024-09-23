import enum
from dataclasses import dataclass
from typing import Any
from isv.src.dict_utils import iterate_sv_info

class RegulatoryTypes(enum.StrEnum):
    """Types of regulatory elements as stored in the database."""
    ENAHNCER = "enhancer"
    PROMOTER = "promoter"
    OPEN_CHROMATIN_REGION = "open_chromatin_region"
    CTCF_BINDING_SITE = "CTCF_binding_site"
    TF_BINDING_SITE = "TF_binding_site"
    CURATED = "regulatory_curated"
    FLANKING_REGION = "flanking_region"
    SILENCER = "silencer"
    TRANSCRIPTIONAL_CIS_REGULATORY_REGION = "transcriptional_cis_regulatory_region"
    DNASE_I_HYPERSENSITIVE_SITE = "DNase_I_hypersensitive_site"
    ENHANCER_BLOCKING_ELEMENT = "enhancer_blocking_element"
    TATA_BOX = "TATA_box"



@dataclass
class RegulatoryTypesCounter:
    regulatory_enhancer: int
    regulatory_promoter: int
    regulatory_open_chromatin_region: int
    regulatory_CTCF_binding_site: int
    regulatory_TF_binding_site: int
    regulatory_curated: int
    regulatory_flanking_region: int
    regulatory_silencer: int
    regulatory_transcriptional_cis_regulatory_region: int
    regulatory_DNase_I_hypersensitive_site: int
    regulatory_enhancer_blocking_element: int
    regulatory_TATA_box: int
    regulatory: int

    def to_dict(self)->dict[str, int]:
        return {
            "regulatory_enhancer": self.regulatory_enhancer,
            "regulatory_promoter": self.regulatory_promoter,
            "regulatory_open_chromatin_region": self.regulatory_open_chromatin_region,
            "regulatory_CTCF_binding_site": self.regulatory_CTCF_binding_site,
            "regulatory_TF_binding_site": self.regulatory_TF_binding_site,
            "regulatory_curated": self.regulatory_curated,
            "regulatory_flanking_region": self.regulatory_flanking_region,
            "regulatory_silencer": self.regulatory_silencer,
            "regulatory_transcriptional_cis_regulatory_region": self.regulatory_transcriptional_cis_regulatory_region,
            "regulatory_DNase_I_hypersensitive_site": self.regulatory_DNase_I_hypersensitive_site,
            "regulatory_enhancer_blocking_element": self.regulatory_enhancer_blocking_element,
            "regulatory_TATA_box": self.regulatory_TATA_box,
            "regulatory": self.regulatory,
        }

def count_regulatory_types(regulatory_data: list[dict[str, Any]], element_type: str) -> RegulatoryTypesCounter:
    cnv_types_dict = iterate_sv_info(regulatory_data, "type")
    counter = RegulatoryTypesCounter(
        regulatory_enhancer=cnv_types_dict.get(RegulatoryTypes.ENAHNCER, 0),
        regulatory_promoter=cnv_types_dict.get(RegulatoryTypes.PROMOTER, 0),
        regulatory_open_chromatin_region=cnv_types_dict.get(RegulatoryTypes.OPEN_CHROMATIN_REGION, 0),
        regulatory_CTCF_binding_site=cnv_types_dict.get(RegulatoryTypes.CTCF_BINDING_SITE, 0),
        regulatory_TF_binding_site=cnv_types_dict.get(RegulatoryTypes.TF_BINDING_SITE, 0),
        regulatory_curated=cnv_types_dict.get(RegulatoryTypes.CURATED, 0),
        regulatory_flanking_region=cnv_types_dict.get(RegulatoryTypes.FLANKING_REGION, 0),
        regulatory_silencer=cnv_types_dict.get(RegulatoryTypes.SILENCER, 0),
        regulatory_transcriptional_cis_regulatory_region=cnv_types_dict.get(RegulatoryTypes.TRANSCRIPTIONAL_CIS_REGULATORY_REGION, 0),
        regulatory_DNase_I_hypersensitive_site=cnv_types_dict.get(RegulatoryTypes.DNASE_I_HYPERSENSITIVE_SITE, 0),
        regulatory_enhancer_blocking_element=cnv_types_dict.get(RegulatoryTypes.ENHANCER_BLOCKING_ELEMENT, 0),
        regulatory_TATA_box=cnv_types_dict.get(RegulatoryTypes.TATA_BOX, 0),
        regulatory=sum(cnv_types_dict.values())
    )
    return counter