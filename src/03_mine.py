"""
03_mine.py
----------
Stage 4: Data Mining
Applies K-Means clustering and linear regression to the cleaned dataset.

Inputs:
  data/processed/cleaned_main.csv

Outputs:
  data/processed/clustered.csv            (merged + cluster assignments)
  figures/fig_elbow.png
  figures/fig_clusters_scatter.png
  figures/fig_clusters_profile.png
  figures/fig_regression_coeffs.png
  figures/fig_regression_actual_vs_pred.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.decomposition import PCA
import warnings
import os

warnings.filterwarnings("ignore")
os.makedirs("figures", exist_ok=True)

df = pd.read_csv("data/processed/cleaned_main.csv")
sns.set_theme(style="whitegrid", font_scale=1.1)
PALETTE = {"Low": "#2ecc71", "Medium": "#f39c12", "High": "#e74c3c"}

# ── TECHNIQUE A: K-Means Clustering ──────────────────────────────────────────
print("=" * 60)
print("TECHNIQUE A: K-MEANS CLUSTERING")
print("=" * 60)

# Features for clustering
cluster_features = ["automation_prob", "adaptive_capacity_score",
                    "wage_norm", "edu_norm"]
cluster_df = df[cluster_features + ["occupation", "risk_tier",
                                     "emp_change_pct", "occupation_group",
                                     "education_required", "median_wage_2024"]].dropna()

X = cluster_df[cluster_features].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Elbow method to find optimal k
inertias = []
K_range = range(2, 10)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(K_range, inertias, "o-", color="#3498db", linewidth=2, markersize=7)
ax.axvline(x=4, color="#e74c3c", linestyle="--", label="Chosen k=4")
ax.set_title("Elbow Method — Optimal Number of Clusters", fontweight="bold")
ax.set_xlabel("Number of Clusters (k)")
ax.set_ylabel("Inertia (Within-Cluster Sum of Squares)")
ax.legend()
plt.tight_layout()
fig.savefig("figures/fig_elbow.png", dpi=150)
plt.close()
print("Saved fig_elbow.png")

# Fit final model with k=4
k_optimal = 4
km = KMeans(n_clusters=k_optimal, random_state=42, n_init=10)
cluster_df = cluster_df.copy()
cluster_df["cluster"] = km.fit_predict(X_scaled)

# Label clusters by their profile
cluster_profiles = cluster_df.groupby("cluster")[
    ["automation_prob", "adaptive_capacity_score", "emp_change_pct"]
].mean().round(3)
print("\nCluster profiles (means):")
print(cluster_profiles)

# Name clusters based on their characteristics
cluster_names = {}
for c, row in cluster_profiles.iterrows():
    if row["automation_prob"] > 0.6 and row["adaptive_capacity_score"] < 0.4:
        cluster_names[c] = "High Risk / Low Resilience"
    elif row["automation_prob"] > 0.6 and row["adaptive_capacity_score"] >= 0.4:
        cluster_names[c] = "High Risk / High Resilience"
    elif row["automation_prob"] <= 0.6 and row["adaptive_capacity_score"] >= 0.5:
        cluster_names[c] = "Low Risk / High Skill"
    else:
        cluster_names[c] = "Low Risk / Stable"

cluster_df["cluster_label"] = cluster_df["cluster"].map(cluster_names)
print("\nCluster labels assigned:")
print(cluster_df["cluster_label"].value_counts())

# PCA for 2D visualization
pca = PCA(n_components=2, random_state=42)
coords = pca.fit_transform(X_scaled)
cluster_df["pca_1"] = coords[:, 0]
cluster_df["pca_2"] = coords[:, 1]

CLUSTER_COLORS = {
    "High Risk / Low Resilience":  "#e74c3c",
    "High Risk / High Resilience": "#e67e22",
    "Low Risk / High Skill":       "#2ecc71",
    "Low Risk / Stable":           "#3498db",
}

fig, ax = plt.subplots(figsize=(10, 7))
for label, grp in cluster_df.groupby("cluster_label"):
    ax.scatter(grp["pca_1"], grp["pca_2"],
               label=label, alpha=0.55, s=25,
               color=CLUSTER_COLORS.get(label, "gray"))
ax.set_title("K-Means Clusters (PCA 2D Projection)", fontweight="bold")
ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)")
ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)")
ax.legend(title="Cluster", loc="best")
plt.tight_layout()
fig.savefig("figures/fig_clusters_scatter.png", dpi=150)
plt.close()
print("Saved fig_clusters_scatter.png")

# Cluster profile chart
profile_means = cluster_df.groupby("cluster_label")[
    ["automation_prob", "adaptive_capacity_score"]
].mean()

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
profile_means["automation_prob"].sort_values().plot(
    kind="barh", ax=axes[0], color="#e74c3c", alpha=0.8)
axes[0].set_title("Avg Automation Probability by Cluster", fontweight="bold")
axes[0].set_xlabel("Automation Probability")
axes[0].axvline(0.5, color="gray", linestyle="--", linewidth=0.8)

profile_means["adaptive_capacity_score"].sort_values().plot(
    kind="barh", ax=axes[1], color="#3498db", alpha=0.8)
axes[1].set_title("Avg Adaptive Capacity Score by Cluster", fontweight="bold")
axes[1].set_xlabel("Adaptive Capacity Score (0–1)")

plt.tight_layout()
fig.savefig("figures/fig_clusters_profile.png", dpi=150)
plt.close()
print("Saved fig_clusters_profile.png")

# Save clustered data
out = df.merge(
    cluster_df[["occupation", "cluster", "cluster_label", "pca_1", "pca_2"]],
    on="occupation", how="left"
)
out.to_csv("data/processed/clustered.csv", index=False)
print("Saved clustered.csv")

# ── TECHNIQUE B: Linear Regression ───────────────────────────────────────────
print("\n" + "=" * 60)
print("TECHNIQUE B: LINEAR REGRESSION")
print("=" * 60)

# Target: emp_change_pct
# Features: automation_prob, adaptive_capacity_score, wage_norm, edu_norm
# + occupation group dummies

reg_df = df[["emp_change_pct", "automation_prob", "adaptive_capacity_score",
             "wage_norm", "edu_norm", "occupation_group"]].dropna()

# One-hot encode occupation group
dummies = pd.get_dummies(reg_df["occupation_group"], prefix="grp", drop_first=True)
X_reg = pd.concat([
    reg_df[["automation_prob", "adaptive_capacity_score", "wage_norm", "edu_norm"]],
    dummies
], axis=1)
y_reg = reg_df["emp_change_pct"]

X_train, X_test, y_train, y_test = train_test_split(
    X_reg, y_reg, test_size=0.2, random_state=42
)

model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2  = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

print(f"\nR²:  {r2:.4f}")
print(f"MAE: {mae:.4f} percentage points")

# Key coefficients (non-dummy features only)
key_features = ["automation_prob", "adaptive_capacity_score", "wage_norm", "edu_norm"]
coef_df = pd.DataFrame({
    "feature": key_features,
    "coefficient": model.coef_[:len(key_features)],
}).sort_values("coefficient")

print("\nKey coefficients:")
print(coef_df.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Coefficient plot
colors = ["#e74c3c" if c < 0 else "#2ecc71" for c in coef_df["coefficient"]]
axes[0].barh(coef_df["feature"], coef_df["coefficient"], color=colors, alpha=0.85)
axes[0].axvline(0, color="black", linewidth=0.8)
axes[0].set_title("Regression Coefficients\n(Effect on Projected Employment Change %)",
                  fontweight="bold")
axes[0].set_xlabel("Coefficient Value")

# Actual vs. predicted
axes[1].scatter(y_test, y_pred, alpha=0.4, s=15, color="#3498db")
lims = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
axes[1].plot(lims, lims, "r--", linewidth=1, label="Perfect fit")
axes[1].set_title(f"Actual vs. Predicted Employment Change\n(R² = {r2:.3f})",
                  fontweight="bold")
axes[1].set_xlabel("Actual (%)")
axes[1].set_ylabel("Predicted (%)")
axes[1].legend()

plt.tight_layout()
fig.savefig("figures/fig_regression.png", dpi=150)
plt.close()
print("Saved fig_regression.png")

print("\nData mining complete.")
