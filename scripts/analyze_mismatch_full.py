"""
Full mismatch analysis: adult/child burn center mismatch, referral delay root cause,
and figure generation for updating the Equitable Access report.
"""
from __future__ import annotations
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_loading import load_clean_hospital_data

DATA_EXTERNAL = ROOT / "data" / "external"
OUTPUTS = ROOT / "outputs"
FIGURES = ROOT / "docs" / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# State abbreviation to full name mapping
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

def build_mismatch_analysis():
    df = load_clean_hospital_data()
    
    # Normalize boolean flags
    df['burn_adult'] = df['BURN_ADULT'].fillna(False).astype(bool)
    df['burn_peds'] = df['BURN_PEDS'].fillna(False).astype(bool)
    df['trauma_adult'] = df['TRAUMA_ADULT'].fillna(False).astype(bool)
    df['trauma_peds'] = df['TRAUMA_PEDS'].fillna(False).astype(bool)
    
    # Facility-level burn category
    df['burn_category'] = 'Neither'
    df.loc[df['burn_adult'] & df['burn_peds'], 'burn_category'] = 'Both'
    df.loc[df['burn_adult'] & ~df['burn_peds'], 'burn_category'] = 'Adult-Only'
    df.loc[~df['burn_adult'] & df['burn_peds'], 'burn_category'] = 'Peds-Only'
    
    # Facility-level trauma category
    df['trauma_category'] = 'Neither'
    df.loc[df['trauma_adult'] & df['trauma_peds'], 'trauma_category'] = 'Both'
    df.loc[df['trauma_adult'] & ~df['trauma_peds'], 'trauma_category'] = 'Adult-Only'
    df.loc[~df['trauma_adult'] & df['trauma_peds'], 'trauma_category'] = 'Peds-Only'
    
    # State-level aggregation
    state_burn = df.groupby('STATE').agg(
        total_facilities=('STATE', 'size'),
        adult_burn_centers=('burn_adult', 'sum'),
        peds_burn_centers=('burn_peds', 'sum'),
        both_burn=('burn_category', lambda x: (x=='Both').sum()),
        adult_only_burn=('burn_category', lambda x: (x=='Adult-Only').sum()),
        peds_only_burn=('burn_category', lambda x: (x=='Peds-Only').sum()),
        adult_trauma_centers=('trauma_adult', 'sum'),
        peds_trauma_centers=('trauma_peds', 'sum'),
    ).reset_index()
    
    # Mismatch flags
    state_burn['mismatch_adult_only'] = (state_burn['adult_burn_centers'] > 0) & (state_burn['peds_burn_centers'] == 0)
    state_burn['mismatch_peds_only'] = (state_burn['peds_burn_centers'] > 0) & (state_burn['adult_burn_centers'] == 0)
    state_burn['gap_no_burn'] = (state_burn['adult_burn_centers'] == 0) & (state_burn['peds_burn_centers'] == 0)
    state_burn['has_both'] = (state_burn['adult_burn_centers'] > 0) & (state_burn['peds_burn_centers'] > 0)
    
    # Overall status category
    state_burn['burn_coverage_status'] = 'Both Adult & Peds'
    state_burn.loc[state_burn['mismatch_adult_only'], 'burn_coverage_status'] = 'Adult-Only Gap'
    state_burn.loc[state_burn['mismatch_peds_only'], 'burn_coverage_status'] = 'Peds-Only Gap'
    state_burn.loc[state_burn['gap_no_burn'], 'burn_coverage_status'] = 'No Burn Center'
    
    # Referral needed flags
    state_burn['child_burn_referral_needed'] = state_burn['peds_burn_centers'] == 0
    state_burn['adult_burn_referral_needed'] = state_burn['adult_burn_centers'] == 0
    
    print("=== BURN COVERAGE STATUS BY STATE ===")
    print(state_burn[['STATE','adult_burn_centers','peds_burn_centers','burn_coverage_status']].to_string())
    
    print("\nSummary counts:")
    print(state_burn['burn_coverage_status'].value_counts())
    
    return state_burn, df


def merge_with_fatality(state_burn):
    fatal_path = DATA_EXTERNAL / "fatal_report_per_state.csv"
    if not fatal_path.exists():
        print("Fatal data not found, skipping merge")
        return state_burn
    
    fatal = pd.read_csv(fatal_path)
    # Map full names to abbreviations
    fatal['STATE'] = fatal['State'].map(FULL_TO_ABBREV)
    fatal['crude_rate'] = pd.to_numeric(fatal['Crude Rate'], errors='coerce')
    fatal['deaths'] = pd.to_numeric(fatal['Deaths'].astype(str).str.replace(',',''), errors='coerce')
    
    merged = state_burn.merge(fatal[['STATE','deaths','crude_rate']], on='STATE', how='left')
    return merged


