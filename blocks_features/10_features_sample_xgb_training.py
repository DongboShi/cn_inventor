import pandas as pd
import numpy as np
from time import time
import os
from concurrent.futures import ThreadPoolExecutor
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score, roc_auc_score
import joblib
from multiprocessing import Pool, Manager
import gc


def show_folders(path):
    all_scientist_folder = []
    for root, folder, file in os.walk(path):
        if len(folder) == 0 and len(file) > 0:
            all_scientist_folder.append(root)
    return all_scientist_folder


def process_file(file):
    try:
        with open(file, 'r', encoding="utf-8") as f:
            content = f.readlines()
        feature_name = os.path.splitext(os.path.basename(file))[0]
        feature_values = [p.strip() for p in content]
        return feature_name, feature_values
    except Exception as error:
        print(f"Error reading {file}: {error}")
        return feature_name, []


def features_merge(inventor_folder, key_lst, results):
    try:
        start = time()
        # 根据提供的key_lst构建文件路径列表
        sorted_files = [f'{inventor_folder}/{key}.txt' for key in key_lst]

        feature_data = {}
        with ThreadPoolExecutor(max_workers=12) as executor:
            # 提交所有文件处理任务，并保留futures以保持顺序
            futures = [executor.submit(process_file, file) for file in sorted_files]
            # 按提交顺序获取future结果
            for future in futures:
                feature_name, feature_values = future.result()
                feature_data[feature_name] = feature_values

        # 合并为dataframe
        df = pd.DataFrame.from_dict(feature_data)
        df['inventor'] = os.path.basename(inventor_folder)
        end = time()
        df = df.apply(pd.to_numeric, errors='ignore')
        df['diff_days'] = df['diff_days'].abs()
        print(f'{inventor_folder} finished. Cost {end - start}s.')
        results.append(df)
    except Exception as e:
        print(f"Error in {inventor_folder}: {e}")


def features_df(features_all_path, key_lst):
    try:
        features_files = show_folders(features_all_path)
        manager = Manager()
        results = manager.list()
        pool = Pool(processes=18)
        for features_file in features_files:
            pool.apply_async(features_merge, (features_file, key_lst, results))
        pool.close()
        pool.join()

        combined_df = pd.concat(results, ignore_index=True)
        combined_df = combined_df[['inventor'] + key_lst]  # Ensure columns are ordered correctly
        return combined_df
    except Exception as e:
        print(f"Error: {e}")
        return pd.DataFrame()


def train_model(X, y, params):
    dtrain = xgb.DMatrix(X, label=y)
    model = xgb.train(params, dtrain, num_boost_round=100)
    return model


def predict_and_evaluate(model, X, y_true):
    dtest = xgb.DMatrix(X)
    y_pred = model.predict(dtest)
    y_pred_binary = np.where(y_pred > 0.5, 1, 0)
    f1_weighted = f1_score(y_true, y_pred_binary, average='weighted')
    auc = roc_auc_score(y_true, y_pred)
    return f1_weighted, auc, y_pred


def xgb_train_sci(train_index, test_index, X, y):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]

    model = train_model(X_train, y_train, params)
    f1_weighted, auc, _ = predict_and_evaluate(model, X_test, y_test)
    score = (f1_weighted, auc)
    joblib.dump(model, f'model/model_sci_{score}.pkl')
    with open(f'model/model_sci_score.txt', mode='a', encoding='utf-8') as f:
        f.write(f'{f1_weighted, auc}\n')
    print(score)
    return score


def xgb_train_mix(train_index, test_index, X, y):
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    X_train = pd.concat([X_train, df_rarename[features]], ignore_index=True)
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    y_train = pd.concat([y_train, df_rarename['label']], ignore_index=True)

    model = train_model(X_train, y_train, params)
    f1_weighted, auc, _ = predict_and_evaluate(model, X_test, y_test)
    score = (f1_weighted, auc)
    joblib.dump(model, f'model/model_mix_{score}.pkl')
    print(score)
    return score


def xgb_train_rare(train_index, test_index, X, y):
    X_test = X.iloc[test_index]
    X_train = df_rarename[features]
    y_test = y.iloc[test_index]
    y_train = df_rarename['label']

    model = train_model(X_train, y_train, params)
    f1_weighted, auc, _ = predict_and_evaluate(model, X_test, y_test)
    score = (f1_weighted, auc)
    joblib.dump(model, f'model/model_rare_{score}.pkl')
    print(score)
    return score


