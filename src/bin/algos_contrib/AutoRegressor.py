#!/usr/bin/env python

import requests
import uuid
import base64
import json
import time
import pandas as pd

import StringIO

from base import RegressorMixin, BaseAlgo
from codec import codecs_manager

PORT = 8001
HOST = 'localhost'
URL_BASE = 'http://{}:{}'.format(HOST, PORT)


class AutoRegressor(RegressorMixin, BaseAlgo):
    def __init__(self, options):
        self.handle_options(options)
        self.params = options.get('params', {})

    def fit(self, df, options):
        csv_data = df.to_csv(index=False)

        self.fit_data_id = "data" + str(uuid.uuid4())
        payload = {}
        payload['id'] = self.fit_data_id
        payload['name'] = self.fit_data_id
        payload['payload'] = base64.b64encode(csv_data)
        payload['description'] = 'fit data from splunk'

        headers = {'Content-Type': 'application/json'}

        # add dataset
        requests.post('{}/api/datasets'.format(URL_BASE),
                      data=json.dumps(payload), headers=headers)

        # train
        job_payload = {
            "name": "autoregressor",
            "type": "AutoRegressionJob",
            "dataset": self.fit_data_id,
            "features": options['feature_variables'],
            "targets": options['target_variable'],
            "job_option": {},
            "validation_option": {}
        }

        train_rsp = requests.post('{}/api/ml_jobs'.format(URL_BASE),
                                  data=json.dumps(job_payload), headers=headers)

        train_rsp = json.loads(train_rsp.text)
        self.job_id = train_rsp['id']

        while True:
            status_rsp = requests.get(
                '{}/api/ml_jobs/{}'.format(URL_BASE, self.job_id), headers=headers)
            status_rsp = json.loads(status_rsp.text)
            status = status_rsp['status']
            if status in ['SUCCESS', 'FAILED']:
                break
            time.sleep(3)

        if status == 'SUCCESS':
            self.summary = status_rsp['model_representation']

        # delete dataset
        requests.delete(
            '{}/api/datasets/{}'.format(URL_BASE, self.fit_data_id), headers=headers)

    def apply(self, df, options):
        csv_data = df.to_csv(index=False)
        payload = {}
        payload['data'] = base64.b64encode(csv_data)
        payload['input_type'] = 'csv'
        headers = {'Content-Type': 'application/json'}

        # add dataset
        predict_rsp = requests.post('{}/api/ml_jobs/{}/predict'.format(URL_BASE, self.job_id),
                                    data=json.dumps(payload), headers=headers)

        predict_rsp = json.loads(predict_rsp.text)
        predict_result = base64.b64decode(predict_rsp['data'])

        csv_data = StringIO.StringIO(predict_result)
        pred_df = pd.read_csv(csv_data)

        '''
        col = options['target_variable'] + \
            options['feature_variables'] + ['prediction']
        pred_df = pred_df[col]
        '''

        return pred_df

    def summary(self, options):
        df = pd.DataFrame({
            'summary': [self.summary],
        })
        return df

    @staticmethod
    def register_codecs():
        from codec.codecs import SimpleObjectCodec
        codecs_manager.add_codec(
            'algos_contrib.AutoRegressor', 'AutoRegressor', SimpleObjectCodec)
