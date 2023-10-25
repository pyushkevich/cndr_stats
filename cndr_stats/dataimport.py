import pandas as pd
import numpy as np

# Rules for reading InQuery fields and assigning to types
inquery_types = {
    'INDDID': str, 
    'FlywheelSessionDate': np.datetime64,
    'AutopsyDate': np.datetime64
}

def semiq_scores_to_numeric(df):
    
    # All the columns for a given region
    measures = [ 'Tau', 'ThioPlaques', 'AntibodyPlaques', 'aSyn', 'Ubiquitin', 
                'Gliosis', 'NeuronLoss', 'TDP43', 'Other', 'Update' ]

    # Find all the columns with regional pathology scores
    regions = [ 'Amyg', 'DG', 'CS', 'EC', 'MF', 'Ang', 'SMT', 'Cing', 'OC',
                'Neocortical', 'CP', 'GP', 'TS', 'Subcortical', 'MB', 'SN',
                'Pons', 'LC', 'Med', 'CB', 'SC', 'Brainstem', 'MC', 'OFC']
    
    # Cross product of these lists
    cols_semiq = [x + y for x in regions for y in measures ]

    # Conversion rules
    repl_semiq = { 'Rare': 0.5, '2+': 2.0, '3+': 3.0, '1+': 1.0, '0': 0.0, 
                  'Presumed 0': 0.0, 'Not Avail': np.nan, 'Not Done': np.nan, 
                  'Not Available': np.nan }

    # Apply the replacements
    return df.replace({x: repl_semiq for x in cols_semiq})


def merge_braak_stages(df):

    # Compute combined Braak stage
    if 'Braak06' in df and 'Braak03' in df:
        df['BraakMrg'] = np.nanmean(np.stack([
            np.ceil(df['Braak06'].replace({'Unknown': np.nan}).astype('float32') * 0.5),
            df['Braak03'].replace({'Unknown': np.nan}).astype('float32')], axis=1), axis=1)
    
    return df


def read_excel(filename, **kwargs):
    return pd.read_excel(filename, dtype=inquery_types)


def read_csv(filename, **kwargs):
    return pd.read_csv(filename, dtype=inquery_types)


def clean_cndr_dataset(df)
    """
    Apply default cleaning routines to a CNDR inquery dataframe.
    Includes making regional semi-quantitative scores numeric, merging Braak 3 and Braak 6 scores.
    """
    df = semiq_scores_to_numeric(df)
    df = merge_braak_stages(df)


