import enum

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


def predict(annotated_cnv: CNVAnnotation, path_to_save_predictions: str) -> None:
    cnv_type = annotated_cnv.region.cnv_type

    annotated_cnv_floats: dict[str, float] = {}
    cnv_prediction_dict = dict()

    if cnv_type == cnv_region.CNVType.LOSS:
        attributes = constants.LOSS_ATTRIBUTES
    elif cnv_type == cnv_region.CNVType.GAIN:
        attributes = constants.GAIN_ATTRIBUTES
    else:
        raise ValueError("Invalid CNV type")
        print("Invalid CNV type")  # TODO ????

    # load saved model
    model_path = "./isv/models/isv2_" + cnv_type + ".json"
    loaded_model = joblib.load(model_path)

    # get predictions from annotated CNVs

    annotated_cnv_dct = annotated_cnv.as_flat_dict()
    for column in attributes:
        annotated_cnv_floats[column] = float(annotated_cnv_dct[column])

    input_df = pd.DataFrame.from_dict(annotated_cnv_floats, orient="index").T

    dmat_cnvs = xgb.DMatrix(input_df[attributes])
    prediction_cnvs = loaded_model.predict(dmat_cnvs)
    predictions_df = pd.DataFrame(prediction_cnvs, columns=["isv2_predictions"])
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

    # get predictions
    # cnvs_predictions_df = pd.concat([annotated_cnv[["chr", "start", "end", "cnv_type"]], predictions_df], axis=1)
    # TODO ...

    # store predictions
    path_to_save_predictions = "predictions.tsv"
    predictions_df.to_csv(path_to_save_predictions, sep="\t", index=False)

    print("Predictions stored to " + path_to_save_predictions)

    # fill dict
    cnv_prediction_dict["isv_prediction"] = predictions_df["isv2_predictions"].iloc[0].item()
    cnv_prediction_dict["isv_score"] = predictions_df["isv2_score"].iloc[0].item()
    cnv_prediction_dict["isv_classification"] = predictions_df["isv2_classification"].iloc[0]
    cnv_prediction_dict["isv_shap_values"] = {}

    print(f"{cnv_prediction_dict=}")