def load_referral_and_metrics():
    referral = pd.read_csv(OUTPUTS / "referral_network_recommendations.csv")
    metrics = pd.read_csv(OUTPUTS / "equitable_access_state_metrics.csv")
    return referral, metrics


def figure_burn_coverage_status(state_burn):
    """Bar chart showing burn coverage status distribution as stacked grouped chart."""
    status_counts = state_burn['burn_coverage_status'].value_counts()
    colors = {'Both Adult & Peds': '#2ecc71', 'Adult-Only Gap': '#f39c12', 
              'Peds-Only Gap': '#e74c3c', 'No Burn Center': '#7f8c8d'}
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(status_counts.index, status_counts.values,
                  color=[colors.get(k, '#3498db') for k in status_counts.index],
                  edgecolor='white', linewidth=1.5, zorder=3)
    
    for bar, val in zip(bars, status_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
                f'{val} states', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(axis='y', alpha=0.4, zorder=0)
    ax.set_ylabel('Number of States', fontsize=13)
    ax.set_title('State-Level Burn Center Coverage Status\n(Adult vs. Pediatric Capability Mismatch)', 
                 fontsize=14, fontweight='bold', pad=15)
    ax.spines[['top','right']].set_visible(False)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_burn_coverage_status.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_burn_coverage_status.png")


def figure_mismatch_state_map(state_burn):
    """State map color-coded by mismatch status."""
    try:
        import geopandas as gpd
        
        zip_path = DATA_EXTERNAL / "cb_2023_us_state_20m.zip"
        shp_path = DATA_EXTERNAL / "cb_2023_us_state_20m" / "cb_2023_us_state_20m.shp"
        
        if zip_path.exists():
            gdf = gpd.read_file(f"zip://{zip_path}")
        elif shp_path.exists():
            gdf = gpd.read_file(shp_path)
        else:
            print("Shapefile not found, skipping map")
            return
        
        gdf = gdf.rename(columns={'STUSPS': 'STATE'})
        gdf = gdf.merge(state_burn[['STATE','burn_coverage_status']], on='STATE', how='left')
        
        # Exclude non-contiguous for clarity
        gdf_lower = gdf[~gdf['STATE'].isin(['AK', 'HI', 'PR', 'VI', 'GU', 'MP', 'AS'])]
        
        color_map = {
            'Both Adult & Peds': '#27ae60',
            'Adult-Only Gap': '#f39c12', 
            'Peds-Only Gap': '#e74c3c',
            'No Burn Center': '#c0392b',
        }
        
        gdf_lower['color'] = gdf_lower['burn_coverage_status'].map(color_map).fillna('#bdc3c7')
        
        fig, ax = plt.subplots(figsize=(14, 8))
        fig.patch.set_facecolor('#f0f4f8')
        ax.set_facecolor('#d6eaf8')
        
        for status, color in color_map.items():
            subset = gdf_lower[gdf_lower['burn_coverage_status'] == status]
            if not subset.empty:
                subset.plot(ax=ax, color=color, edgecolor='white', linewidth=0.7, label=status)
        
        # States with no data
        no_data = gdf_lower[gdf_lower['burn_coverage_status'].isna()]
        if not no_data.empty:
            no_data.plot(ax=ax, color='#bdc3c7', edgecolor='white', linewidth=0.7)
        
        ax.set_axis_off()
        
        # Add state labels for mismatch/gap states
        gap_states = state_burn[state_burn['burn_coverage_status'] != 'Both Adult & Peds']['STATE'].tolist()
        for _, row in gdf_lower.iterrows():
            if row['STATE'] in gap_states:
                centroid = row.geometry.centroid
                ax.annotate(row['STATE'], (centroid.x, centroid.y),
                           ha='center', va='center', fontsize=7, fontweight='bold', color='white')
        
        patches = [mpatches.Patch(color=c, label=l) for l, c in color_map.items()]
        ax.legend(handles=patches, loc='lower left', framealpha=0.9, fontsize=10, title='Burn Coverage Status')
        
        ax.set_title('Adult vs. Pediatric Burn Center Coverage by State\n(Mismatch and Gap States)', 
                    fontsize=14, fontweight='bold', pad=10)
        
        fig.tight_layout()
        fig.savefig(FIGURES / "narr_ea_mismatch_map.png", dpi=150, bbox_inches='tight')
        plt.close(fig)
        print("Saved: narr_ea_mismatch_map.png")
    except Exception as e:
        print(f"Map generation error: {e}")


def figure_referral_delay_distance(referral, state_burn):
    """Referral distance bar chart color-coded by mismatch type."""
    merged_ref = referral.merge(
        state_burn[['STATE','burn_coverage_status','child_burn_referral_needed']],
        left_on='origin_state', right_on='STATE', how='left'
    )
    
    merged_ref = merged_ref.sort_values('estimated_distance_km', ascending=True)
    
    # Add peds-referral states (CT, KY, ME, VT, WV) — they're not in referral list since they have adult centers
    # The referral list only shows adult burn referrals; peds gaps need separate treatment
    
    color_map_ref = {
        'No Burn Center': '#c0392b',
        'Adult-Only Gap': '#f39c12',
        'Peds-Only Gap': '#e74c3c',
        'Both Adult & Peds': '#27ae60',
    }
    
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = [color_map_ref.get(s, '#3498db') for s in merged_ref['burn_coverage_status']]
    bars = ax.barh(merged_ref['origin_state'], merged_ref['estimated_distance_km'],
                   color=colors, edgecolor='white', linewidth=1)
    
    for bar, row in zip(bars, merged_ref.itertuples()):
        ax.text(bar.get_width() + 10, bar.get_y() + bar.get_height()/2,
                f"{row.estimated_distance_km:.0f} km → {row.recommended_hub_state}",
                va='center', fontsize=9)
    
    ax.set_xlabel('Estimated Distance to Nearest Adult Burn Hub (km)', fontsize=11)
    ax.set_title('Referral Distance Burden for States Without Adult Burn Centers\n(Root Cause of Real-Time Referral Delays)', 
                fontsize=12, fontweight='bold')
    ax.set_xlim(0, max(merged_ref['estimated_distance_km']) * 1.3)
    ax.yaxis.set_tick_params(labelsize=11)
    ax.spines[['top','right']].set_visible(False)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(axis='x', alpha=0.4)
    
    patches = [mpatches.Patch(color=c, label=l) for l, c in color_map_ref.items() if l in merged_ref['burn_coverage_status'].values]
    ax.legend(handles=patches, loc='lower right', fontsize=9)
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_referral_delay_distance.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_referral_delay_distance.png")


def figure_mismatch_vs_fatality(state_burn_fatal):
    """Scatter: mismatch states with fatality rate markers."""
    df_plot = state_burn_fatal.dropna(subset=['crude_rate'])
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    color_map = {
        'Both Adult & Peds': '#27ae60',
        'Adult-Only Gap': '#f39c12',
        'Peds-Only Gap': '#e74c3c',
        'No Burn Center': '#c0392b',
    }
    marker_map = {
        'Both Adult & Peds': 'o',
        'Adult-Only Gap': 's',
        'Peds-Only Gap': '^',
        'No Burn Center': 'X',
    }
    
    for status, grp in df_plot.groupby('burn_coverage_status'):
        ax.scatter(grp.index, grp['crude_rate'],
                   color=color_map.get(status, '#95a5a6'),
                   marker=marker_map.get(status, 'o'),
                   s=120, label=status, zorder=3, edgecolors='black', linewidths=0.5)
    
    # Add labels for gap/mismatch states
    highlight = df_plot[df_plot['burn_coverage_status'].isin(['No Burn Center','Adult-Only Gap'])]
    for _, row in highlight.iterrows():
        ax.annotate(row['STATE'], (row.name, row['crude_rate']),
                   textcoords='offset points', xytext=(5, 5), fontsize=8, fontweight='bold')
    
    # National average line
    nat_avg = df_plot['crude_rate'].mean()
    ax.axhline(nat_avg, color='navy', linestyle='--', linewidth=1.2, alpha=0.7, label=f'Nat. Avg ({nat_avg:.2f}/100k)')
    
    ax.set_ylabel('Burn Fatality Rate (per 100k)', fontsize=12)
    ax.set_title('Burn Fatality Rate by State Burn Coverage Status\n(Mismatch States Show Elevated Mortality)', 
                fontsize=13, fontweight='bold')
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.spines[['top','right']].set_visible(False)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=10, framealpha=0.9)
    ax.set_xticks([])
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_mismatch_vs_fatality.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_mismatch_vs_fatality.png")


