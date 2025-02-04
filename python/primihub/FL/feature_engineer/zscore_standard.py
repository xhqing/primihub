import numpy as np
import pandas as pd
from os import path


class ZscoreStandard():
    def __init__(self):
        self.mean = 0
        self.std = 0
        self.dev = 0
        self.num = 0

    def _check_data(self, np_data):
        if isinstance(np_data, np.ndarray):
            if len(np_data.shape) == 1:
                return np.reshape(np_data, (-1, 1))
            elif len(np_data.shape) > 2:
                raise ValueError("numpy data array shape should be 2-D")
            else:
                return np_data
        elif isinstance(np_data, pd.DataFrame):
            return np.array(np_data)
        else:
            raise ValueError("data should be numpy data array")

    def _check_idxs(self, idxs):
        if isinstance(idxs, int):
            return [idxs, ]
        elif isinstance(idxs, (tuple, list)):
            idxs = list(idxs)
            idxs.sort()
            return idxs
        else:
            raise ValueError("idxs may be int | list | tuple")

    def _fit(self, data, idxs):
        self.mean = np.mean(data[:, idxs].astype(float), axis=0)
        self.std = np.std(data[:, idxs].astype(float), axis=0)
        self.dev = np.power(self.std, 2)
        self.num = data.shape[0]
        return self.mean, self.std

    def __call__(self, data, idxs):
        data = self._check_data(data)
        idxs = self._check_idxs(idxs)
        self._fit(data, idxs)
        data[:, idxs] = (data[:, idxs] - self.mean) / self.std
        return data


class HorZscoreStandard(ZscoreStandard):
    def __init__(self):
        super().__init__()
        self.union_flag = False

    def stat_union(self, other_stats):
        num_client = len(other_stats) + 1
        ratio_list = np.zeros(num_client)
        ratio_list[0] = self.num
        for i, (_, _, num) in enumerate(other_stats):
            ratio_list[i+1] = num
        sum_num = np.sum(ratio_list)
        ratio_list /= sum_num

        self.mean = self.mean * ratio_list[0]
        self.dev = self.dev * ratio_list[0]
        for i, (mean, std, _) in enumerate(other_stats):
            self.mean += mean * ratio_list[i+1]
            self.dev += np.power(std, 2) * ratio_list[i+1]
        self.std = np.sqrt(self.dev)
        self.union_flag = True

    def fit(self, data, idxs):
        data = self._check_data(data)
        idxs = self._check_idxs(idxs)
        mean, std = self._fit(data, idxs)
        return mean, std, data.shape[0]

    def __call__(self, data, idxs):
        if self.union_flag == False:
            raise ValueError("horizontal standard must do after stat_union")
        data[:, idxs] = (data[:, idxs] - self.mean) / self.std
        return data
