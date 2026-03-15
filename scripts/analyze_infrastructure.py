"""
Deep infrastructure & certification inconsistency analysis.
Covers:
  1. Burn BED infrastructure mismatch (adult vs peds burn beds)
  2. ACS/ABA verification inconsistencies vs actual burn bed possession
  3. BC_STATE_DESIGNATED vs ABA_VERIFIED vs burn beds
  4. Hospitals with burn beds but NO verification (dangerous capability gap)
  5. State-level summary of all dimensions
"""
from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loading import load_clean_hospital_data

DATA_EXTERNAL = ROOT / "data" / "external"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "docs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

STATE_ABBREV = {
    'AL':'Alabama','AK':'Alaska','AZ':'Arizona','AR':'Arkansas','CA':'California',
    'CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia',
    'HI':'Hawaii','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa',
    'KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland',
    'MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi',
    'MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire',
    'NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina',
    'ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania',
    'RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee',
    'TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington',
    'WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming','DC':'District of Columbia'
}
FULL_TO_ABBREV = {v: k for k, v in STATE_ABBREV.items()}

# -----------------------------------------------------------------------
# LOAD & NORMALIZE
# -----------------------------------------------------------------------
def load_and_prepare():
    df = load_clean_hospital_data()
    
    # Boolean normalization
    for col in ['BURN_ADULT','BURN_PEDS','TRAUMA_ADULT','TRAUMA_PEDS',
                'ACS_VERIFIED','ABA_VERIFIED','BC_STATE_DESIGNATED',
                'TC_STATE_DESIGNATED','ADULT_TRAUMA_L1','ADULT_TRAUMA_L2',
                'PEDS_TRAUMA_L1','PEDS_TRAUMA_L2']:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)
    
    df['BURN_BEDS'] = pd.to_numeric(df['BURN_BEDS'], errors='coerce').fillna(0)
    df['TOTAL_BEDS'] = pd.to_numeric(df['TOTAL_BEDS'], errors='coerce')
    
    # Has any burn beds (bed infrastructure)
    df['has_burn_beds'] = df['BURN_BEDS'] > 0
    
    # Burn capability flags
    df['burn_adult'] = df['BURN_ADULT']
    df['burn_peds'] = df['BURN_PEDS']
    df['has_any_burn_flag'] = df['burn_adult'] | df['burn_peds']
    
    # ABA verified for burn
    df['aba_verified'] = df['ABA_VERIFIED']
    df['acs_verified'] = df['ACS_VERIFIED']
    df['bc_state_designated'] = df['BC_STATE_DESIGNATED']
    
    # "Any burn verification" — ABA or BC_STATE_DESIGNATED
    df['any_burn_verification'] = df['aba_verified'] | df['bc_state_designated']
    
    return df

# -----------------------------------------------------------------------
# DIMENSION 1: BURN BED INFRASTRUCTURE — who has burn beds vs who is certified
# -----------------------------------------------------------------------
def analyze_burn_bed_certification(df):
    """
    Key question: Are burn beds concentrated in verified facilities,
    or are burn beds scattered across unverified facilities?
    """
    print("\n" + "="*70)
    print("DIMENSION 1: BURN BED INFRASTRUCTURE vs CERTIFICATION")
    print("="*70)
    
    # Categorise facilities by: have burn beds? + have any verification?
    df['infra_cert_category'] = 'No burn beds, No verification'
    df.loc[df['has_burn_beds'] & df['any_burn_verification'], 'infra_cert_category'] = 'Burn beds + Verified'
    df.loc[df['has_burn_beds'] & ~df['any_burn_verification'], 'infra_cert_category'] = 'Burn beds, NOT verified'
    df.loc[~df['has_burn_beds'] & df['any_burn_verification'], 'infra_cert_category'] = 'No burn beds, but Verified'
    df.loc[~df['has_burn_beds'] & ~df['any_burn_verification'], 'infra_cert_category'] = 'No burn beds, No verification'
    
    cat_counts = df['infra_cert_category'].value_counts()
    print("\nFacility categories (burn beds × verification):")
    print(cat_counts)
    
    # Total burn beds by category
    beds_by_cat = df.groupby('infra_cert_category')['BURN_BEDS'].sum()
    print("\nTotal BURN_BEDS held by each category:")
    print(beds_by_cat)
    
    # Specific alarm: verified facilities with NO burn beds
    no_beds_verified = df[~df['has_burn_beds'] & df['any_burn_verification']]
    print(f"\nVerified burn facilities with ZERO burn beds: {len(no_beds_verified)}")
    print(no_beds_verified[['STATE','HOSPITAL_NAME','BURN_BEDS','ABA_VERIFIED','BC_STATE_DESIGNATED']].to_string())
    
    # Specific alarm: facilities with burn beds but NO verification
    beds_no_verify = df[df['has_burn_beds'] & ~df['any_burn_verification']]
    print(f"\nFacilities with burn beds but NO verification: {len(beds_no_verify)}")
    print(beds_no_verify[['STATE','HOSPITAL_NAME','BURN_BEDS','ABA_VERIFIED','ACS_VERIFIED','BC_STATE_DESIGNATED']].to_string())
    total_unverif_beds = beds_no_verify['BURN_BEDS'].sum()
    print(f"  --> Total unverified burn beds: {total_unverif_beds:.0f}")
    
    return df, cat_counts, beds_no_verify, no_beds_verified

