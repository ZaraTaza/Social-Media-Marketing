# 1. Load libraries and dataset
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

pd.set_option('display.width', 120)

events = pd.read_csv("ad_events.csv", parse_dates=["timestamp"])
print("Shape:", events.shape)
print(events.dtypes)
print(events.isna().sum())
print(events['event_type'].value_counts())

conn = sqlite3.connect("ad_campaign_db.sqlite")

# 2. Funnel Analysis with SQL

DEPTHS_CTE = """
WITH depths AS (
    SELECT user_id, ad_id,
        CASE event_type
            WHEN 'Impression' THEN 1 WHEN 'Click' THEN 2 WHEN 'Like' THEN 3
            WHEN 'Comment' THEN 4 WHEN 'Share' THEN 5 WHEN 'Purchase' THEN 6
        END AS stage_depth
    FROM ad_events
),
pair_depths AS (
    SELECT user_id, ad_id, MAX(stage_depth) AS max_depth
    FROM depths GROUP BY user_id, ad_id
)
"""
 
# Overall funnel: counts + percentages at each stage
funnel_query = DEPTHS_CTE + """
SELECT
    SUM(CASE WHEN max_depth >= 1 THEN 1 ELSE 0 END) AS impression,
    SUM(CASE WHEN max_depth >= 2 THEN 1 ELSE 0 END) AS click,
    SUM(CASE WHEN max_depth >= 3 THEN 1 ELSE 0 END) AS like_,
    SUM(CASE WHEN max_depth >= 4 THEN 1 ELSE 0 END) AS comment,
    SUM(CASE WHEN max_depth >= 5 THEN 1 ELSE 0 END) AS share,
    SUM(CASE WHEN max_depth >= 6 THEN 1 ELSE 0 END) AS purchase,
    SUM(CASE WHEN max_depth >= 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_impression,
    SUM(CASE WHEN max_depth >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_click,
    SUM(CASE WHEN max_depth >= 3 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_like,
    SUM(CASE WHEN max_depth >= 4 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_comment,
    SUM(CASE WHEN max_depth >= 5 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_share,
    SUM(CASE WHEN max_depth >= 6 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_purchase
FROM pair_depths;
"""
funnel = pd.read_sql_query(funnel_query, conn)
print("\n=== OVERALL FUNNEL ===")
print(funnel)
 
# Day-of-week check 
dow_query = """
SELECT day_of_week, COUNT(*) AS day_count
FROM ad_events
GROUP BY day_of_week
ORDER BY day_count DESC;
"""
print("\n=== EVENTS BY DAY OF WEEK ===")
print(pd.read_sql_query(dow_query, conn))

# 3. Segemntation (platform, ad_type, country, age_group)

SEGMENT_TEMPLATE = DEPTHS_CTE + """
SELECT
    {segment_col} AS segment,
    COUNT(*) AS total_pairs,
    SUM(CASE WHEN pd.max_depth >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_click,
    SUM(CASE WHEN pd.max_depth >= 6 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) AS pct_purchase
FROM pair_depths pd
{join_clause}
GROUP BY {segment_col};
"""
 
segments = {
    "Platform": ("a.ad_platform", "JOIN ads a ON pd.ad_id = a.ad_id"),
    "Ad type": ("a.ad_type", "JOIN ads a ON pd.ad_id = a.ad_id"),
    "Country": ("u.country", "JOIN users u ON pd.user_id = u.user_id"),
    "Age group": ("u.age_group", "JOIN users u ON pd.user_id = u.user_id"),
}
 
segment_results = {}
for label, (col, join_clause) in segments.items():
    q = SEGMENT_TEMPLATE.format(segment_col=col, join_clause=join_clause)
    df = pd.read_sql_query(q, conn)
    segment_results[label] = df
    print(f"\n=== FUNNEL BY {label.upper()} ===")
    print(df)

# 4. Campaign efficency (note: campaigns #16 and #43 have zero ads, verified via LEFT JOIN, and
#    are excluded here since an inner JOIN naturally drops unmatched rows)

missing_campaigns_query = """
SELECT c.campaign_id, c.name, COUNT(a.ad_id) AS num_ads
FROM campaigns c
LEFT JOIN ads a ON c.campaign_id = a.campaign_id
GROUP BY c.campaign_id, c.name
HAVING num_ads = 0;
"""
print("\n=== CAMPAIGNS WITH NO ADS (excluded from efficiency analysis) ===")
print(pd.read_sql_query(missing_campaigns_query, conn))
 
campaign_query = DEPTHS_CTE + """
SELECT
    c.campaign_id,
    c.name,
    c.total_budget,
    COUNT(*) AS total_pairs,
    SUM(CASE WHEN pd.max_depth >= 6 THEN 1 ELSE 0 END) AS total_purchases,
    c.total_budget / SUM(CASE WHEN pd.max_depth >= 6 THEN 1 ELSE 0 END) AS cost_per_purchase
FROM pair_depths pd
JOIN ads a ON pd.ad_id = a.ad_id
JOIN campaigns c ON a.campaign_id = c.campaign_id
GROUP BY c.campaign_id, c.name, c.total_budget
ORDER BY cost_per_purchase;
"""
campaign_efficiency = pd.read_sql_query(campaign_query, conn)
print("\n=== CAMPAIGN EFFICIENCY (sorted, cheapest first) ===")
print(campaign_efficiency)

