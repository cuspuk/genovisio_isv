import argparse
import json
import sys

from isv.annotate import annotate
from isv.predict import predict
from isv.src import cnv_region, constants, genovisio_sources_db


def main() -> None:
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Classify CNV and/or find intersecting items in MongoDB collections.")
    parser.add_argument("input", help='Input string in the format "chr1:10000-20000/del"')
    parser.add_argument("--mongodb_uri", help="MongoDB full URI", default="mongodb://localhost:27017/")
    parser.add_argument("--db_name", help="MongoDB database name", default="genovisio")
    parser.add_argument("--annotation-output", help="Path to store the annotation JSON. Else stdout.", default=None)
    parser.add_argument("--prediction-output", help="Path to store the prediction JSON. Else stdout.", default=None)
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

    prediction_dict = predict(annotation)

    if args.annotation_output:
        annotation.store_as_json(args.output)
    else:
        print(json.dumps(annotation.as_flat_dict(), indent=2), file=sys.stdout)

    if args.prediction_output:
        json.dump(prediction_dict, open(args.output, "w"))
    else:
        print(json.dumps(prediction_dict, indent=2), file=sys.stdout)


if __name__ == "__main__":
    main()