# -----------------------------------------------------------------------
# DIMENSION 2: ACS vs ABA VERIFICATION INCONSISTENCY
# -----------------------------------------------------------------------
def analyze_verification_inconsistency(df):
    print("\n" + "="*70)
    print("DIMENSION 2: ACS vs ABA VERIFICATION INCONSISTENCY")
    print("="*70)
    
    # ACS = trauma-level verification, ABA = burn-specific verification
    # A hospital can be ACS-verified (for trauma) but NOT ABA-verified (for burn)
    # and still have burn beds — this is a certification gap
    
    burn_facilities = df[df['has_burn_beds']].copy()
    
    burn_facilities['acs_only'] = burn_facilities['acs_verified'] & ~burn_facilities['aba_verified'] & ~burn_facilities['bc_state_designated']
    burn_facilities['aba_only'] = burn_facilities['aba_verified'] & ~burn_facilities['acs_verified']
    burn_facilities['both_acs_aba'] = burn_facilities['acs_verified'] & (burn_facilities['aba_verified'] | burn_facilities['bc_state_designated'])
    burn_facilities['neither'] = ~burn_facilities['acs_verified'] & ~burn_facilities['aba_verified'] & ~burn_facilities['bc_state_designated']
    
    print(f"\nOf {len(burn_facilities)} facilities with BURN BEDS:")
    print(f"  ACS + ABA verified (full): {burn_facilities['both_acs_aba'].sum()}")
    print(f"  ACS-only (trauma certified, NOT burn certified): {burn_facilities['acs_only'].sum()}")
    print(f"  ABA-only (burn certified, NOT ACS trauma certified): {burn_facilities['aba_only'].sum()}")
    print(f"  Neither ACS nor ABA verified: {burn_facilities['neither'].sum()}")
    
    print("\nFacilities with burn beds, ACS verified but NOT ABA/BC_STATE verified:")
    acs_not_aba = burn_facilities[burn_facilities['acs_only']]
    print(acs_not_aba[['STATE','HOSPITAL_NAME','BURN_BEDS','ACS_VERIFIED','ABA_VERIFIED','BC_STATE_DESIGNATED']].to_string())
    
    print("\nFacilities with burn beds but NEITHER ACS nor ABA/BC verified:")
    neither_verified = burn_facilities[burn_facilities['neither']]
    print(neither_verified[['STATE','HOSPITAL_NAME','BURN_BEDS','ACS_VERIFIED','ABA_VERIFIED']].to_string())
    
    return burn_facilities, acs_not_aba, neither_verified

