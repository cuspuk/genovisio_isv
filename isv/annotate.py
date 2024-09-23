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

    @classmethod
    def from_json(cls, path: str) -> "CNVAnnotation":
        with open(path) as f:
            data = json.load(f)
        return cls(
            region=cnv_region.CNVRegion(**data),
            gene_type_counter=annotators.GenesDBGeneTypesCounter(**data),
            annot_sv_counter=annotators.GenesDBAnnotatedSVCounter(**data),
            hi_genes_counter=annotators.HIGenesCounter(**data),
            hi_regions_counter=annotators.HIRegionsCounter(**data),
            ts_region_counter=annotators.TSRegionsCounter(**data),
            regulatory_counter=annotators.RegulatoryTypesCounter(**data),
        )


def annotate(
    *,
    region: cnv_region.CNVRegion,
    collection_parser: genovisio_sources_db.IntersectionCollectionsParser,
) -> CNVAnnotation:
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


def main() -> None:
    import argparse

    from isv.src import constants

    parser = argparse.ArgumentParser(description="Annotate CNV and/or find intersecting items in MongoDB collections.")
    parser.add_argument(
        "input", help='Input string in the form "chr1:10000-20000/del". CNV type should be del/dup/loss/gain.'
    )
    parser.add_argument("--mongodb_uri", help="MongoDB full URI", default="mongodb://localhost:27017/")
    parser.add_argument("--db_name", help="MongoDB database name", default="genovisio")
    args = parser.parse_args()

    region = cnv_region.build_from_str(args.input)

    collection_parser = genovisio_sources_db.IntersectionCollectionsParser(
        uri=args.mongodb_uri,
        db_name=args.db_name,
        collection_names=constants.COLLECTION_NAMES,
        check_type_names=constants.CHECK_TYPE_NAMES,
    )

    annotation = annotate(region=region, collection_parser=collection_parser)
    annotation.store_as_json("annotation.json")


if __name__ == "__main__":
    main()
