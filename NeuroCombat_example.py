#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script to run NeuroCombat on numerical(!) imaging data. This can be morphometric (e.g. thickness, volume),
diffusivity, graph or other data.

@author: Chris Vriend - c.vriend <at> amsterdamumc <dot> nl

"""

import os
import pandas as pd
from neuroCombat import neuroCombat

# specify directories
mridir='/home/anw/cvriend/my-scratch/global-ocd/mri'
clindir='/home/anw/cvriend/my-scratch/global-ocd/clin'

##################
##   load data  ## 
##################
# make sure the two files have the same index name (e.g. subj)), the same number of participants and sorted in the same order

# dataframe with mri measures with each row a different participant, a column with the subject ids and every next column a different measure, e.g. volume ROI 1, volume ROI 2, etc.
# assumes that data is saved in a csv file
df_mri=pd.read_csv(os.path.join(mridir,'imagingmeasures.tsv'),index_col=['subj'])
# dataframe with demographic and clinical data with each row a different participant and every column a different measure
#, e.g. age, sex, education, from the same sample
# this dataframe should also contain the site variable!
df_clin=pd.read_csv(os.path.join(clindir,'demo_clin_vars.tsv'),index_col=['subj'])

# optional in case files do not match, filter rows
#df_mri = df_mri.loc[df_mri.index.isin(df_clin.index)]


#####################
##   NeuroCombat  ## 
#####################
# from https://github.com/Jfortin1/neuroCombat/tree/ac82a067412078680973ddf72bd634d51deae735

# Specifying the site variable as well as all covariates to preserve in df_clin
# in case of structural T1w Surface Area or volume also add ICV!
# (change names and/or add delete rows)
#example:
covars= pd.DataFrame({'site':df_clin['site'].tolist(),
                      'sex':df_clin['sex'].tolist(),
                      'diagnosis':df_clin['diagnosis'].tolist(),
                      'age':df_clin['age'].tolist(),
                      'TOLrt':df_clin['TOLrt'].tolist(),
                      'edu':df_clin['edu'].tolist()})

    
# specify the name of the variable that encodes for the scanner/batch covariate:
site_col = 'site'
# specify names of the variables that are categorical
categorical_cols = ['sex','diagnosis']
# specify names of the variables that are continuous
continuous_cols=['age','edu','TOLsc']


## run ComBat ##
df_combat=pd.DataFrame(neuroCombat(dat=df_mri.T.values,
                                covars=covars,
                                categorical_cols=categorical_cols,
                                continuous_cols=continuous_cols,   
                                batch_col=site_col)['data'],
                   index=df_mri.columns)
df_combat.columns=df_mri.index


# transpose back to original 
df_combat=df_combat.T


# (optional) add demographic variables and Dx and ICV 
#df_combat=df_combat.join(df_clin)

# save 
df_combat.to_csv(os.path.join(mridir,('imagingmeasures_combat' + '.csv')))

