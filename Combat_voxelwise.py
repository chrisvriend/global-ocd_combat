#!/usr/bin/env python3


"""
C.Vriend - Amsterdam UMC - Aug 2024
Combat-GAM of voxel MRI images using neuroHarmonize 
the script assumes that each subject has its own 3D niftii file and that each file 
has the format: sub-[SUBJID][optionaltags].nii.gz
e.g. sub-1001.nii.gz or sub-1001_space-dtitk_AD.nii.gz
the sort order of the niftii files needs to be EXACTLY the same as the order in the 
demographic file (demo_clin_vars.tsv) and the no. of files needs to be consistent with 
the no. rows.

if you are working with 4D images (because the stat images are merged together from the whole sample )
you first need to split them to get subject-specific 3D images using for example 'fslsplit'
you can subsequently merge the ComBat corrected images back together using fslmerge -t, 
e.g. fslmerge -t combatcorrected_4d.nii.gz *CBadj.nii.gz



see also : https://github.com/rpomponio/neuroHarmonize



"""
import pandas as pd
import numpy as np
import os
import neuroHarmonize as nh
from neuroHarmonize.harmonizationNIFTI import createMaskNIFTI
from neuroHarmonize.harmonizationNIFTI import flattenNIFTIs
from neuroHarmonize.harmonizationNIFTI import applyModelNIFTIs


# specify directories
mridir='/home/anw/cvriend/my-scratch/combattest/mri'
clindir='/home/anw/cvriend/my-scratch/combattest/clin'

# Specifying the site variable as well as all covariates to preserve in df_clin
# (change names and/or add delete rows)
#example:
# neuroHarmonize requires the site variable to be written as SITE
df_clin=pd.read_csv(os.path.join(clindir,'demo_clin_vars.tsv'),sep='\t',index_col=['subj'])
covars= pd.DataFrame({'SITE':df_clin['site'].tolist(),
                      'sex':df_clin['sex'].tolist(),
                      'diagnosis':df_clin['Dx'].tolist(),
                      'age':df_clin['age'].tolist(),
                      'edu':df_clin['edu'].tolist()})

# find the nii files
os.chdir(mridir)
nii_files = [niifile for niifile in os.listdir(mridir)
              if  'sub-' in niifile and niifile.endswith('.nii.gz')  ]

# sort the list and save to dataframe
nii_files.sort()
nii_list=pd.DataFrame({'PATH':nii_files})


# check if no. images is equal to number of rows in demographic file
if not nii_list.shape[0] == covars.shape[0]:
    raise Exception('the number of nifti images and rows in demographic file are unequal')


### NIFTI ComBat-GAM ###
# Load nifti path lists
print('\n%d NIFTI files to be processed' % (nii_list.shape[0]))

# create common mask across all nifti images 
nifti_avg, nifti_mask, affine, hdr0 = createMaskNIFTI(nii_list, threshold=0)

# Flatten the images to a 2D numpy.array
nii_array = flattenNIFTIs(nii_list, 'thresholded_mask.nii.gz')

# Pass the 2D array to neuroHarmonize.harmonizationLearn
effect_model, effect_array_adj = nh.harmonizationLearn(nii_array, covars)

# Apply the model sequentially to images one-by-one and saving the results as NIFTIs
nii_list['PATH_NEW'] = nii_list['PATH'].str.replace('.nii.gz', '_CBadj.nii.gz')
applyModelNIFTIs(covars, effect_model, nii_list, 'thresholded_mask.nii.gz'
