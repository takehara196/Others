# !/usr/bin/env python
# -*- coding:utf-8 -*-

from unittest import result
from flask import Flask, request, jsonify, render_template
from flask import Response
from flask_cors import CORS
import numpy as np
import pandas as pd
import random
import datetime
import send2trash
import shutil

import pymysql
import sqlalchemy as sa

import os

random.seed(0)

import mysql.connector
from sklearn.cluster import KMeans

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.dialects.mysql import insert

AGENT_FILE_PATH = 'tables/agents.csv'
BUYER_FILE_PATH = 'tables/buyers.csv'

import mysql.connector

import datetime
from logger import set_logger

# パスやロガーの設定
INPUT_PATH = "input"
OUTPUT_PATH = "output"
LOG_PATH = f"log/{datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')}"
today_str = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d_%H:%M:%S')
os.makedirs(LOG_PATH, exist_ok=True)
logger = set_logger(__name__, today_str, LOG_PATH)


def conn():
    # コネクションの作成
    con = mysql.connector.connect(
        host='localhost',
        port='4306',
        user='root',
        password='',
        database='app_development'
    )
    con.ping(reconnect=True)
    return con


def select_buyers_table(con):
    logger.info("*** select_buyers_table ***")
    cur = con.cursor()
    cur.execute('SELECT * FROM buyers;')
    buyers = cur.fetchall()
    buyer_df = pd.DataFrame(buyers)

    cur.execute('SHOW COLUMNS FROM buyers;')
    buyers_cols = cur.fetchall()
    cols = pd.DataFrame(buyers_cols)[[0]].T.iloc[0].to_list()
    buyer_df.columns = cols
    return buyer_df


def select_agents_table(con):
    logger.info("*** select_agents_table ***")
    cur = con.cursor()
    cur.execute('SELECT * FROM agents;')
    agents = cur.fetchall()
    agent_df = pd.DataFrame(agents)

    cur.execute('SHOW COLUMNS FROM agents;')
    agents_cols = cur.fetchall()
    cols = pd.DataFrame(agents_cols)[[0]].T.iloc[0].to_list()
    agent_df.columns = cols
    return agent_df


def make_distances_table():
    logger.info("*** make_distances_table ***")
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


def delete_log():
    try:
        """
        古いlogディレクトリの削除
        (90日以上経過したlogディレクトリを削除)
        """
        # 現在の日付を取得
        now = datetime.date.today()
        path = './log'
        files = os.listdir(path)
        files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]
        for dir in files_dir:
            mtime = datetime.date.fromtimestamp(int(os.path.getmtime(f'{path}/{dir}')))
            # 90日以上経過している場合は削除
            if (now - mtime).days >= 90:
                # ディレクトリを中身ごと削除
                shutil.rmtree(f'{path}/{dir}')
                logger.info(f"*** delete log directory {str(dir)} ***")
    except:
        pass
    return


