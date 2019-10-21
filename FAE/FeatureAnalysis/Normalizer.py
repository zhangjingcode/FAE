import numpy as np
import os
from abc import abstractmethod
import pandas as pd
from copy import deepcopy

class Normalizer:
    def __init__(self):
        self._slop = np.array([])
        self._interception = np.array([])

    def Transform(self, data_container):
        new_data_container = deepcopy(data_container)
        array = data_container.GetArray()

        invariability_position = np.where(self._slop == 0)
        if invariability_position :
            array = np.delete(array, invariability_position, axis=1)
            self._slop = np.delete(self._slop, invariability_position, axis=0)
            self._interception = np.delete(self._interception, invariability_position, axis=0)

            feature_name_list = data_container.GetFeatureName()

            invariability_feature_name = [feature_name_list[index] for index in
                                      [index for index in invariability_position[0]]]

            feature_name_list = [index for index in feature_name_list if index not in invariability_feature_name]
            new_data_container.SetFeatureName(feature_name_list)

        array -= self._interception
        array /= self._slop
        array = np.nan_to_num(array)
        new_data_container.SetArray(array)
        new_data_container.UpdateFrameByData()
        return new_data_container

    def Save(self, store_path):
        df = pd.DataFrame({'slop':self._slop, 'interception':self._interception})
        df.to_csv(store_path)

    def Load(self, file_path):
        df = pd.read_csv(file_path)
        self._slop = np.array(df['slop'])
        self._interception = np.array(df['interception'])

    @abstractmethod
    def Run(self, data_container, store_folder, is_test=False):
        pass

    def GetName(self):
        pass

class NormalizerNone(Normalizer):
    def __init__(self):
        super(NormalizerNone, self).__init__()

    def GetName(self):
        return 'NormNone'

    def Run(self, data_container, store_folder='', is_test=False):
        self._slop = np.ones((len(data_container.GetFeatureName()),))
        self._interception = np.zeros((len(data_container.GetFeatureName()),))
        if store_folder:
            store_path = os.path.join(store_folder, 'non_normalized_feature.csv')
            data_container.Save(store_path)

            self.Save(store_path=os.path.join(store_folder, 'non_normalization.csv'))

        return data_container

    def GetDescription(self):
        text = "We did not apply any normalization method on the feature matrix. "
        return text

class NormalizerUnit(Normalizer):
    def __init__(self):
        super(NormalizerUnit, self).__init__()

    def GetName(self):
        return 'NormUnit'

    def Run(self, data_container, store_folder='', is_test=False):
        array = data_container.GetArray()
        if is_test:
            self.Load(os.path.join(store_folder, 'unit_normalization_training.csv'))
        else:
            self._slop = np.sum(np.square(array), axis=0)
            self._interception = np.zeros_like(self._slop)

        data_container = self.Transform(data_container)
        if store_folder:
            if not is_test:
                data_container.Save(os.path.join(store_folder, 'unit_normalized_training_feature.csv'))
                self.Save(store_path=os.path.join(store_folder, 'unit_normalization_training.csv'))
            else:
                data_container.Save(os.path.join(store_folder, 'unit_normalized_testing_feature.csv'))
        return data_container

    def GetDescription(self):
        text = "We applied the normalization on the feature matrix. For each feature vector, we calculated the L2 norm " \
               "and divided by it. Then the feature vector was mapped to an unit vector. "
        return text

class NormalizerZeroCenter(Normalizer):
    def __init__(self):
        super(NormalizerZeroCenter, self).__init__()

    def GetName(self):
        return 'Norm0Center'

    def Run(self, data_container, store_folder='', is_test=False):
        array = data_container.GetArray()
        if is_test:
            self.Load(os.path.join(store_folder, 'zero_center_normalization_training.csv'))
        else:
            self._slop = np.std(array, axis=0)
            self._interception = np.mean(array, axis=0)

        data_container = self.Transform(data_container)
        if store_folder:
            if not is_test:
                data_container.Save(os.path.join(store_folder, 'zero_center_normalized_training_feature.csv'))
                self.Save(store_path=os.path.join(store_folder, 'zero_center_normalization_training.csv'))
            else:
                data_container.Save(os.path.join(store_folder, 'zero_center_normalized_testing_feature.csv'))
        return data_container

    def GetDescription(self):
        text = "We applied the normalization on the feature matrix. For each feature vector, we calculated the mean " \
               "value and the standard deviation. Each feature vector was subtracted by the mean value and was divided " \
               "by the standard deviation. After normalization process, each vector has zero center and unit standard " \
               "deviation. "
        return text

class NormalizerZeroCenterAndUnit(Normalizer):
    def __init__(self):
        super(NormalizerZeroCenterAndUnit, self).__init__()

    def GetName(self):
        return 'Norm0CenterUnit'

    def Run(self, data_container, store_folder='', is_test=False):
        array = data_container.GetArray()
        if is_test:
            self.Load(os.path.join(store_folder, 'zero_center_unit_normalization_training.csv'))
        else:
            self._slop = np.sum(np.square(array), axis=0)
            self._interception = np.mean(array, axis=0)

        data_container = self.Transform(data_container)
        if store_folder:
            if not is_test:
                data_container.Save(os.path.join(store_folder, 'zero_center_unit_training_feature.csv'))
                self.Save(store_path=os.path.join(store_folder, 'zero_center_unit_normalization_training.csv'))
            else:
                data_container.Save(os.path.join(store_folder, 'zero_center_unit_normalized_testing_feature.csv'))
        return data_container

    def GetDescription(self):
        text = "We applied the normalization on the feature matrix.  Each feature vector was subtracted by the mean " \
               "value of the vector and was divided by the length of it. "
        return text

if __name__ == '__main__':
    from FAE.DataContainer.DataContainer import DataContainer

    data_container = DataContainer()
    file_path = os.path.abspath(r'..\..\Example\numeric_feature.csv')
    print(file_path)
    data_container.Load(file_path)

    normalizer = NormalizerZeroCenterAndUnit()
    normalizer.Run(data_container, store_folder=r'..\..\Example\one_pipeline')