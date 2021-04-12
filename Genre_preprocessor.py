from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
import numpy as np
from scipy import stats
import pandas as pd
import time
from joblib import dump,load
from sklearn import metrics
from sklearn.model_selection import train_test_split,cross_val_score
from sklearn import preprocessing
from sklearn.neural_network import MLPClassifier
from sklearn.base import BaseEstimator,TransformerMixin


class DropTransformer(BaseEstimator,TransformerMixin):
    def __init__(self,drop=None):
        self.drop = drop

    def fit(self,X,y=None):
        return self
    
    def transform(self,X):
        return X.drop(columns=self.drop)

def topkscore(preds, ground_truth, model,k):
    if not len(preds) == len(ground_truth):
        raise exception('Shape Mismatch')
    
    mdfd_pred = []
    for i in range(len(preds)):
        preds_classes = model.classes_[preds[i].argsort()[::-1][:k]]
        if ground_truth[i] in preds_classes :
            mdfd_pred.append(ground_truth[i])
        else:
            mdfd_pred.append(preds_classes[0])
    return mdfd_pred

def top3predictions(preds,model,encoder):
    preds_classes = model.classes_[preds[0].argsort()[::-1][:3]]
    genre_confidence_dict = dict()
    for pred in preds_classes:
        genre_confidence_dict[encoder.inverse_transform(pred.reshape(-1))[0]] = preds[0][pred]
    return genre_confidence_dict

def train_pipeline():
    data = pd.read_csv('CleanData.csv')
    full_prep_pipeline = Pipeline([
        ('Drop',DropTransformer('loudness')), # During the data analysis portion we found loudness was a collinear feature that wasn't really needed so we drop it.
        ('Scaler',StandardScaler()),
        ('MLPModel',MLPClassifier(max_iter=300))
    ])
    Xval = data.drop(columns=['genre'])
    encoder = preprocessing.LabelEncoder()
    Yval = encoder.fit_transform(data['genre'])
    x_train, x_test, y_train, y_test = train_test_split (Xval, Yval, test_size = 0.2, random_state = 29,stratify=Yval)
    full_prep_pipeline.fit(x_train,y_train)
    y_pred = full_prep_pipeline.predict_proba(x_test)
    y_pred = topkscore(y_pred,y_test,full_prep_pipeline['MLPModel'],3)
    y_pred_label = encoder.inverse_transform(y_pred)
    y_test_label = encoder.inverse_transform(y_test)
    metric= metrics.classification_report (y_pred_label,y_test_label)
    dump(encoder,'Encoder.joblib') # We have so save the encoder to get back the actual values as the model just prints out integers.
    dump(full_prep_pipeline,'MLPModelPipeline.joblib')

def test_saved_pipeline():
    start = time.time()
    data = pd.read_csv('CleanData.csv')
    pipeline =  load('MLPModelPipeline.joblib')
    encoder  =  load('Encoder.joblib')
    Xval = data.drop(columns=['genre'])
    encoder = preprocessing.LabelEncoder()
    Yval = encoder.fit_transform(data['genre'])
    x_train, x_test, y_train, y_test = train_test_split (Xval, Yval, test_size = 0.2, random_state = 10,stratify=Yval)
    y_pred = pipeline.predict_proba(x_test)
    y_pred = topkscore(y_pred,y_test,pipeline['MLPModel'],3)
    y_pred_label = encoder.inverse_transform(y_pred)
    y_test_label = encoder.inverse_transform(y_test)
    metric= metrics.classification_report (y_pred_label,y_test_label)
    return metric

'''
song_info = {
    "danceability": float,
    "energy": float,
    "key": float,
    "loudness": float,
    "mode": int,
    "speechiness": float,
    "acousticness": float,
    "instrumentalness": float,
    "liveness": float,
    "valence": float,
    "tempo": float,
    "duration_ms": float,
    "time_signature": int,
    "Song_name": Str,
    "popularity": int,
    "release_year": int,
    "is_explicit": int
} 
'''
def get_prediction(song_info):
    column_order = ['popularity', 'acousticness', 'danceability', 'duration_ms', 'energy',
       'instrumentalness', 'key', 'liveness', 'loudness', 'mode',
       'speechiness', 'tempo', 'time_signature', 'valence', 'is_explicit',
       'release_year'] # We need to keep the order in the same way we had it during the training process.
    pipeline =  load('MLPModelPipeline.joblib')
    encoder  =  load('Encoder.joblib')
    if 'Song_name' in song_info:
        del song_info['Song_name']
    song_info = pd.DataFrame(song_info, index=[0])
    song_info = song_info[column_order] # We need to reorder the columns in the way it was given in training otherwise it won't work correctly.
    prob  = pipeline.predict_proba(song_info)
    return top3predictions(prob,pipeline['MLPModel'],encoder)