def adjust_params(scores, params):
    # Adjust parameters based on the average of F1 and AUC scores
    avg_score = np.mean(scores)
    if avg_score < 0.5:
        params['max_depth'] += 1
        params['eta'] -= 0.1
    elif avg_score < 0.75:
        params['max_depth'] += 1
    else:
        params['eta'] -= 0.02
    params['eta'] = max(params['eta'], 0.01)
    return params


key_lst = ['patents_cp', 'app_i', 'app_i_est', 'app_s', 'app_s_est',
           'inventor_i', 'inventor_i_est', 'ipc_c', 'ipc_c_est', 'ipc_g', 'ipc_g_est',
           'title', 'title_est', 'keyword1', 'keyword1_est', 'keyword2', 'keyword2_est',
           'address_s', 'address_s_est', 'geo', 'geo_est', 'citing_rp', 'citing_lst_est',
           'cited_lst_est', 'diff_days', 'label']

if __name__ == '__main__':
    df_rarename = features_df('rarename_features/0', key_lst)
    print('rarename over')
    # surnames = [os.path.splitext(os.path.basename(file))[0] for file in show_folders('rarename_features/0')]
    # df_rarename_sur = list(df_rarename['inventor'].unique())
    # lost_surnames = set(surnames)-set(df_rarename_sur)
    # for i in show_folders('rarename_features/0'):
    #     if os.path.splitext(os.path.basename(i))[0] in lost_surnames:
    #         sorted_files = [f'{i}/{key}.txt' for key in key_lst]
    #         feature_data = {}
    #         with ThreadPoolExecutor(max_workers=16) as executor:
    #             # 提交所有文件处理任务，并保留futures以保持顺序
    #             futures = [executor.submit(process_file, file) for file in sorted_files]
    #             # 按提交顺序获取future结果
    #             for future in futures:
    #                 feature_name, feature_values = future.result()
    #                 feature_data[feature_name] = feature_values
    #
    #         df = pd.DataFrame.from_dict(feature_data)
    #         df['inventor'] = os.path.splitext(os.path.basename(i))[0]
    #         df = df.apply(pd.to_numeric, errors='ignore')
    #         df['diff_days'] = df['diff_days'].abs()
    #         df_rarename = pd.concat([df_rarename, df], ignore_index=True)
    #         print(f'{i} append.')
    #
    # del feature_data
    # del df
    # del lost_surnames
    # del surnames
    # del df_rarename_sur
    # gc.collect()

    df_sci_neg = pd.read_csv('clean_data/features_scientists_neg.csv')
    df_sci_pos = pd.read_csv('clean_data/features_scientists_pos_new.csv')
    df_sci_neg['label'] = 0
    df_sci_pos['label'] = 1
    data = pd.concat([df_sci_neg, df_sci_pos], ignore_index=True)
    del df_sci_neg
    del df_sci_pos
    gc.collect()
    data['diff_days'] = data['diff_days'].abs()

    data = data.sample(frac=1, random_state=42).reset_index(drop=True)
    grouped = data.groupby('inventor').ngroup()
    features = ['app_i', 'app_s', 'inventor_i', 'ipc_c', 'ipc_g', 'title', 'keyword1', 'keyword2', 'address_s', 'geo',
                'citing_rp', 'diff_days']
    X = data[features]
    y = data['label']
    del data
    gc.collect()

    gkf = GroupKFold(n_splits=5)
    params = {'max_depth': 3, 'eta': 0.3, 'objective': 'binary:logistic', 'eval_metric': 'auc'}
    scores = []

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(xgb_train_sci, train_index, test_index, X, y) for train_index, test_index in
                   gkf.split(X, y, groups=grouped)]
        for future in futures:
            try:
                score = future.result()
                scores.append(score)
            except ValueError as e:
                print(f"Error calculating score: {e}")

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(xgb_train_rare, train_index, test_index, X, y) for train_index, test_index in
                   gkf.split(X, y, groups=grouped)]
        for future in futures:
            try:
                score = future.result()
                scores.append(score)
            except ValueError as e:
                print(f"Error calculating score: {e}")

    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(xgb_train_mix, train_index, test_index, X, y) for train_index, test_index in
                   gkf.split(X, y, groups=grouped)]
        for future in futures:
            try:
                score = future.result()
                scores.append(score)
            except ValueError as e:
                print(f"Error calculating score: {e}")