def figure_peds_referral_states(state_burn):
    """Bar chart showing states needing pediatric burn referral (12 states)."""
    peds_ref = state_burn[state_burn['child_burn_referral_needed']].copy()
    peds_ref = peds_ref.sort_values('adult_burn_centers', ascending=False)
    
    colors = ['#f39c12' if s == 'Adult-Only Gap' else '#c0392b' 
              for s in peds_ref['burn_coverage_status']]
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(peds_ref['STATE'], peds_ref['adult_burn_centers'],
                   color=colors, edgecolor='white', linewidth=1)
    
    # Annotations
    for bar, row in zip(bars, peds_ref.itertuples()):
        label = f"Adult centers: {int(row.adult_burn_centers)}" if row.adult_burn_centers > 0 else "NO burn centers"
        ax.text(max(bar.get_width(), 0.05) + 0.05, bar.get_y() + bar.get_height()/2,
                label, va='center', fontsize=9)
    
    ax.set_xlabel('Number of Adult Burn Centers (Peds burn centers = 0 for all)', fontsize=10)
    ax.set_title('States Where Children Must Be Referred Out-of-State for Burn Care\n(12 States with No Pediatric Burn Center)', 
                fontsize=12, fontweight='bold')
    ax.set_xlim(0, peds_ref['adult_burn_centers'].max() + 2)
    ax.spines[['top','right']].set_visible(False)
    ax.set_facecolor('#f8f9fa')
    fig.patch.set_facecolor('#ffffff')
    ax.grid(axis='x', alpha=0.3)
    
    orange = mpatches.Patch(color='#f39c12', label='Adult-Only Gap (children must travel)')
    red = mpatches.Patch(color='#c0392b', label='No Burn Center (all patients must travel)')
    ax.legend(handles=[orange, red], fontsize=9, loc='lower right')
    
    fig.tight_layout()
    fig.savefig(FIGURES / "narr_ea_peds_referral_states.png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("Saved: narr_ea_peds_referral_states.png")


def print_summary_stats(state_burn, state_burn_fatal, referral):
    print("\n" + "="*60)
    print("FINAL SUMMARY STATISTICS FOR REPORT")
    print("="*60)
    
    print(f"\n1. FACILITY-LEVEL BURN MISMATCH:")
    print(f"   - Total facilities with burn capability: {(state_burn['adult_burn_centers'].sum()+state_burn['peds_burn_centers'].sum()):.0f} center-slots")
    
    print(f"\n2. STATE-LEVEL MISMATCH:")
    vc = state_burn['burn_coverage_status'].value_counts()
    for k,v in vc.items():
        print(f"   - {k}: {v} states")
    
    print(f"\n3. REFERRAL BURDEN:")
    print(f"   - States with NO adult burn center (need adult referral): {state_burn['adult_burn_referral_needed'].sum()}")
    print(f"     States: {state_burn[state_burn['adult_burn_referral_needed']]['STATE'].tolist()}")
    print(f"   - States with NO peds burn center (need child referral): {state_burn['child_burn_referral_needed'].sum()}")
    print(f"     States: {state_burn[state_burn['child_burn_referral_needed']]['STATE'].tolist()}")
    
    print(f"\n4. REFERRAL DISTANCES (Adult Burn):")
    print(referral.to_string(index=False))
    avg_dist = referral['estimated_distance_km'].mean()
    print(f"   Average referral distance: {avg_dist:.1f} km")
    print(f"   Max referral distance: {referral['estimated_distance_km'].max():.1f} km (AK → WA)")
    
    print(f"\n5. MISMATCH + FATALITY CORRELATION:")
    if 'crude_rate' in state_burn_fatal.columns:
        both = state_burn_fatal[state_burn_fatal['burn_coverage_status'] == 'Both Adult & Peds']['crude_rate'].mean()
        gap = state_burn_fatal[state_burn_fatal['burn_coverage_status'].isin(['Adult-Only Gap','No Burn Center'])]['crude_rate'].mean()
        print(f"   - Avg fatality rate (Both A+P states): {both:.2f}/100k")
        print(f"   - Avg fatality rate (Mismatch/No-burn states): {gap:.2f}/100k")
        print(f"   - Ratio: {gap/both:.1f}x higher in mismatch/gap states")


if __name__ == "__main__":
    state_burn, df = build_mismatch_analysis()
    state_burn_fatal = merge_with_fatality(state_burn)
    referral, metrics = load_referral_and_metrics()
    
    figure_burn_coverage_status(state_burn)
    figure_mismatch_state_map(state_burn)
    figure_referral_delay_distance(referral, state_burn)
    figure_mismatch_vs_fatality(state_burn_fatal)
    figure_peds_referral_states(state_burn)
    
    print_summary_stats(state_burn, state_burn_fatal, referral)
    
    # Save comprehensive mismatch data
    state_burn_fatal.to_csv(OUTPUTS / "burn_mismatch_by_state.csv", index=False)
    print("\nSaved: outputs/burn_mismatch_by_state.csv")
