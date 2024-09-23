import pandas as pd
import numpy as np
import xgboost as xgb
import joblib

from collections import Counter
import sys
import os
import json

from isv.src.constants import LOSS_ATTRIBUTES, GAIN_ATTRIBUTES


# Class accroding to threshold
def get_class_threshold_0_5(prediction):
    if prediction < 0.05:
        return 'Benign'
    elif prediction > 0.95:
        return 'Pathogenic'
    else:
        return 'VOUS'


def get_class_threshold_5_10(prediction):
    if prediction < 0.05:
        return 'Benign'
    elif prediction < 0.1:
        return 'Likely Benign'
    elif prediction > 0.95:
        return 'Pathogenic'
    elif prediction > 0.9:
        return 'Likely Pathogenic'
    else:
        return 'VOUS'

def get_class_threshold_10_20(prediction):
    if prediction < 0.1:
        return 'Benign'
    elif prediction < 0.2:
        return 'Likely Benign'
    elif prediction > 0.9:
        return 'Pathogenic'
    elif prediction > 0.8:
        return 'Likely Pathogenic'
    else:
        return 'VOUS'


# bez vous
def get_class_threshold_25_50(prediction):
    if prediction < 0.25:
        return 'Benign'
    elif prediction < 0.5:
        return 'Likely Benign'
    elif prediction > 0.75:
        return 'Pathogenic'
    elif prediction > 0.5:
        return 'Likely Pathogenic'
    else:
        return 'VOUS'


def get_isv_score(prediction):

    isv_score = (prediction * 2) -1

    return isv_score

def get_acmg_classification(isv_score):

    if isv_score >= 0.99:
        return 'Pathogenic'
    elif isv_score >= 0.9:
        return 'Likely Pathogenic'
    elif isv_score >= -0.89:
        return 'VOUS'
    elif isv_score > -0.99:
        return 'Likely Benign'
    else:
        return 'Benign'





def get_predictions(annotated_cnv, path_to_save_predictions: str):

    cnv_type = annotated_cnv['cnv_type'].iloc[0]

    cnv_prediction_dict = dict()

    if cnv_type == 'loss':
        attributes = LOSS_ATTRIBUTES
    elif cnv_type == 'gain':
        attributes = GAIN_ATTRIBUTES
    else:
        print('Invalid CNV type')

    #load saved model
    model_path = './isv2_' + cnv_type + '.json'
    loaded_model = joblib.load(model_path)

    # get predictions from annotated CNVs

    for column in attributes:
        annotated_cnv[column] = annotated_cnv[column].astype('float')

    dmat_cnvs = xgb.DMatrix(annotated_cnv[attributes])
    prediction_cnvs = loaded_model.predict(dmat_cnvs)
    predictions_df = pd.DataFrame(prediction_cnvs, columns=['isv2_predictions'])
    predictions_df['isv2_prediction_2'] = (predictions_df['isv2_predictions'] > 0.5) *1

    # add class when using threshold
    predictions_df['isv2_prediction_threshold_5_10'] = predictions_df['isv2_predictions'].apply(get_class_threshold_5_10)
    predictions_df['isv2_prediction_threshold_10_20'] = predictions_df['isv2_predictions'].apply(get_class_threshold_10_20)
    predictions_df['isv2_prediction_threshold_25_50'] = predictions_df['isv2_predictions'].apply(get_class_threshold_25_50)

    # isv score from prediction
    predictions_df['isv2_score'] = predictions_df['isv2_predictions'].apply(get_isv_score)
    predictions_df['isv2_classification'] = predictions_df['isv2_score'].apply(get_acmg_classification)

    # get predictions
    cnvs_predictions_df = pd.concat([annotated_cnv[['chr', 'start', 'end', 'cnv_type']], predictions_df], axis=1)

    # print(cnvs_predictions_df)

    # store predictions
    path_to_save_predictions = path_to_save_predictions + '.tsv.gz'

    # Check if the file exists
    if not os.path.exists(path_to_save_predictions):
        cnvs_predictions_df.to_csv(path_to_save_predictions, sep='\t', index=False, compression='gzip')

    else:
        cnvs_predictions_df.to_csv(path_to_save_predictions, sep='\t', mode='a', compression='gzip', index=False, header=False)

    print('Predictions stored to ' + path_to_save_predictions)

    # fill dict
    cnv_prediction_dict['isv_prediction'] = predictions_df['isv2_predictions'].iloc[0].item()
    cnv_prediction_dict['isv_score'] = predictions_df['isv2_score'].iloc[0].item()
    cnv_prediction_dict['isv_classification'] = predictions_df['isv2_classification'].iloc[0]
    cnv_prediction_dict['isv_shap_values'] = {}
    return cnv_prediction_dict
