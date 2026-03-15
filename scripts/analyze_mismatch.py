"""
Analyze Adult-only vs Child-only Hospital Mismatch in NIRD data.
Investigates if the mismatch is a root cause for referral delays in burn care.
"""
from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loading import load_clean_hospital_data

DATA_EXTERNAL = ROOT / "data" / "external"
OUTPUTS = ROOT / "outputs"

def analyze_mismatch():
    df = load_clean_hospital_data()
    
    print("=== NIRD Dataset Columns ===")
    print(df.columns.tolist())
    print(f"\nTotal facilities: {len(df)}")
    print("\n=== Sample of key capability flags ===")
    caps = ['STATE','TRAUMA_ADULT','TRAUMA_PEDS','BURN_ADULT','BURN_PEDS','TOTAL_BEDS','BURN_BEDS']
    available_cols = [c for c in caps if c in df.columns]
    print(df[available_cols].head(10).to_string())
    
    print("\n=== Value counts for capability flags ===")
    for col in ['TRAUMA_ADULT','TRAUMA_PEDS','BURN_ADULT','BURN_PEDS']:
        if col in df.columns:
            print(f"\n{col}:")
            print(df[col].value_counts(dropna=False))

    # --- Facility-level mismatch categories ---
    # For BURN capability mismatch
    if 'BURN_ADULT' in df.columns and 'BURN_PEDS' in df.columns:
        df['burn_adult'] = df['BURN_ADULT'].fillna(False).astype(bool)
        df['burn_peds'] = df['BURN_PEDS'].fillna(False).astype(bool)
        
        df['burn_category'] = 'Neither'
        df.loc[df['burn_adult'] & df['burn_peds'], 'burn_category'] = 'Both'
        df.loc[df['burn_adult'] & ~df['burn_peds'], 'burn_category'] = 'Adult-Only'
        df.loc[~df['burn_adult'] & df['burn_peds'], 'burn_category'] = 'Peds-Only'
        
        print("\n=== BURN Capability Mismatch at Facility Level ===")
        print(df['burn_category'].value_counts())
        print(f"\nAdult-Only Burn Centers: {(df['burn_category']=='Adult-Only').sum()}")
        print(f"Peds-Only Burn Centers: {(df['burn_category']=='Peds-Only').sum()}")
        print(f"Both (Adult+Peds) Burn Centers: {(df['burn_category']=='Both').sum()}")
        print(f"Neither: {(df['burn_category']=='Neither').sum()}")

    # --- For TRAUMA capability mismatch ---
    if 'TRAUMA_ADULT' in df.columns and 'TRAUMA_PEDS' in df.columns:
        df['trauma_adult'] = df['TRAUMA_ADULT'].fillna(False).astype(bool)
        df['trauma_peds'] = df['TRAUMA_PEDS'].fillna(False).astype(bool)
        
        df['trauma_category'] = 'Neither'
        df.loc[df['trauma_adult'] & df['trauma_peds'], 'trauma_category'] = 'Both'
        df.loc[df['trauma_adult'] & ~df['trauma_peds'], 'trauma_category'] = 'Adult-Only'
        df.loc[~df['trauma_adult'] & df['trauma_peds'], 'trauma_category'] = 'Peds-Only'
        
        print("\n=== TRAUMA Capability Mismatch at Facility Level ===")
        print(df['trauma_category'].value_counts())

    # --- State-level mismatch analysis ---
    print("\n\n=== STATE-LEVEL BURN MISMATCH ANALYSIS ===")
    state_burn = df.groupby('STATE').agg(
        total_facilities=('STATE','size'),
        adult_burn=('burn_adult', 'sum'),
        peds_burn=('burn_peds', 'sum'),
        both_burn=('burn_category', lambda x: (x=='Both').sum()),
        adult_only_burn=('burn_category', lambda x: (x=='Adult-Only').sum()),
        peds_only_burn=('burn_category', lambda x: (x=='Peds-Only').sum()),
    ).reset_index()
    
    # Detect mismatch states
    # Type A: Has adult burn but NO peds burn centers
    state_burn['mismatch_adult_only'] = (state_burn['adult_burn'] > 0) & (state_burn['peds_burn'] == 0)
    # Type B: Has peds burn but NO adult burn centers
    state_burn['mismatch_peds_only'] = (state_burn['peds_burn'] > 0) & (state_burn['adult_burn'] == 0)
    # Type C: Has neither
    state_burn['gap_no_burn'] = (state_burn['adult_burn'] == 0) & (state_burn['peds_burn'] == 0)
    
    print("\nStates with Adult-Only burn centers (no peds capability):")
    adult_only_states = state_burn[state_burn['mismatch_adult_only']]
    print(adult_only_states[['STATE','adult_burn','peds_burn']].to_string())
    
    print("\nStates with Peds-Only burn centers (no adult capability):")
    peds_only_states = state_burn[state_burn['mismatch_peds_only']]
    print(peds_only_states[['STATE','adult_burn','peds_burn']].to_string())
    
    print("\nStates with NO burn centers at all:")
    no_burn_states = state_burn[state_burn['gap_no_burn']]
    print(no_burn_states[['STATE','total_facilities']].to_string())
    
    print(f"\nSummary:")
    print(f"  States with Only Adult burn centers: {state_burn['mismatch_adult_only'].sum()}")
    print(f"  States with Only Peds burn centers: {state_burn['mismatch_peds_only'].sum()}")
    print(f"  States with No burn centers: {state_burn['gap_no_burn'].sum()}")
    print(f"  States with Both adult+peds: {((state_burn['adult_burn']>0)&(state_burn['peds_burn']>0)).sum()}")

    # --- Referral Delay Analysis ---
    print("\n\n=== REFERRAL DELAY ROOT CAUSE ANALYSIS ===")
    # Children in adult-only states need out-of-state referral for burn care
    # Adults in peds-only states need out-of-state referral for burn care
    # This is the mismatch causing referral delays
    
    state_burn['child_referral_needed'] = state_burn['mismatch_adult_only'] | state_burn['gap_no_burn']
    state_burn['adult_referral_needed'] = state_burn['mismatch_peds_only'] | state_burn['gap_no_burn']
    
    print(f"\nStates where CHILDREN need out-of-state burn referral (no peds burn center): {state_burn['child_referral_needed'].sum()}")
    print(state_burn[state_burn['child_referral_needed']]['STATE'].tolist())
    
    print(f"\nStates where ADULTS need out-of-state burn referral (no adult burn center): {state_burn['adult_referral_needed'].sum()}")
    print(state_burn[state_burn['adult_referral_needed']]['STATE'].tolist())

    # Merge with CDC fatality data for impact
    fatal_path = DATA_EXTERNAL / "fatal_report_per_state.csv"
    if fatal_path.exists():
        fatal = pd.read_csv(fatal_path)
        print("\n=== CDC Fatal Data Columns ===")
        print(fatal.columns.tolist())
        print(fatal.head(3).to_string())
        
        # Try to merge
        if 'State' in fatal.columns:
            fatal_merge = fatal.rename(columns={'State':'STATE'})
        elif 'state' in fatal.columns:
            fatal_merge = fatal.rename(columns={'state':'STATE'})
        else:
            fatal_merge = fatal.copy()
        
        # Merge state_burn with fatality data
        state_burn_fatal = state_burn.merge(fatal_merge, on='STATE', how='left')
        
        print("\n=== States with Adult-Only burn centers + High Fatality Rates ===")
        adult_only_fatal = state_burn_fatal[state_burn_fatal['mismatch_adult_only']].sort_values(
            state_burn_fatal.columns[-1], ascending=False
        )
        print(adult_only_fatal.to_string())
        
        print("\n=== States with No Burn Centers + Fatality Data ===")
        no_burn_fatal = state_burn_fatal[state_burn_fatal['gap_no_burn']]
        print(no_burn_fatal.to_string())
    
    # --- Quantify the referral delay ---
    referral_path = OUTPUTS / "referral_network_recommendations.csv"
    if referral_path.exists():
        referral = pd.read_csv(referral_path)
        print("\n=== Referral Network Recommendations ===")
        print(referral.to_string())
        
        # Link mismatch states to referral distances
        mismatch_states = state_burn[state_burn['mismatch_adult_only'] | state_burn['gap_no_burn']]['STATE'].tolist()
        referral_impact = referral[referral['origin_state'].isin(mismatch_states)]
        print("\n=== Referral Distances for Mismatch/Gap States (Adult Burn) ===")
        print(referral_impact.to_string())
    
    # Save the mismatch analysis
    state_burn.to_csv(OUTPUTS / "burn_mismatch_by_state.csv", index=False)
    print(f"\nSaved mismatch analysis to outputs/burn_mismatch_by_state.csv")
    
    return state_burn, df

if __name__ == "__main__":
    state_burn, df = analyze_mismatch()