# -----------------------------------------------------------------------
# DIMENSION 3: ADULT vs PEDS BURN BED MISMATCH (bed-count level)
# -----------------------------------------------------------------------
def analyze_burn_bed_age_mismatch(df):
    print("\n" + "="*70)
    print("DIMENSION 3: BURN BED AGE-APPROPRIATENESS MISMATCH (bed count level)")
    print("="*70)
    
    # Burn beds exist but only adult OR only peds flag set
    beds_df = df[df['has_burn_beds']].copy()
    beds_df['adult_flag'] = beds_df['burn_adult']
    beds_df['peds_flag'] = beds_df['burn_peds']
    
    beds_df['age_coverage'] = 'Both (Adult + Peds)'
    beds_df.loc[beds_df['adult_flag'] & ~beds_df['peds_flag'], 'age_coverage'] = 'Adult-Only beds'
    beds_df.loc[~beds_df['adult_flag'] & beds_df['peds_flag'], 'age_coverage'] = 'Peds-Only beds'
    beds_df.loc[~beds_df['adult_flag'] & ~beds_df['peds_flag'], 'age_coverage'] = 'Beds but NO capability flag'
    
    print("\nFacilities with burn beds, by age-flag coverage:")
    print(beds_df['age_coverage'].value_counts())
    print("\nTotal BURN_BEDS by age coverage category:")
    print(beds_df.groupby('age_coverage')['BURN_BEDS'].agg(['sum','mean','count']))
    
    # Most alarming: beds but no capability flag at all
    no_flag = beds_df[beds_df['age_coverage'] == 'Beds but NO capability flag']
    print(f"\nFacilities with burn beds but NO adult/peds flag set: {len(no_flag)}")
    print(no_flag[['STATE','HOSPITAL_NAME','BURN_BEDS','BURN_ADULT','BURN_PEDS','ACS_VERIFIED','ABA_VERIFIED']].to_string())
    
    # State-level: burn beds per capita adult vs peds capable
    state_bed_age = df.groupby('STATE').agg(
        total_burn_beds=('BURN_BEDS', 'sum'),
        adult_burn_beds=('BURN_BEDS', lambda x: x[df.loc[x.index, 'burn_adult']].sum()),
        peds_burn_beds=('BURN_BEDS', lambda x: x[df.loc[x.index, 'burn_peds']].sum()),
        beds_no_flag=('BURN_BEDS', lambda x: x[~df.loc[x.index, 'has_any_burn_flag']].sum()),
    ).reset_index()
    
    print("\n\nState-level burn beds breakdown (adult capable vs peds capable):")
    print(state_bed_age[state_bed_age['total_burn_beds'] > 0].to_string())
    
    return beds_df, state_bed_age, no_flag

# -----------------------------------------------------------------------
# DIMENSION 4: FULL STATE INFRASTRUCTURE SCORECARD
# -----------------------------------------------------------------------
def build_state_infrastructure_scorecard(df):
    print("\n" + "="*70)
    print("DIMENSION 4: STATE INFRASTRUCTURE SCORECARD")
    print("="*70)
    
    scorecard = df.groupby('STATE').agg(
        facilities=('STATE', 'size'),
        total_burn_beds=('BURN_BEDS', 'sum'),
        burn_adult_centers=('burn_adult', 'sum'),
        burn_peds_centers=('burn_peds', 'sum'),
        aba_verified_count=('aba_verified', 'sum'),
        acs_verified_count=('acs_verified', 'sum'),
        bc_designated_count=('bc_state_designated', 'sum'),
        any_burn_verification_count=('any_burn_verification', 'sum'),
        unverified_burn_beds=('BURN_BEDS', lambda x: x[~df.loc[x.index, 'any_burn_verification']].sum()),
        pct_burn_beds_in_verified=('BURN_BEDS', lambda x: (
            x[df.loc[x.index, 'any_burn_verification']].sum() / x.sum() * 100
            if x.sum() > 0 else np.nan
        )),
    ).reset_index()
    
    # Derive mismatch flags
    scorecard['has_burn_infrastructure'] = scorecard['total_burn_beds'] > 0
    scorecard['peds_burn_coverage_gap'] = scorecard['burn_peds_centers'] == 0
    scorecard['adult_burn_coverage_gap'] = scorecard['burn_adult_centers'] == 0
    scorecard['has_unverified_burn_beds'] = scorecard['unverified_burn_beds'] > 0
    scorecard['full_gap_no_burn_beds'] = scorecard['total_burn_beds'] == 0
    
    # Infrastructure adequacy categories
    scorecard['infrastructure_status'] = 'Adequate'
    scorecard.loc[scorecard['full_gap_no_burn_beds'], 'infrastructure_status'] = 'Critical: No Burn Beds'
    scorecard.loc[scorecard['has_burn_infrastructure'] & scorecard['peds_burn_coverage_gap'], 'infrastructure_status'] = 'Partial: Adult-Only Bed Access'
    scorecard.loc[scorecard['has_unverified_burn_beds'] & ~scorecard['full_gap_no_burn_beds'], 'infrastructure_status'] = 'Risk: Unverified Burn Beds Present'
    
    print("\nInfrastructure status by state:")
    print(scorecard[['STATE','total_burn_beds','burn_adult_centers','burn_peds_centers',
                      'aba_verified_count','unverified_burn_beds','pct_burn_beds_in_verified',
                      'infrastructure_status']].sort_values('total_burn_beds').to_string())
    
    print("\n\nStatus counts:")
    print(scorecard['infrastructure_status'].value_counts())
    
    print(f"\nTotal unverified burn beds across all states: {scorecard['unverified_burn_beds'].sum():.0f}")
    print(f"States with no burn beds at all: {scorecard['full_gap_no_burn_beds'].sum()}")
    print(f"States with unverified burn beds: {scorecard['has_unverified_burn_beds'].sum()}")
    
    return scorecard