def add_diagnostic_categories(df):
    """
    Add diagnostic categories to a CNDR InQuery dataframe. The diagnostic categories
    are based on the processing of NPDX fields and include the following categories,
    taking values 0 and 1

    is_any_diag_ad:          Has diagnosis of AD as primary, secondary, etc.
    is_any_diag_nadt_ftld:   Has diagnosis of non-AD tauopathy or FTLD as primary, secondary, etc.
    is_any_diag_late:        Has diagnosis of LATE-NC as primary, secondary, etc.
    is_clean_ad:             Has AD diagnosis and does not have non-AD tauopathy or FTLD
    is_clean_ad_cont:        Does not have non-AD tauopathy or FTLD
    is_clean_late_ad:        Has LATE and AD diagnoses and does not have non-AD tauopathy or FTLD
    is_clean_late_ad_cont:   Has LATE diagnosis and does not have non-AD tauopathy or FTLD
    is_robin_eligible        Meets criteria for the 2020 DeFlores paper

    Also adds the following variables:

    ADNC_severity:           Severity of ADNC, 0:none, 1:low, 2:intermediate, 3:high or NaN
    LATE_stage:              Stage of LATE-NC, 0:none, 1:amygdala, 2:mtl or NaN
    """
    # This variable is true if any one of the NPDx values is AD
    is_any_diag_ad = (df[['NPDx1','NPDx2','NPDx3','NPDx4']]=="Alzheimer's disease").any(axis=1)

    # This variable is true if the primary diagnosis is a non-AD tauopathy
    is_first_diag_nadt = df['NPDx1'].isin([
        'Argyrophilic grain disease', 
        'Corticobasal degeneration', 
        'Globular glial tauopathy', 
        'Progressive supranuclear palsy',
        'Tauopathy unclassifiable',
        'Other'])

    # This variable is true if any of the diagnoses is a non-AD tauopathy or FTLD (for a clean AD/LATE comparison)
    is_any_diag_nadt_ftld = df[['NPDx1','NPDx2','NPDx3','NPDx4']].isin([
        'Amyotrophic lateral sclerosis',
        'Amyotrophic lateral sclerosis - Other',
        'Argyrophilic grain disease',
        'Chronic Traumatic Encephalopathy',
        'Corticobasal degeneration',
        'Frontotemporal dementia with parkinsonism linked to chromosome 17',
        'Frontotemporal lobar degeneration with TDP inclusions (Also known as FTLD-TDP)',
        'Globular glial tauopathy',
        'Multiple system atrophy',
        "Pick's disease",
        'Progressive supranuclear palsy',
        'Tauopathy unclassifiable',
        'Other']).any(axis=1)

    # Include a flag to indicate if patients have LATE
    is_any_diag_late = (df[['NPDx1','NPDx2','NPDx3','NPDx4']]=="Limbic-predominant Age-related TDP-43 Encephalopathy (Also known as LATE)").any(axis=1)

    # Is the subject eligible based on Robin's selection criteria
    is_robin_eligible = is_any_diag_ad & (-is_first_diag_nadt)

    # Is the subject eligible based on more stringent criteria we typically use 
    is_ad = is_any_diag_ad & (-is_any_diag_nadt_ftld)

    # Is the subject on the AD continuum without weird co-pathologies 
    is_ad_cont = -is_any_diag_nadt_ftld

    # Determine if this subject has low, intermediate, or high ADNC
    if 'ABeta' in df and 'BraakMrg' in df and 'CERAD' in df:
        df['ADNC_severity'] = 0
        df.loc[df.ABeta.isnull(),'ADNC_severity'] = np.nan
        df.loc[df.BraakMrg.isnull(),'ADNC_severity'] = np.nan
        df.loc[df.CERAD.isnull(),'ADNC_severity'] = np.nan
        df.loc[df.ABeta > 0.5,'ADNC_severity'] = 1.0
        df.loc[(df.BraakMrg > 1.5) & (df.ABeta > 1.5),'ADNC_severity'] = 2.0
        df.loc[(df.BraakMrg > 1.5) & (df.ABeta > 0.5) & (df.CERAD > 1.5),'ADNC_severity'] = 2.0
        df.loc[(df.BraakMrg > 2.5) & (df.ABeta > 2.5) & (df.CERAD > 1.5),'ADNC_severity'] = 3.0

    # Is the subject an eligible AD subject with late
    is_late_ad = is_ad & is_any_diag_late
    is_late_ad_cont = is_ad_cont & is_any_diag_late

    # Determine LATE stage
    if 'CSTDP43' in df and 'DGTDP43' in df and 'ECTDP43' in df:
        mtl_tdp = (df.CSTDP43 + df.DGTDP43 + df.ECTDP43) / 3.0
        df['LATE_stage'] = 0.0
        df.loc[is_any_diag_late, 'LATE_stage'] = 1.0
        df.loc[is_any_diag_late & mtl_tdp > 0, 'LATE_stage'] = 2.0

    df['is_any_diag_ad'] = is_any_diag_ad.replace({True: 1, False: 0})
    df['is_any_diag_nadt_ftld'] = is_any_diag_nadt_ftld.replace({True: 1, False: 0})
    df['is_any_diag_late'] = is_any_diag_late.replace({True: 1, False: 0})
    df['is_robin_eligible'] = is_robin_eligible.replace({True: 1, False: 0})
    df['is_clean_ad'] = is_ad.replace({True: 1, False: 0})
    df['is_clean_ad_cont'] = is_ad_cont.replace({True: 1, False: 0})
    df['is_clean_late_ad'] = is_late_ad
    df['is_clean_late_ad_cont'] = is_late_ad_cont

    return df