# 5. Weekly time trend 

weekly_query = """
SELECT
    strftime('%Y-%W', timestamp) AS year_week,
    COUNT(*) AS event_count,
    SUM(CASE WHEN event_type = 'Impression' THEN 1 ELSE 0 END) AS total_impressions,
    SUM(CASE WHEN event_type = 'Click' THEN 1 ELSE 0 END) AS total_clicks,
    SUM(CASE WHEN event_type = 'Purchase' THEN 1 ELSE 0 END) AS total_purchases
FROM ad_events
GROUP BY year_week
ORDER BY year_week;
"""
weekly_trend = pd.read_sql_query(weekly_query, conn)
print("\n=== WEEKLY TREND ===")
print(weekly_trend)

# 6. Engagement vs Purchase 

raw_events = pd.read_sql_query("SELECT user_id, ad_id, event_type FROM ad_events", conn)
 
event_sets = raw_events.groupby(['user_id', 'ad_id'])['event_type'].apply(set).reset_index()
event_sets.columns = ['user_id', 'ad_id', 'events']
 
event_sets['clicked'] = event_sets['events'].apply(lambda s: 'Click' in s)
event_sets['purchased'] = event_sets['events'].apply(lambda s: 'Purchase' in s)
event_sets['engaged'] = event_sets['events'].apply(lambda s: bool(s & {'Like', 'Comment', 'Share'}))
 
clickers = event_sets[event_sets['clicked']]
engagement_purchase_rate = clickers.groupby('engaged')['purchased'].mean() * 100
 
print("\n=== PURCHASE RATE AMONG CLICKERS, BY ENGAGEMENT ===")
print(engagement_purchase_rate)
print(f"Total clickers: {len(clickers)}")
print(f"Engaged clickers: {clickers['engaged'].sum()} ({clickers['engaged'].mean()*100:.1f}%)")

# 7. Vsiusalisations
# Funnel chart

stages = ['Impression', 'Click', 'Like', 'Comment', 'Share', 'Purchase']
counts = [funnel[c].iloc[0] for c in ['impression', 'click', 'like_', 'comment', 'share', 'purchase']]
 
fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.barh(stages, counts, color='#4C72B0')
for bar, count in zip(bars, counts):
    pct = count / counts[0] * 100
    ax.text(count + 5000, bar.get_y() + bar.get_height() / 2,
            f"{count:,} ({pct:.1f}%)", va='center', fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('User-Ad Pairs')
ax.set_title('Ad Engagement Funnel: Impression → Purchase', fontsize=13, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('funnel_chart.png', dpi=150)
plt.show()
 
# Comparison by country chart
country_df = segment_results['Country'].sort_values('pct_purchase', ascending=False)
 
fig, ax = plt.subplots(figsize=(9, 5))
ax.bar(country_df['segment'], country_df['pct_purchase'], color='#4C72B0')
ax.set_ylabel('Purchase Rate (%)')
ax.set_title('Purchase Rate by Country', fontsize=13, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('country_chart.png', dpi=150)
plt.show()

# Camapign efficiency chart
top_bottom = pd.concat([campaign_efficiency.head(5), campaign_efficiency.tail(5)])
 
fig, ax = plt.subplots(figsize=(9, 6))
colors = ['#4C72B0'] * 5 + ['#C44E52'] * 5
ax.barh(top_bottom['name'], top_bottom['cost_per_purchase'], color=colors)
ax.invert_yaxis()
ax.set_xlabel('Cost per Purchase ($)')
ax.set_title('Campaign Efficiency: 5 Best vs 5 Worst', fontsize=13, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
plt.savefig('campaign_efficiency_chart.png', dpi=150)
plt.show()

# Weekly trend chart (excluding partial edge weeks)

trend_plot = weekly_trend.iloc[1:-1]  # drop first/last partial weeks
 
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(trend_plot['year_week'], trend_plot['total_clicks'], marker='o', label='Clicks')
ax.plot(trend_plot['year_week'], trend_plot['total_purchases'] * 20, marker='o', label='Purchases (x20 scale)')
ax.set_xlabel('Week')
ax.set_ylabel('Count')
ax.set_title('Weekly Clicks & Purchases (partial edge weeks excluded)', fontsize=13, fontweight='bold')
ax.spines[['top', 'right']].set_visible(False)
plt.xticks(rotation=45)
ax.legend()
plt.tight_layout()
plt.savefig('weekly_trend_chart.png', dpi=150)
plt.show()
 
conn.close()
print("\nDone. Charts saved: funnel_chart.png, country_chart.png, "
      "campaign_efficiency_chart.png, weekly_trend_chart.png")
 
