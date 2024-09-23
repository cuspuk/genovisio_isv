import argparse
import re

from isv.annotate import annotate
from isv.predict import predict
from isv.src import cnv_region, constants, genovisio_sources_db


def parse_input(input_str: str) -> cnv_region.CNVRegion:
    """
    Parse the input string of the form 'chr1:10000-20000/DEL' and return a dictionary.
    """
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


def main() -> None:
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Classify CNV and/or find intersecting items in MongoDB collections.")
    parser.add_argument(
        "input", help='Input string in the form "chr1:10000-20000/del". CNV type should be del/dup/loss/gain.'
    )
    parser.add_argument("--mongodb_uri", help="MongoDB full URI", default="mongodb://localhost:27017/")
    parser.add_argument("--db_name", help="MongoDB database name", default="genovisio")

    args = parser.parse_args()

    cnv_region = parse_input(args.input)
    # attributes = constants.LOSS_ATTRIBUTES if cnv_region.cnv_type == CNVType.LOSS else constants.GAIN_ATTRIBUTES
    # TODO what is the purpose of the attributes?

    collection_parser = genovisio_sources_db.IntersectionCollectionsParser(
        uri=args.mongodb_uri,
        db_name=args.db_name,
        collection_names=constants.COLLECTION_NAMES,
        check_type_names=constants.CHECK_TYPE_NAMES,
    )

    annotation = annotate(region=cnv_region, collection_parser=collection_parser)
    annotation.store_as_json("annotation.json")

    predict(annotation, "predictions.json")


if __name__ == "__main__":
    main()
