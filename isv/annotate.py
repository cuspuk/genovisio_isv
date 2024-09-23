import argparse
import re
from dataclasses import dataclass
import isv.src.genovisio_sources_db as genovisio_sources_db
from isv.src import constants
from isv.src import annotators
from isv.src.cnv_region import CNVRegion, CNVType
import json


@dataclass
class CNVAnnotation:
    region: CNVRegion
    gene_type_counter: annotators.GenesDBGeneTypesCounter
    annot_sv_counter: annotators.GenesDBAnnotatedSVCounter
    hi_genes_counter: annotators.HIGenesCounter
    hi_regions_counter: annotators.HIRegionsCounter
    ts_region_counter: annotators.TSRegionsCounter
    regulatory_counter: annotators.RegulatoryTypesCounter

    def as_flat_dict(self):
        return self.region.__dict__ | self.gene_type_counter.__dict__ | self.annot_sv_counter.__dict__ | self.hi_genes_counter.__dict__ | self.hi_regions_counter.__dict__ | self.ts_region_counter.__dict__ | self.regulatory_counter.__dict__

    def store_as_json(self, path:str):
        with open(path, 'w') as f:
            json.dump(self.as_flat_dict(), f)


def annotate(
    *,
    region: CNVRegion,
    collection_parser: genovisio_sources_db.IntersectionCollectionsParser,
) -> CNVAnnotation:
    # Traverse collections and find intersections
    data = collection_parser.get_for_region(region)

    return CNVAnnotation(
        region = region,
        gene_type_counter = annotators.count_gene_types(data["Genes"], "gene_type"),
        annot_sv_counter = annotators.count_annotated_sv(data["Genes"], "AnnotSV"),
        hi_genes_counter = annotators.count_hi_genes(data["HI_gene"], "Haploinsufficiency Score"),
        hi_regions_counter = annotators.count_hi_regions(data["HI_region"], "Haploinsufficiency Score"),
        ts_region_counter = annotators.count_ts_regions(data["HI_region"], "Triplosensitivity Score"),
        regulatory_counter = annotators.count_regulatory_types(data["Regulatory"], "type"),
    )


def parse_input(input_str: str) -> CNVRegion:
    """
    Parse the input string of the form 'chr1:10000-20000/DEL' and return a dictionary.
    """
    match = re.match(r'(chr[\dXY]+):(\d+)-(\d+)/(\w+)', input_str)
    cnv_type_map = {'del': 'loss', 'dup': 'gain', 'gain': 'gain', 'loss': 'loss', 'aoh': 'loss'}
    if not match or match.group(4).lower() not in cnv_type_map.keys() or match.group(1) not in constants.ALLOWED_CHROMOSOMES:
        raise ValueError(f'Input format must be "chr1:10000-20000/del". CNV type should be {"/".join(cnv_type_map.keys())}. '
                         f'Chromosome should be {"/".join(constants.ALLOWED_CHROMOSOMES)}')

    return CNVRegion(
        chr=match.group(1),
        start=int(match.group(2)),
        end=int(match.group(3)),
        cnv_type=CNVType(cnv_type_map[match.group(4).lower()]),
    )


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Classify CNV and/or find intersecting items in MongoDB collections.')
    parser.add_argument('input', help='Input string in the form "chr1:10000-20000/del". CNV type should be del/dup/loss/gain.')
    parser.add_argument('--mongodb_uri', help='MongoDB full URI', default='mongodb://localhost:27017/')
    parser.add_argument('--db_name', help='MongoDB database name', default='genovisio')

    args = parser.parse_args()

    cnv_region = parse_input(args.input)
    attributes = constants.LOSS_ATTRIBUTES if cnv_region.cnv_type == CNVType.LOSS else constants.GAIN_ATTRIBUTES

    collection_names = ['Benign_CNV', 'Regulatory', 'GnomAD', 'HI_gene', 'HI_region', 'Genes']
    check_type_names = ['Benign_CNV']

    collection_parser = genovisio_sources_db.IntersectionCollectionsParser(
        uri=args.mongodb_uri,
        db_name=args.db_name,
        collection_names=collection_names,
        check_type_names=check_type_names,
    )

    annotation = annotate(
        region=cnv_region,
        collection_parser=collection_parser
    )
    annotation.store_as_json('annotation.json')


if __name__ == '__main__':
    main()
