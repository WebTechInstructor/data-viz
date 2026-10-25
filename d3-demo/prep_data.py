"""Step 0: export a tidy, incident-level CSV (title kept for tooltips) for the D3 demo.

Source: IFSC 54503 cleaned workbook, sheet Incidents_2018_2025 (1,289 incidents).
D3 does the aggregation in the browser, so we keep one row per incident.
Missing MIT classifications are encoded explicitly as "Not classified".
"""
import pandas as pd

SRC = "AIID_2018-2025_visualization_ready_with_samples.xlsx"
df = pd.read_excel(SRC, sheet_name="Incidents_2018_2025")

assert df["incident_id"].is_unique, "incident_id must be unique (one row per incident)"

out = df[["incident_id", "year", "title", "risk_domain", "intent"]].copy()
out[["risk_domain", "intent"]] = out[["risk_domain", "intent"]].fillna("Not classified")
out = out.sort_values(["year", "incident_id"])
out.to_csv("data/aiid_incidents_2018_2025.csv", index=False)

print(len(out), "rows written")
print(out.groupby("year").size().to_dict())
