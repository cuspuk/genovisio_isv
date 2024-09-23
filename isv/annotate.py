import json
from dataclasses import dataclass

from isv.src import annotators, cnv_region, genovisio_sources_db


@dataclass
class CNVAnnotation:
    region: cnv_region.CNVRegion
    gene_type_counter: annotators.GenesDBGeneTypesCounter
    annot_sv_counter: annotators.GenesDBAnnotatedSVCounter
    hi_genes_counter: annotators.HIGenesCounter
    hi_regions_counter: annotators.HIRegionsCounter
    ts_region_counter: annotators.TSRegionsCounter
    regulatory_counter: annotators.RegulatoryTypesCounter

    def as_flat_dict(self) -> dict[str, str | int]:
        return (
            self.region.__dict__
            | self.gene_type_counter.__dict__
            | self.annot_sv_counter.__dict__
            | self.hi_genes_counter.__dict__
            | self.hi_regions_counter.__dict__
            | self.ts_region_counter.__dict__
            | self.regulatory_counter.__dict__
        )

    def store_as_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.as_flat_dict(), f, indent=2)


def annotate(
    *,
    region: cnv_region.CNVRegion,
    collection_parser: genovisio_sources_db.IntersectionCollectionsParser,
) -> CNVAnnotation:
    # Traverse collections and find intersections
    data = collection_parser.get_for_region(region)

    return CNVAnnotation(
        region=region,
        gene_type_counter=annotators.count_gene_types(data["Genes"], "gene_type"),
        annot_sv_counter=annotators.count_annotated_sv(data["Genes"], "AnnotSV"),
        hi_genes_counter=annotators.count_hi_genes(data["HI_gene"], "Haploinsufficiency Score"),
        hi_regions_counter=annotators.count_hi_regions(data["HI_region"], "Haploinsufficiency Score"),
        ts_region_counter=annotators.count_ts_regions(data["HI_region"], "Triplosensitivity Score"),
        regulatory_counter=annotators.count_regulatory_types(data["Regulatory"], "type"),
    )
