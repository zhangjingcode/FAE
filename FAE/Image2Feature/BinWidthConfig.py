import collections
import warnings
import os

import csv
import copy
import glob
import numpy as np
import SimpleITK as sitk
import matplotlib.pyplot as plt

class BinGenerator:
    def __init__(self, bin_count=2, binvmin='', binvmax='', binvmin_roi='', binvmax_roi=''):

        self.bin_count = bin_count

        self._binvmin = binvmin
        self._binvmax = binvmax

        self._binvmin_roi = binvmin_roi
        self._binvmax_roi = binvmax_roi

    def Load(self, nii_path, mask_path):
        self._nii_path = nii_path
        self._mask_path = mask_path
        self.image_array = sitk.GetArrayFromImage(sitk.ReadImage(self._nii_path))
        self.roi_array = sitk.GetArrayFromImage(sitk.ReadImage(self._mask_path))
        self.voxel_list = collections.Counter(self.roi_array.flatten())


        if len(self.voxel_list) > 2:
            warnings.warn('Here are not binary roi: ' + str(self.voxel_list))
        else:
            if 1 not in self.voxel_list or 0 not in self.voxel_list:
                warnings.warn('Here are voxels except 0 or 1 in the roi: ' + str(self.voxel_list))

        self.voxel_in_roi = self.image_array[np.where(self.roi_array == 1)]

        if self._binvmin == '':
            self._binvmin = np.min(self.image_array)

        if self._binvmax == '':
            self._binvmin = np.max(self.image_array)

        if self._binvmin_roi == '':
            self._binvmin_roi = np.min(self.voxel_in_roi)

        if self._binvmax_roi == '':
            self._binvmax_roi = np.max(self.voxel_in_roi)


    def Generate(self, is_show=True):
        self._start_roi = self._binvmin_roi
        self._end_roi = self._binvmax_roi

        self._steps = (self._end_roi - self._start_roi) / self.bin_count

        self._range = np.arange(self._start_roi, self._end_roi, self._steps)

        if is_show:
            plt.style.use('ggplot')
            plt.title('In ROI')

            n, bins, patches = plt.hist(self.voxel_in_roi, normed=0)
            if self._binvmin_roi != '' and self._binvmax_roi != '':
                plt.plot([self._binvmin_roi, self._binvmin_roi], [0, np.max(n)], color='black', linewidth=3, linestyle="-")
                plt.plot([self._binvmax_roi, self._binvmax_roi], [0, np.max(n)], color='black', linewidth=3, linestyle="-")

            for range_index in self._range:
                # x_list = [range_index] * int(np.max(n))
                # y_list = list(np.arange(0, int(np.max(n)), 1))

                x_list = [range_index, range_index]
                y_list = [0, np.max(n)]
                plt.plot(x_list, y_list, '--', linewidth=1, color='blue')

            plt.show()


def main():
    bin_generator = BinGenerator(bin_count=4, binvmin_roi=10, binvmax_roi=45)
    bin_generator.Load(nii_path=r'D:\hospital\BreastCancer\demo\A001_CHEN HAN YING\t1_14.3s.nii',
                       mask_path=r'D:\hospital\BreastCancer\demo\A001_CHEN HAN YING\roi3D.nii',)
    bin_generator.Generate()



if __name__ == '__main__':
    main()