# -----------------------------------------------------------------------
# FIGURES
# -----------------------------------------------------------------------
def figure_infra_cert_donut(df):
    """Donut chart: burn bed × verification status at facility level."""
    df['infra_cert_simple'] = 'Other'
    df.loc[df['has_burn_beds'] & df['any_burn_verification'], 'infra_cert_simple'] = 'Burn beds + Verified'
    df.loc[df['has_burn_beds'] & ~df['any_burn_verification'], 'infra_cert_simple'] = 'Burn beds, NOT verified'
    df.loc[~df['has_burn_beds'] & df['any_burn_verification'], 'infra_cert_simple'] = 'No burn beds, but Verified'
    df.loc[~df['has_burn_beds'] & ~df['has_any_burn_flag'], 'infra_cert_simple'] = 'No burn beds, No verification'
    
    counts = df['infra_cert_simple'].value_counts()
    colors = ['#27ae60', '#e74c3c', '#f39c12', '#95a5a6']
    
    fig, ax = plt.subplots(figsize=(9, 7))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=None,
        colors=colors[:len(counts)],
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.78,
        wedgeprops=dict(width=0.55, edgecolor='white', linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight('bold')
        at.set_color('white')
    
    ax.legend(
        [f"{l} (n={v})" for l, v in zip(counts.index, counts.values)],
        loc='lower center', bbox_to_anchor=(0.5, -0.12), fontsize=10, framealpha=0.9
    )
    ax.set_title('Burn Bed Infrastructure vs. Certification Status\n(Facility Level, n=635)', 
                fontsize=13, fontweight='bold', pad=20)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_infra_cert_donut.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_infra_cert_donut.png")


def figure_unverified_beds_by_state(scorecard):
    """Bar chart: unverified burn beds by state, stacked with verified."""
    df_plot = scorecard[scorecard['total_burn_beds'] > 0].copy()
    df_plot = df_plot.sort_values('total_burn_beds', ascending=True)
    
    verified_beds = df_plot['total_burn_beds'] - df_plot['unverified_burn_beds']
    
    fig, ax = plt.subplots(figsize=(12, 10))
    bars1 = ax.barh(df_plot['STATE'], verified_beds, color='#27ae60', label='Verified burn beds', height=0.7)
    bars2 = ax.barh(df_plot['STATE'], df_plot['unverified_burn_beds'], 
                    left=verified_beds, color='#e74c3c', label='Unverified burn beds', height=0.7)
    
    # Add state total annotations
    for i, (_, row) in enumerate(df_plot.iterrows()):
        if row['unverified_burn_beds'] > 0:
            ax.text(row['total_burn_beds'] + 1, i, f"+{int(row['unverified_burn_beds'])} unverified",
                   va='center', fontsize=7.5, color='#c0392b', fontweight='bold')
    
    ax.set_xlabel('Burn Beds', fontsize=12)
    ax.set_title('Burn Bed Distribution: Verified vs. Unverified Facilities by State\n(Red = beds in facilities lacking ABA or State Burn Centre designation)', 
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=11, loc='lower right')
    ax.spines[['top','right']].set_visible(False)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(axis='x', alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_unverified_beds_by_state.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_unverified_beds_by_state.png")


def figure_acs_vs_aba_mismatch(burn_facilities):
    """Stacked bar comparison of ACS vs ABA verification for facilities with burn beds."""
    acs_no_aba = burn_facilities['acs_only'].sum()
    both = burn_facilities['both_acs_aba'].sum()
    aba_no_acs = burn_facilities['aba_only'].sum()
    neither = burn_facilities['neither'].sum()
    
    categories = ['ACS + ABA\n(Fully Verified)', 'ACS Only\n(Trauma cert, no burn cert)', 
                  'ABA Only\n(Burn cert, no ACS)', 'Neither\n(No formal certification)']
    values = [both, acs_no_aba, aba_no_acs, neither]
    colors = ['#27ae60', '#f39c12', '#3498db', '#e74c3c']
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(categories, values, color=colors, edgecolor='white', linewidth=1.5, width=0.6)
    
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
               f'{val}', ha='center', va='bottom', fontsize=13, fontweight='bold')
    
    ax.set_ylabel('Number of Facilities with Burn Beds', fontsize=11)
    ax.set_title('Certification Inconsistency: Facilities WITH Burn Beds by Verification Type\n(Orange/Red = certification-infrastructure mismatch)', 
                fontsize=12, fontweight='bold')
    ax.spines[['top','right']].set_visible(False)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(axis='y', alpha=0.3)
    ax.set_ylim(0, max(values) * 1.15)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_acs_aba_cert_mismatch.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_acs_aba_cert_mismatch.png")


def figure_pct_verified_beds_vs_total(scorecard):
    """Scatter: % of burn beds in verified facilities vs total burn beds."""
    df_plot = scorecard[scorecard['total_burn_beds'] > 0].dropna(subset=['pct_burn_beds_in_verified']).copy()
    
    fig, ax = plt.subplots(figsize=(11, 7))
    
    scatter = ax.scatter(
        df_plot['total_burn_beds'],
        df_plot['pct_burn_beds_in_verified'],
        s=df_plot['total_burn_beds'] * 1.5,
        c=df_plot['pct_burn_beds_in_verified'],
        cmap='RdYlGn',
        vmin=0, vmax=100,
        alpha=0.85,
        edgecolors='gray',
        linewidth=0.6,
        zorder=3
    )
    
    plt.colorbar(scatter, ax=ax, label='% burn beds in verified facilities')
    
    # Label states below 80% verified
    for _, row in df_plot[df_plot['pct_burn_beds_in_verified'] < 80].iterrows():
        ax.annotate(row['STATE'], (row['total_burn_beds'], row['pct_burn_beds_in_verified']),
                   textcoords='offset points', xytext=(5, 3), fontsize=8, fontweight='bold')
    
    ax.axhline(100, color='green', linestyle='--', linewidth=1, alpha=0.5, label='100% verified')
    ax.axhline(80, color='orange', linestyle=':', linewidth=1.2, label='80% threshold')
    ax.set_xlabel('Total Burn Beds in State', fontsize=12)
    ax.set_ylabel('% Burn Beds in Verified Facilities', fontsize=12)
    ax.set_title('Burn Bed Volume vs. Verification Coverage by State\n(States below 80% line have significant unverified burn capacity)', 
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_pct_verified_beds_scatter.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_pct_verified_beds_scatter.png")


def figure_age_mismatch_beds(state_bed_age):
    """Grouped bar: adult-capable burn beds vs peds-capable burn beds by state."""
    df_plot = state_bed_age[state_bed_age['total_burn_beds'] > 0].copy()
    df_plot = df_plot.sort_values('total_burn_beds', ascending=False).head(25)
    
    x = np.arange(len(df_plot))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 6))
    b1 = ax.bar(x - width/2, df_plot['adult_burn_beds'], width, 
                label='Beds in Adult-capable facilities', color='#2980b9', alpha=0.9)
    b2 = ax.bar(x + width/2, df_plot['peds_burn_beds'], width, 
                label='Beds in Peds-capable facilities', color='#e74c3c', alpha=0.9)
    
    # Highlight states where peds beds = 0
    for i, (_, row) in enumerate(df_plot.iterrows()):
        if row['peds_burn_beds'] == 0 and row['adult_burn_beds'] > 0:
            ax.axvspan(i - 0.5, i + 0.5, alpha=0.07, color='red', zorder=0)
    
    ax.set_xticks(x)
    ax.set_xticklabels(df_plot['STATE'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Burn Beds Count', fontsize=11)
    ax.set_title('Adult vs. Pediatric Burn Bed Capacity by State (Top 25 by Volume)\n(Red shading = State where children cannot access burn beds in-state)', 
                fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.spines[['top','right']].set_visible(False)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(axis='y', alpha=0.3)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_age_mismatch_beds.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_age_mismatch_beds.png")


def figure_infrastructure_scorecard_heatmap(scorecard):
    """Heatmap-style grid of infrastructure scores per state."""
    metrics = ['total_burn_beds', 'burn_adult_centers', 'burn_peds_centers',
               'aba_verified_count', 'unverified_burn_beds']
    labels = ['Burn Beds\n(total)', 'Adult Burn\nCenters', 'Peds Burn\nCenters',
              'ABA\nVerified', 'Unverif.\nBurn Beds']
    
    df_plot = scorecard.set_index('STATE')[metrics].copy()
    
    # Normalize each column for color coding
    df_norm = df_plot.copy().astype(float)
    for col in metrics:
        col_max = df_norm[col].max()
        if col_max > 0:
            df_norm[col] = df_norm[col] / col_max
    
    # For 'unverified beds' invert color (higher is worse)
    df_norm_for_plot = df_norm.copy()
    
    fig, ax = plt.subplots(figsize=(10, 18))
    
    im = ax.imshow(df_norm_for_plot.values, aspect='auto', cmap='YlOrRd', vmin=0, vmax=1)
    
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10, fontweight='bold')
    ax.set_yticks(range(len(df_plot)))
    ax.set_yticklabels(df_plot.index, fontsize=8)
    ax.xaxis.tick_top()
    
    # Add text values
    for i in range(len(df_plot)):
        for j, col in enumerate(metrics):
            val = df_plot.iloc[i][col]
            ax.text(j, i, f'{int(val)}', ha='center', va='center', fontsize=7,
                   color='black' if df_norm_for_plot.iloc[i][col] < 0.6 else 'white')
    
    ax.set_title('State Burn Infrastructure Scorecard\n(Burn Beds, Center Designations, Verification)', 
                fontsize=13, fontweight='bold', pad=30)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_infrastructure_scorecard.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_infrastructure_scorecard.png")


# -----------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------
if __name__ == "__main__":
    df = load_and_prepare()
    
    df, cat_counts, beds_no_verify, no_beds_verified = analyze_burn_bed_certification(df)
    burn_facilities, acs_not_aba, neither_verified = analyze_verification_inconsistency(df)
    beds_df, state_bed_age, no_flag = analyze_burn_bed_age_mismatch(df)
    scorecard = build_state_infrastructure_scorecard(df)
    
    print("\n\n=== GENERATING FIGURES ===")
    figure_infra_cert_donut(df)
    figure_unverified_beds_by_state(scorecard)
    figure_acs_vs_aba_mismatch(burn_facilities)
    figure_pct_verified_beds_vs_total(scorecard)
    figure_age_mismatch_beds(state_bed_age)
    figure_infrastructure_scorecard_heatmap(scorecard)
    
    # Save scorecard
    scorecard.to_csv(OUTPUTS / "burn_infrastructure_scorecard.csv", index=False)
    state_bed_age.to_csv(OUTPUTS / "burn_bed_age_mismatch.csv", index=False)
    print("\nSaved: outputs/burn_infrastructure_scorecard.csv")
    print("Saved: outputs/burn_bed_age_mismatch.csv")
