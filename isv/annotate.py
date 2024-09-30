import json
import os
import sys
from dataclasses import asdict, dataclass

from isv.src import annotators, cnv_region, genovisio_sources_db


@dataclass
class ISVAnnotValues:
    gencode_genes: int
    protein_coding: int
    pseudogenes: int
    mirna: int
    lncrna: int
    rrna: int
    snrna: int
    morbid_genes: int
    disease_associated_genes: int
    hi_genes: int
    regions_HI: int
    regions_TS: int
    regulatory: int
    regulatory_enhancer: int
    regulatory_silencer: int
    regulatory_transcriptional_cis_regulatory_region: int
    regulatory_promoter: int
    regulatory_DNase_I_hypersensitive_site: int
    regulatory_enhancer_blocking_element: int
    regulatory_TATA_box: int

    def as_dict_of_attributes(self) -> dict[str, int]:
        return asdict(self)


@dataclass
class AnnotationsReporting:
    HI_genes: list[str]
    TS_genes: list[str]
    morbid_genes: list[str]
    disease_associated_genes: list[str]


@dataclass
class CNVAnnotation:
    cnv: cnv_region.CNVRegion
    isv_annot_values: ISVAnnotValues
    annotations_reporting: AnnotationsReporting

    @classmethod
    def build(
        cls,
        region: cnv_region.CNVRegion,
        gene_type_counter: annotators.GenesDBGeneTypesCounter,
        annot_sv: annotators.GenesDBAnnotatedSV,
        hi_ts_genes: annotators.HIandTSGenes,
        hi_regions_counter: annotators.HIRegionsCounter,
        ts_region_counter: annotators.TSRegionsCounter,
        regulatory_counter: annotators.RegulatoryTypesCounter,
    ) -> "CNVAnnotation":
        return cls(
            cnv=region,
            isv_annot_values=ISVAnnotValues(
                gencode_genes=gene_type_counter.gencode_genes,
                protein_coding=gene_type_counter.protein_coding,
                pseudogenes=gene_type_counter.pseudogenes,
                lncrna=gene_type_counter.lncrna,
                rrna=gene_type_counter.rrna,
                snrna=gene_type_counter.snrna,
                mirna=gene_type_counter.mirna,
                morbid_genes=annot_sv.morbid_genes,
                disease_associated_genes=annot_sv.disease_associated_genes,
                hi_genes=hi_ts_genes.hi_genes,
                regions_HI=hi_regions_counter.regions_HI,
                regions_TS=ts_region_counter.regions_TS,
                regulatory=regulatory_counter.regulatory,
                regulatory_enhancer=regulatory_counter.regulatory_enhancer,
                regulatory_silencer=regulatory_counter.regulatory_silencer,
                regulatory_transcriptional_cis_regulatory_region=regulatory_counter.regulatory_transcriptional_cis_regulatory_region,
                regulatory_promoter=regulatory_counter.regulatory_promoter,
                regulatory_DNase_I_hypersensitive_site=regulatory_counter.regulatory_DNase_I_hypersensitive_site,
                regulatory_enhancer_blocking_element=regulatory_counter.regulatory_enhancer_blocking_element,
                regulatory_TATA_box=regulatory_counter.regulatory_TATA_box,
            ),
            annotations_reporting=AnnotationsReporting(
                HI_genes=hi_ts_genes.hi_genes_list,
                TS_genes=hi_ts_genes.ts_genes_list,
                morbid_genes=annot_sv.morbid_genes_list,
                disease_associated_genes=annot_sv.disease_associated_genes_list,
            ),
        )

    # def as_flat_dict(self) -> dict[str, str | int]:
    #     return (
    #         self.region.__dict__
    #         | self.gene_type_counter.__dict__
    #         | self.annot_sv.__dict__
    #         | self.hi_ts_genes.__dict__
    #         | self.hi_regions_counter.__dict__
    #         | self.ts_region_counter.__dict__
    #         | self.regulatory_counter.__dict__
    #     )

    # def output_dict(self) -> dict[str, dict[str, str | int | list[str]]]:
    #     return {
    #         "cnv": self.region.__dict__,
    #         "isv_annot_values": self.gene_type_counter.__dict__
    #         | self.annot_sv.__dict__
    #         | self.hi_ts_genes.to_dict_for_prediction()
    #         | self.hi_regions_counter.__dict__
    #         | self.ts_region_counter.__dict__
    #         | self.regulatory_counter.__dict__,
    #         "annotations_reporting": self.annot_sv.to_dict_for_annotation()
    #         | self.hi_ts_genes.to_dict_for_annotation(),
    #     }

    def store_as_json(self, path: str) -> None:
        path = os.path.abspath(path)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def from_json(cls, path: str) -> "CNVAnnotation":
        with open(path) as f:
            data = json.load(f)
        return cls(**data)


def annotate(
    *,
    region: cnv_region.CNVRegion,
    collection_parser: genovisio_sources_db.IntersectionCollectionsParser,
) -> CNVAnnotation:
    data = collection_parser.get_for_region(region)
    return CNVAnnotation.build(
        region=region,
        gene_type_counter=annotators.count_gene_types(data["Genes"], "gene_type"),
        annot_sv=annotators.count_annotated_sv(data["Genes"], "AnnotSV"),
        hi_ts_genes=annotators.count_hi_genes(data["HI_gene"], "Haploinsufficiency Score"),
        hi_regions_counter=annotators.count_hi_regions(data["HI_region"], "Haploinsufficiency Score"),
        ts_region_counter=annotators.count_ts_regions(data["HI_region"], "Triplosensitivity Score"),
        regulatory_counter=annotators.count_regulatory_types(data["Regulatory"], "type"),
    )


def main() -> None:
    import argparse

    from isv.src import constants

    parser = argparse.ArgumentParser(description="Annotate CNV and/or find intersecting items in MongoDB collections.")
    parser.add_argument("input", help='Input string in the format "chr1:10000-20000/del"')
    parser.add_argument("--mongodb_uri", help="MongoDB full URI", default="mongodb://localhost:27017/")
    parser.add_argument("--db_name", help="MongoDB database name", default="genovisio")
    parser.add_argument("--output", help="Path to store the annotation JSON. Else prints to stdout.", default=None)
    args = parser.parse_args()

    region = cnv_region.build_from_str(args.input)

    collection_parser = genovisio_sources_db.IntersectionCollectionsParser(
        uri=args.mongodb_uri,
        db_name=args.db_name,
        collection_names=constants.COLLECTION_NAMES,
        check_type_names=constants.CHECK_TYPE_NAMES,
    )

    annotation = annotate(region=region, collection_parser=collection_parser)
    if args.output:
        annotation.store_as_json(args.output)
    else:
        print(json.dumps(asdict(annotation), indent=2), file=sys.stdout)


if __name__ == "__main__":
    main()
