# !/usr/bin/env python
# -*- coding:utf-8 -*-

from unittest import result
from flask import Flask, request, jsonify, render_template
from flask import Response
from flask_cors import CORS
import pandas as pd
import random
import sqlalchemy as sa
import os

random.seed(0)

import mysql.connector
from sklearn.cluster import KMeans

AGENT_FILE_PATH = 'tables/agents.csv'
BUYER_FILE_PATH = 'tables/buyers.csv'

import mysql.connector

# コネクションの作成
conn = mysql.connector.connect(
    host='localhost',
    port='4306',
    user='root',
    password='',
    database='app_development'
)

conn.ping(reconnect=True)

cur = conn.cursor()
cur.execute('SELECT * FROM buyers')
sql_result_a = cur.fetchall()

print(sql_result_a)

def read_csv():
    agent_df = pd.read_csv(AGENT_FILE_PATH)
    buyer_df = pd.read_csv(BUYER_FILE_PATH)
    return agent_df, buyer_df


def make_distances_table():
    distances_table_cols = [
        'id',
        'buyer_id',
        'agent_id',
        'distance',
        'created_at',
        'updated_at'
    ]
    distances_df = pd.DataFrame(columns=distances_table_cols)

    return distances_df


def main():
    agent_df, buyer_df = read_csv()

    '''tmp_id列の作成
    '''
    # テーブル名からagent, buyerを判別する
    agent_file_name = os.path.splitext(os.path.basename(AGENT_FILE_PATH))[0]
    buyer_file_name = os.path.splitext(os.path.basename(BUYER_FILE_PATH))[0]
    # tmp_id列の作成
    # agent_df['agent_id'] = agent_file_name + '_' + agent_df['id'].astype('str')
    # buyer_df['buyer_id'] = buyer_file_name + '_' + buyer_df['id'].astype('str')
    agent_df['agent_id'] = agent_df['id'].astype('str')
    buyer_df['buyer_id'] = buyer_df['id'].astype('str')

    # 結合
    df = pd.concat([buyer_df, agent_df], axis=0, join='outer')
    # df.to_csv('output/df.csv')

    # アンケートカラムのみ抽出
    clustering_use_cols = [
        'id',
        # 'tmp_id',
        # 'agent_id',
        # 'buyer_id',
        'preference1',
        'preference2',
        'preference3',
        'preference4',
        'preference5',
        'preference6',
        'preference7',
        'preference8',
        'preference9'
    ]

    '''クラスタリング
    '''
    # idカラムをindexに指定
    tmp_df = df[clustering_use_cols].set_index('id')
    # データを4クラスに分割、乱数固定
    model_kmeans = KMeans(n_clusters=4, random_state=0)
    # 学習、フィッティング
    model_kmeans.fit(tmp_df.values)
    # 学習済みデータの重心点
    # print(model_kmeans.cluster_centers_)
    # 重心点の形状
    # print(model_kmeans.cluster_centers_.shape)
    # 作成したモデルでクラスタリング
    cluster = model_kmeans.predict(tmp_df.values)
    cluster_df = tmp_df.copy()
    cluster_df['cluster'] = cluster
    # print(cluster_df.reset_index())
    # print(cluster_df.reset_index()[['id', 'cluster']])

    '''距離による順位づけ
    '''
    distance_df = make_distances_table()
    # 次元削減によりtmp_id毎の位置算出
    # print(distance_df)

    distances_table_cols = [
        'id',
        'buyer_id',
        'agent_id',
        'distance',
        'created_at',
        'updated_at'
    ]

    # distance列を0で初期化
    df['distance'] = 0
    df[distances_table_cols].to_csv('output/distance_table_df.csv', index=False)

    # buyer, agentのpreferenceの回答の差の二乗の和の平方根
    buyer_preference_df = buyer_df[clustering_use_cols]
    agent_preference_df = agent_df[clustering_use_cols]

    # print(buyer_preference_df)

    # アンケートカラム
    preference_cols = [
        'preference1',
        'preference2',
        'preference3',
        'preference4',
        'preference5',
        'preference6',
        'preference7',
        'preference8',
        'preference9'
    ]

    id_col = [
        'id'
    ]

    buyer_id_list = []
    agent_id_list = []
    distance_list = []
    for b_index, b_row in buyer_preference_df.iterrows():
        b = b_row[preference_cols]
        buyer_id = b_row[id_col]
        for a_index, a_row in agent_preference_df.iterrows():
            a = a_row[preference_cols]
            agent_id = a_row[id_col]
            tmp_df = pd.concat([b, a], axis=1)
            # distance列の作成
            tmp_df.columns = ['', 'distance']
            # 差: b-a
            tmp_diff_df = tmp_df.diff(axis=1)
            # 二乗: (b-a)^2
            tmp_diff_square_df = tmp_diff_df ** 2
            # 和: ((b-a)^2).sum()
            tmp_diff_square_sum_df = tmp_diff_square_df.sum()
            # 平方根: sqrt(((b-a)^2).sum())
            tmp_diff_square_sum_sqrt_df = tmp_diff_square_sum_df ** 0.5
            # buyer_id, agent_id, distance_listリスト作成
            buyer_id_list.append(buyer_id[0])
            agent_id_list.append(agent_id[0])
            distance_list.append(tmp_diff_square_sum_sqrt_df['distance'])
    buyer_id_df = pd.DataFrame(buyer_id_list)
    agent_id_df = pd.DataFrame(agent_id_list)
    distance_df = pd.DataFrame(distance_list)

    distance_table_df = pd.concat([buyer_id_df, agent_id_df], axis=1)
    distance_table_df = pd.concat([distance_table_df, distance_df], axis=1)
    distance_table_df.columns = ['buyer_id', 'agent_id', 'distance']

    distance_table_df[['created_at', 'updated_at']] = ''

    distance_table_df.to_csv('output/distances_table_df.csv', index=False)


if __name__ == '__main__':
    main()