def main():
    delete_log()
    con = conn()
    buyer_df = select_buyers_table(con)
    agent_df = select_agents_table(con)
    # agent_df, buyer_df = read_csv()

    '''tmp_id列の作成
    '''
    # テーブル名からagent, buyerを判別する
    agent_df['agent_id'] = agent_df['id'].astype('str')
    buyer_df['buyer_id'] = buyer_df['id'].astype('str')

    # 結合
    df = pd.concat([buyer_df, agent_df], axis=0, join='outer')

    '''クラスタリング
    '''
    # クラスタリングに使用するカラム
    clustering_use_cols = [
        'id',
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

    # agent, buyerカラム: agents, buyersテーブルのcluster列更新の為に使用
    agent_buyer_id_cols = [
        'agent_id',
        'buyer_id'
    ]
    # agent, buyerカラムのデータフレーム
    agent_buyer_id_df = df[agent_buyer_id_cols].reset_index(drop=True)

    '''クラスタリング
    '''
    # idカラムをindexに指定
    tmp_df = df[clustering_use_cols].set_index('id')
    # データを4クラスに分割、乱数固定
    model_kmeans = KMeans(n_clusters=4, random_state=0)
    # 学習, フィッティング <- preferenceカラムのみ使用する(agent_id, buyer_idを除いたカラムを使用する)
    model_kmeans.fit(tmp_df.values)
    # 学習済みデータの重心点
    # print(model_kmeans.cluster_centers_)
    # 重心点の形状
    # print(model_kmeans.cluster_centers_.shape)
    # 作成したモデルでクラスタリング
    cluster = model_kmeans.predict(tmp_df.values)
    cluster_df = tmp_df.copy()
    cluster_df['cluster'] = cluster

    # buyer, agentのpreferenceの回答の差の二乗の和の平方根
    buyer_preference_df = buyer_df[clustering_use_cols]
    agent_preference_df = agent_df[clustering_use_cols]

    # agent_id列, buyer_id列とcluster列を結合
    cluster = cluster_df[['cluster']].reset_index(drop=True)
    agent_buyer_cluster_df = pd.concat([agent_buyer_id_df, cluster], axis=1)

    buyer_id_df = agent_buyer_cluster_df.dropna(subset=['buyer_id']).drop('agent_id', axis=1).reset_index(drop=True)
    buyer_id_df.columns = ['id', 'cluster']
    agent_id_df = agent_buyer_cluster_df.dropna(subset=['agent_id']).drop('buyer_id', axis=1).reset_index(drop=True)
    agent_id_df.columns = ['id', 'cluster']
    buyer_id_df['id'] = buyer_id_df['id'].astype(np.int64)
    print(buyer_id_df)

    # buyers
    sql1 = ('''
            INSERT INTO buyers
                (id, cluster, created_at, updated_at) 
            VALUES
                (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
                cluster = VALUES(`cluster`);
            ''')

    for index, data in buyer_id_df.iterrows():
        cursor = con.cursor()
        param = (list(data)[0], list(data)[1])
        print(param)
        cursor.execute(sql1, param)
        con.commit()
        cursor.close()

    # agents
    sql2 = ('''
            INSERT INTO agents
                (id, cluster, created_at, updated_at) 
            VALUES
                (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
                cluster = VALUES(`cluster`);
            ''')

    for index, data in agent_id_df.iterrows():
        cursor = con.cursor()
        param = (list(data)[0], list(data)[1])
        print(param)
        cursor.execute(sql2, param)
        con.commit()
        # cursor.close()

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

    # buyer, agentのpreferenceの回答の差の二乗の和の平方根
    buyer_preference_df = buyer_df[clustering_use_cols]
    agent_preference_df = agent_df[clustering_use_cols]

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
    id_list = []
    id_ = 0
    for b_index, b_row in buyer_preference_df.iterrows():
        b = b_row[preference_cols]
        buyer_id = b_row[id_col]
        for a_index, a_row in agent_preference_df.iterrows():
            id_ += 1
            id_list.append(id_)
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
    id_df = pd.DataFrame(id_list)
    # print(id_df)

    distance_table_df = pd.concat([buyer_id_df, agent_id_df], axis=1)
    distance_table_df = pd.concat([distance_table_df, distance_df], axis=1)
    distance_table_df.columns = ['buyer_id', 'agent_id', 'distance']

    distance_table_df[['created_at', 'updated_at']] = ''
    distance_table_df[['id']] = id_df

    distance_table_df.to_csv('output/distances_table_df.csv', index=False)

    sql3 = ('''
            INSERT INTO distances
                (id, buyer_id, agent_id, distance, created_at, updated_at) 
            VALUES
                (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
            ON DUPLICATE KEY UPDATE
                distance = VALUES(distance),
                updated_at = VALUES(updated_at);
            ''')

    for index, data in distance_table_df.iterrows():
        cursor = con.cursor()
        param = (list(data)[5], list(data)[0], list(data)[1], list(data)[2])
        cursor.execute(sql3, param)
        con.commit()
        cursor.close()


if __name__ == '__main__':
    main()
