import itertools
import pandas as pd
import numpy as np
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.preprocessing import MinMaxScaler
import os
from pyod.models.abod import ABOD
from numpy import trapz

# This code applies Fast-ABOD on traffic data exploiting the TP-FDS (Temporal Positioning of Flow-Density Samples)

# Inputs:   1) directory of the data with labels from different experts.
#           2) n_neighbors in Fast-ABOD
#           3) label_thresh: certainty level used for deriving the ground truth labels

# Outputs:  1) a table containing F1-scores and AUCs (with their standard deviations) at different levels of ground truth certainty


# Inputs
directory = 'Labeled Data'
n_neighbors = [13]
label_thresh = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7]

# obtain a list of file names in the data directory
arr = sorted(os.listdir(directory))

# construct a range of thresholds to be applied on anoamly scores
model_thresh= [*range(0,100000,20)]
model_thresh = [-i for i in model_thresh]
model_thresh.append(-10^25)

# create a list of all possible combinations between label certanty level and model-thresh
comb_thresh = list(itertools.product(label_thresh, model_thresh))
comb_model = list(itertools.product(n_neighbors))

final = []

for n in comb_model:
    for loc in range(len(arr)):
        # read the data of a single location
        df = pd.read_csv('Labeled Data/' + arr[loc])
        df = df[['Date', 'Time', 'Volume', 'Density', 'Anomaly Probability']]
        # seperate 80% of data for training and validation
        data = df.iloc[:int(round(0.8*(len(df))))].copy()
        # define the "group" column which devides the data into 10 different groups
        b = int(len(data)/10)
        a = [e for x in zip(*[[0,1,2,3,4,5,6,7,8,9]]*b) for e in x]
        a.extend([9]*(len(data)-len(a)))
        data['group'] = a

        for b in range(9,10):
            # define the training and test set (here "val" is the test set)
            # if we put (val = data[data['group'].isin([b])]), the performance will be reported based on the validation set
            train = data[~data['group'].isin([b])]
            val = df.iloc[int(round(0.8*(len(df)))):].copy()
            train = train[['Time','Anomaly Probability','Volume','Density']].to_numpy()
            val = val[['Time','Anomaly Probability','Volume','Density']].to_numpy()
            # scale the data and modify it
            scaler = MinMaxScaler()
            scaler.fit(train[:,2:])
            train_scaled = scaler.transform(train[:,2:])
            val_scaled = scaler.transform(val[:,2:])
            df_train = pd.DataFrame()
            df_val = pd.DataFrame()
            df_train['Time'] = train[:,0]
            df_val['Time'] = val[:,0]
            df_train['Anomaly'] = train[:,1]
            df_val['Anomaly'] = val[:,1]
            df_train['Scaled_Volume'] = train_scaled[:,0]
            df_val['Scaled_Volume'] = val_scaled[:,0]
            df_train['Scaled_Density'] = train_scaled[:,1]
            df_val['Scaled_Density'] = val_scaled[:,1]
            
            T = df_train['Time'].unique()
            Real_scores = []
            Pred_scores = []
            # apply Fast-ABOD seperately on each batch (T) of data 
            for i in range(len(T)):
                target_train = df_train.loc[df_train['Time'].isin([T[i]])]
                target_val = df_val.loc[df_val['Time'].isin([T[i]])]
                clf = ABOD(method = 'fast', n_neighbors= n[0])
                clf.fit(target_train[['Scaled_Density', 'Scaled_Volume']].values)
                y_score = clf.decision_function(target_val[['Scaled_Density', 'Scaled_Volume']].values)
                Real_scores.extend(target_val['Anomaly'].tolist())
                Pred_scores.extend(y_score)
            # calculate performance metrics at different levels of certainty with various score thresholds
            for k in comb_thresh:
                Real = [1 if i >= k[0] else 0 for i in Real_scores]
                Pred = [1 if i >= k[1] else 0 for i in Pred_scores]
                tpr = round(recall_score(Real, Pred, zero_division=0),3)
                tnr = round(recall_score(Real, Pred, pos_label = 0, zero_division=0),3)
                fpr = 1 - tnr
                fnr = 1 - tpr
                per = round(precision_score(Real, Pred, zero_division=0),3)
                f1 = round(f1_score(Real, Pred, zero_division=0),3)
                report = {'Location':[arr[loc]], 'Label_Threshold':[k[0]], 'Model_Threshold':[k[1]], 'n_neighbors':[n[0]], 'FNR':[fnr],'FPR':[fpr],
                        'val_num':[b], 'TNR':[tnr], 'Recall':[tpr], 'Precision': [per], 'F1-score': [f1]}
                rep = pd.DataFrame(report)
                final.append(rep)

final = pd.concat(final)
df = final 
comb = list(itertools.product(arr, label_thresh, n_neighbors))
# calculate AUCs based on the derived performance metrics
L = []
for i in comb:
    dfp = df[(df['Location'].isin([i[0]])) & (df['Label_Threshold'].isin([i[1]])) & (
        df['n_neighbors'].isin([i[2]]))].copy()   
    dfp = dfp.sort_values(['Recall', 'FPR'], ascending=False)
    AUC = -trapz(dfp.Recall, dfp.FPR)
    report = {'Location':[i[0]], 'Label_Threshold':[i[1]], 'hp' : [str(i[2:])], 'AUC': [AUC]}
    rep = pd.DataFrame(report)
    L.append(rep)
L = pd.concat(L)
AUC_df = L
# create the final table of the results
O = []
for j in label_thresh:
    model_F1=[]
    model_F1_std = []
    for i in comb_model:
        dfp = df[(df['Label_Threshold'].isin([j])) & (df['n_neighbors'].isin([i[0]]))].copy()
        dfp = dfp.sort_values("F1-score", ascending=False)
        dfp = dfp.drop_duplicates(subset=["Location"], keep="first")
        model_F1.append(np.mean(dfp['F1-score']))
        model_F1_std.append(np.std(dfp['F1-score']))
    dff = AUC_df[AUC_df['Label_Threshold'].isin([j]) & AUC_df['hp'].isin([str(comb_model[model_F1.index(max(model_F1))])])]
    AUC = round(np.mean(dff['AUC']),3)
    AUC_std = round(np.std(dff['AUC']),3)
    report = {'Label_Threshold':[j], '(n_neighbors)':[comb_model[model_F1.index(max(model_F1))]], 
            'F1_score' : [round(max(model_F1),3)], 'F1_std': [model_F1_std[model_F1.index(max(model_F1))]], 
            'AUC': [AUC], 'AUC_std': [AUC_std]}
    rep = pd.DataFrame(report)
    O.append(rep)

O = pd.concat(O)
#return O (tbale of the results)
print(O)
