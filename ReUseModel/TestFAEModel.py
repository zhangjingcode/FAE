
import os
import csv
import numpy as np
from FAE.FeatureAnalysis.Normalizer import Normalizer
from FAE.DataContainer.DataContainer import DataContainer
from FAE.FeatureAnalysis.Classifier import Classifier
from FAE.Func.Metric import EstimateMetirc
from FAE.FeatureAnalysis.FeatureSelector import FeatureSelector
from FAE.FeatureAnalysis.CrossValidation import CrossValidation
def LoadTrainInfo(model_folder):

    train_info = {}
    ##Load normalizaiton

    normalizer = Normalizer()
    normalization_path = ''
    for sub_file in os.listdir(model_folder):
        if sub_file.rfind('_normalization_training.csv') != -1:
            normalization_path = os.path.join(model_folder, sub_file)

    if not os.path.exists(normalization_path):
        print('Check the normalization name : zero_center_normalization')
    else:
        normalizer.Load(normalization_path)

    train_info['normalizer'] = normalizer
    ## Load selected features

    selected_feature_path = os.path.join(model_folder, 'feature_select_info.csv')
    selected_feature_list = []
    with open(selected_feature_path, 'r', newline='') as f:
        f_reader = csv.reader(f)
        for index in f_reader:
            if index[0] == 'selected_feature':
                selected_feature_list = index[1:]
    if selected_feature_list == []:
        print('No selected features')

    train_info['selected_features'] = selected_feature_list

    ## Load FAE model

    classifier = Classifier()
    classifier.Load(model_folder)
    train_info['classifier'] = classifier

    return train_info

def TestNewData(NewDataCsv, model_folder, result_save_path=''):
    '''

    :param NewDataCsv: New radiomics feature matrix csv file path
    :param model_folder:The trained model path
    :return:classification result
    '''
    train_info = LoadTrainInfo(model_folder)
    new_data_container = DataContainer()

    #Normlization

    new_data_container.Load(NewDataCsv)

    feature_selector = FeatureSelector()
    feature_selector.SelectFeatureByName(new_data_container, train_info['selected_features'], is_replace=True)

    new_data_container = train_info['normalizer'].Transform(new_data_container)


    # data_frame = new_data_container.GetFrame()
    # data_frame = data_frame[train_info['selected_features']]
    # new_data_container.SetFrame(data_frame)
    # new_data_container.UpdateDataByFrame()




    ##Model
    train_info['classifier'].SetDataContainer(new_data_container)
    model = train_info['classifier'].GetModel()
    predict = model.predict_proba(new_data_container.GetArray())[:, 1]

    label = new_data_container.GetLabel()
    case_name = new_data_container.GetCaseName()



    test_result_info = [['CaseName', 'Pred', 'Label']]
    for index in range(len(label)):
        test_result_info.append([case_name[index], predict[index], label[index]])


    metric = EstimateMetirc(predict, label)
    info = {}
    info.update(metric)
    cv = CrossValidation()



    print(metric)
    print('\t')

    if result_save_path:

        info.update(metric)
        np.save(os.path.join(store_folder, 'test_predict.npy'), test_pred)
        np.save(os.path.join(store_folder, 'test_label.npy'), test_label)

        test_result_info = [['CaseName', 'Pred', 'Label']]
        for index in range(len(test_label)):
            test_result_info.append([test_case_name[index], test_pred[index], test_label[index]])
        with open(os.path.join(store_folder, 'test_info.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_result_info)

        cv.SaveResult(info, result_save_path)
        np.save(os.path.join(result_save_path, 'test_predict.npy'), predict)
        np.save(os.path.join(result_save_path, 'test_label.npy'), label)
        with open(os.path.join(result_save_path, 'test_info.csv'), 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(test_result_info)





    return metric


if __name__ == '__main__':

    TestNewData(r'D:\hospital\Huangli\smote\test_numeric_feature.csv',
            r'D:\hospital\Huangli\smote\process-result\Norm0Center_PCC_ANOVA_5_LR',
            r'D:\MyScript\demo')