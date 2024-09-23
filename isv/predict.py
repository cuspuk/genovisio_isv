import enum
import json
import sys
from dataclasses import dataclass

import joblib
import pandas as pd
import xgboost as xgb

from isv.annotate import CNVAnnotation
from isv.src import cnv_region, constants


class ACMGClassification(enum.StrEnum):
    PATHOGENIC = "Pathogenic"
    LIKELY_PATHOGENIC = "Likely Pathogenic"
    VOUS = "VOUS"
    LIKELY_BENIGN = "Likely Benign"
    BENIGN = "Benign"


def get_class_threshold_0_5(prediction: float) -> ACMGClassification:
    if prediction < 0.05:
        return ACMGClassification.BENIGN
    elif prediction > 0.95:
        return ACMGClassification.PATHOGENIC
    else:
        return ACMGClassification.VOUS


def get_class_threshold_5_10(prediction: float) -> ACMGClassification:
    if prediction < 0.05:
        return ACMGClassification.BENIGN
    elif prediction < 0.1:
        return ACMGClassification.LIKELY_BENIGN
    elif prediction > 0.95:
        return ACMGClassification.PATHOGENIC
    elif prediction > 0.9:
        return ACMGClassification.LIKELY_PATHOGENIC
    else:
        return ACMGClassification.VOUS


def get_class_threshold_10_20(prediction: float) -> ACMGClassification:
    if prediction < 0.1:
        return ACMGClassification.BENIGN
    elif prediction < 0.2:
        return ACMGClassification.LIKELY_BENIGN
    elif prediction > 0.9:
        return ACMGClassification.PATHOGENIC
    elif prediction > 0.8:
        return ACMGClassification.LIKELY_PATHOGENIC
    else:
        return ACMGClassification.VOUS


def get_class_threshold_25_50(prediction: float) -> ACMGClassification:
    if prediction < 0.25:
        return ACMGClassification.BENIGN
    elif prediction < 0.5:
        return ACMGClassification.LIKELY_BENIGN
    elif prediction > 0.75:
        return ACMGClassification.PATHOGENIC
    elif prediction > 0.5:
        return ACMGClassification.LIKELY_PATHOGENIC
    else:
        return ACMGClassification.VOUS


def get_isv_score(prediction: float) -> float:
    isv_score = (prediction * 2) - 1
    return isv_score


def get_acmg_classification(isv_score: float) -> ACMGClassification:
    if isv_score >= 0.99:
        return ACMGClassification.PATHOGENIC
    elif isv_score >= 0.9:
        return ACMGClassification.LIKELY_PATHOGENIC
    elif isv_score >= -0.89:
        return ACMGClassification.VOUS
    elif isv_score > -0.99:
        return ACMGClassification.LIKELY_BENIGN
    else:
        return ACMGClassification.BENIGN


@dataclass
class Prediction:
    isv_prediction: float
    isv_score: float
    isv_classification: ACMGClassification
    isv_shap_values: dict[str, float]

    def to_dict(self) -> dict[str, str | float | dict[str, float]]:
        return {
            "isv_prediction": self.isv_prediction,
            "isv_score": self.isv_score,
            "isv_classification": self.isv_classification,
            "isv_shap_values": self.isv_shap_values,
        }


def format_model_path(cnvtype: cnv_region.CNVType) -> str:
    return f"isv/models/isv2_{cnvtype}.json"


def get_attributes(cnvtype: cnv_region.CNVType) -> list[str]:
    if cnvtype == cnv_region.CNVType.LOSS:
        return constants.LOSS_ATTRIBUTES
    elif cnvtype == cnv_region.CNVType.GAIN:
        return constants.GAIN_ATTRIBUTES
    else:
        raise ValueError("Invalid CNV type")


def prepare_dataframe(annotated_cnv: CNVAnnotation) -> pd.DataFrame:
    attributes = get_attributes(annotated_cnv.region.cnv_type)

    cnv_dct = annotated_cnv.as_flat_dict()
    annotated_cnv_floats = {col: float(cnv_dct[col]) for col in cnv_dct if col in attributes}
    df = pd.DataFrame.from_dict(annotated_cnv_floats, orient="index").T
    return df[attributes]


def predict(annotated_cnv: CNVAnnotation) -> Prediction:
    model_path = format_model_path(annotated_cnv.region.cnv_type)
    print(f"Loading model from {model_path=}", file=sys.stderr)
    loaded_model = joblib.load(model_path)

    input_df = prepare_dataframe(annotated_cnv)

    dmat_cnvs = xgb.DMatrix(input_df)
    prediction_cnvs = loaded_model.predict(dmat_cnvs)
    print(f"{prediction_cnvs=}", file=sys.stderr)
    predictions_df = pd.DataFrame(prediction_cnvs, columns=["isv2_predictions"])
    print(f"{predictions_df=}", file=sys.stderr)
    predictions_df["isv2_prediction_2"] = (predictions_df["isv2_predictions"] > 0.5) * 1

    # add class when using threshold
    predictions_df["isv2_prediction_threshold_5_10"] = predictions_df["isv2_predictions"].apply(
        get_class_threshold_5_10
    )
    predictions_df["isv2_prediction_threshold_10_20"] = predictions_df["isv2_predictions"].apply(
        get_class_threshold_10_20
    )
    predictions_df["isv2_prediction_threshold_25_50"] = predictions_df["isv2_predictions"].apply(
        get_class_threshold_25_50
    )

    # isv score from prediction
    predictions_df["isv2_score"] = predictions_df["isv2_predictions"].apply(get_isv_score)
    predictions_df["isv2_classification"] = predictions_df["isv2_score"].apply(get_acmg_classification)

    return Prediction(
        isv_prediction=predictions_df["isv2_predictions"].iloc[0].item(),
        isv_score=predictions_df["isv2_score"].iloc[0].item(),
        isv_classification=predictions_df["isv2_classification"].iloc[0],
        isv_shap_values={},
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Predict pathogenicity from annotated CNV.")
    parser.add_argument("input", help="Annotated CNV stored as json")
    parser.add_argument("--output", help="Path to store the prediction JSON. Else prints to stdout.", default=None)
    args = parser.parse_args()

    annotation = CNVAnnotation.from_json(args.input)
    prediction = predict(annotation)
    prediction_dict = prediction.to_dict()

    if args.output:
        json.dump(prediction_dict, open(args.output, "w"))
    else:
        print(json.dumps(prediction_dict, indent=2), file=sys.stdout)


if __name__ == "__main__":
    main()
