import argparse

from isv.annotate import annotate
from isv.predict import predict
from isv.src import cnv_region, constants, genovisio_sources_db


def main() -> None:
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Classify CNV and/or find intersecting items in MongoDB collections.")
    parser.add_argument(
        "input", help='Input string in the form "chr1:10000-20000/del". CNV type should be del/dup/loss/gain.'
    )
    parser.add_argument("--mongodb_uri", help="MongoDB full URI", default="mongodb://localhost:27017/")
    parser.add_argument("--db_name", help="MongoDB database name", default="genovisio")

    args = parser.parse_args()

    region = cnv_region.build_from_str(args.input)
    # attributes = constants.LOSS_ATTRIBUTES if cnv_region.cnv_type == CNVType.LOSS else constants.GAIN_ATTRIBUTES
    # TODO what is the purpose of the attributes?

    collection_parser = genovisio_sources_db.IntersectionCollectionsParser(
        uri=args.mongodb_uri,
        db_name=args.db_name,
        collection_names=constants.COLLECTION_NAMES,
        check_type_names=constants.CHECK_TYPE_NAMES,
    )

    annotation = annotate(region=region, collection_parser=collection_parser)
    annotation.store_as_json("annotation.json")

    predict(annotation, "predictions.json")


if __name__ == "__main__":
    main()
