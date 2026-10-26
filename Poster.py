#!/usr/bin/env python
# coding: utf-8

# In[1]:


"""
Do people who trust automation drive differently?
ISOM 675 Final Project - Yerim Mo

Data: Miles & Strybel (2020), Harvard Dataverse
https://doi.org/10.7910/DVN/BWCCET

Run with the three CSVs in this folder. Writes the poster PDF.
"""

import numpy as np
import pandas as pd
import altair as alt

BLUE, ORANGE, RED = "#2a78d6", "#eb6834", "#e34948"
INK, MUTED, GRID = "#0b0b0b", "#898781", "#e1e0d9"

OUT = "Yerim Mo_Data Visualization_Final Project.pdf"

demo = pd.read_csv("Demo_and_Trust_Questionaire_.csv")
tlx = pd.read_csv("Workload_Measure_TLX_.csv")
drive = pd.read_csv("Driver_performance_of_obstacle_maneuvers_.csv",
                    encoding="utf-8-sig")


# In[2]:


# Subscale scores, only when every item was answered
trust_items = ["2", "3", "4", "5"]
views_items = ["9", "10", "11", "12"]
demo["trust"] = demo[trust_items].mean(axis=1).where(
    demo[trust_items].notna().all(axis=1))
demo["views"] = demo[views_items].mean(axis=1).where(
    demo[views_items].notna().all(axis=1))

# Cols 25/26 are the manual and automated TLX means
work = tlx[["Subject", "25", "26"]].copy()
work.columns = ["subject", "tlx_manual", "tlx_auto"]

# Per-subject driving behaviour by mode
drive = drive.dropna(subset=["subject"])
drive["mode"] = drive["carMode"].map({"Manual-Driving": "Manual",
                                      "Self-Driving": "Takeover"})
beh = drive.pivot_table(index="subject", columns="mode",
                        values=["InitSpeed", "Wronglane"], aggfunc="mean")
beh.columns = [f"{v.lower()}_{m.lower()}" for v, m in beh.columns]
beh = beh.reset_index()
beh["subject"] = beh["subject"].astype(int)

# One row per subject
sub = (demo[["Subject", "trust", "views"]]
       .rename(columns={"Subject": "subject"})
       .merge(work, on="subject")
       .merge(beh, on="subject"))

# Long formats for the faceted charts
wl = sub.melt(id_vars=["subject", "trust"],
              value_vars=["tlx_auto", "tlx_manual"],
              var_name="condition", value_name="workload")
wl["condition"] = wl["condition"].map({"tlx_auto": "Take-over",
                                       "tlx_manual": "Manual"})

wr = sub.melt(id_vars=["subject"],
              value_vars=["wronglane_manual", "wronglane_takeover"],
              var_name="condition", value_name="rate")
wr["condition"] = wr["condition"].map({"wronglane_manual": "Manual",
                                       "wronglane_takeover": "Take-over"})


# In[3]:


# 1. Trust vs workload when control is handed back
tk = wl[wl["condition"] == "Take-over"]
r1 = tk["trust"].corr(tk["workload"])

base1 = alt.Chart().encode(
    x=alt.X("trust:Q", title="Trust in the automation (items 2-5)",
            scale=alt.Scale(domain=[1, 6])),
    y=alt.Y("workload:Q", title="NASA-TLX workload (0-100)",
            scale=alt.Scale(domain=[0, 100])),
)
chart1 = alt.layer(
    base1.mark_circle(size=80, opacity=0.7, color=ORANGE),
    base1.transform_regression("trust", "workload").mark_line(
        size=2.5, color=ORANGE),
    data=tk,
).properties(
    width=250, height=250,
    title=alt.Title("Drivers who trust the system find the hand-off easier",
                    subtitle=f"r = {r1:+.2f}   n = {len(tk)}",
                    anchor="start", fontSize=13, subtitleFontSize=11,
                    subtitleColor=MUTED))

# 2. Views vs chosen speed in manual driving
sp = sub.dropna(subset=["views", "initspeed_manual"])
r2 = sp["views"].corr(sp["initspeed_manual"])

base2 = alt.Chart().encode(
    x=alt.X("views:Q", title="Views of automation (items 9-12)",
            scale=alt.Scale(domain=[1, 6])),
    y=alt.Y("initspeed_manual:Q", title="Initial speed, manual driving",
            scale=alt.Scale(domain=[70, 102])),
)
chart2 = alt.layer(
    base2.mark_circle(size=80, opacity=0.7, color=BLUE),
    base2.transform_regression("views", "initspeed_manual").mark_line(
        size=2.5, color=BLUE),
    data=sp,
).properties(
    width=250, height=250,
    title=alt.Title("Enthusiasts drive faster when they drive themselves",
                    subtitle=f"r = {r2:+.2f}   n = {len(sp)}",
                    anchor="start", fontSize=13, subtitleFontSize=11,
                    subtitleColor=MUTED))

# 3. Distribution of wrong-lane rates
chart3 = alt.Chart(wr).mark_bar().encode(
    x=alt.X("rate:Q", bin=alt.Bin(step=0.05, extent=[0, 0.8]),
            title="Share of obstacles taken in the wrong lane"),
    y=alt.Y("count():Q", title="Drivers", axis=alt.Axis(format="d")),
    color=alt.Color("condition:N",
                    scale=alt.Scale(domain=["Take-over", "Manual"],
                                    range=[ORANGE, BLUE]),
                    legend=None),
).properties(width=250, height=130).facet(
    row=alt.Row("condition:N", title=None, sort=["Manual", "Take-over"],
                header=alt.Header(labelOrient="top", labelAngle=0,
                                  labelAnchor="start", labelFontSize=12,
                                  labelFontWeight=600, labelColor=INK)),
).properties(
    title=alt.Title("Automation erased the differences between drivers",
                    subtitle="Each bar counts drivers; n = 33",
                    anchor="start", fontSize=13, subtitleFontSize=11,
                    subtitleColor=MUTED))


# In[5]:


# 4. How the questionnaire items relate to each other
items = [str(i) for i in range(1, 17)]
order = ["5", "4", "2", "3", "7", "13", "12", "10", "11",
         "9", "16", "15", "8", "1", "6", "14"]

q33 = demo[demo["Subject"].isin(sub["subject"])]
cm = q33[items].corr().mask(np.eye(16, dtype=bool))
cm.index.name = "item_y"
hm = (cm.reset_index()
        .melt(id_vars="item_y", var_name="item_x", value_name="r")
        .dropna())

chart4 = alt.Chart(hm).mark_rect().encode(
    x=alt.X("item_x:O", sort=order, title="Questionnaire item"),
    y=alt.Y("item_y:O", sort=order, title=None),
    color=alt.Color("r:Q",
                    scale=alt.Scale(domain=[-1, 0, 1],
                                    range=[BLUE, "#f0efec", RED],
                                    interpolate="lab"),
                    legend=alt.Legend(title="r", direction="horizontal",
                                      orient="bottom", gradientLength=120)),
).properties(
    width=300, height=300,
    title=alt.Title("The questionnaire splits into two blocks",
                    subtitle="Items 2-5 = trust in the system; 9-13, 16 = views of automation; n = 33",
                    anchor="start", fontSize=13, subtitleFontSize=11,
                    subtitleColor=MUTED))

# 5. Each scale predicts a different outcome
cells = []
for pred in ["trust", "views"]:
    for col, lab in [("tlx_auto", "Workload when handed control"),
                     ("initspeed_manual", "Speed chosen when driving")]:
        d = sub[[pred, col]].dropna()
        cells.append({"predictor": pred, "outcome": lab,
                      "r": d[pred].corr(d[col]), "n": len(d)})
cells = pd.DataFrame(cells)

chart5 = alt.layer(
    alt.Chart().mark_rule(color=MUTED, size=1).encode(x=alt.datum(0)),
    alt.Chart().mark_bar(height=16, color=INK, opacity=0.85).encode(
        x=alt.X("r:Q", title="Correlation with the outcome",
                scale=alt.Scale(domain=[-0.6, 0.6])),
        y=alt.Y("predictor:N", title=None, sort=["trust", "views"])),
    data=cells,
).properties(width=440, height=110).facet(
    row=alt.Row("outcome:N", title=None,
                sort=["Workload when handed control",
                      "Speed chosen when driving"],
                header=alt.Header(labelOrient="top", labelAngle=0,
                                  labelAnchor="start", labelFontSize=12,
                                  labelFontWeight=600, labelColor=INK)),
).properties(
    title=alt.Title("Trust and enthusiasm predict different things",
                    subtitle="r = +0.29 between the two scales, so they are not the same measure",
                    anchor="start", fontSize=13, subtitleFontSize=11,
                    subtitleColor=MUTED))

# Assemble and export
poster = alt.vconcat(
    alt.hconcat(chart1, chart2, chart3, spacing=34),
    alt.hconcat(chart4, chart5, spacing=34),
    spacing=24
).properties(
    title=alt.Title(
        "Do people who trust automation drive differently?",
        subtitle=[
            "Trust changes how the drive feels and how fast drivers choose to go - but not how well they avoid obstacles.",
            "Trust = items 2-5 (dependable / reliable / can trust).   Views = items 9-12 (enjoyable / easier / frees me up).   Orange = control handed back, blue = manual.",
            "Driving simulator, 33 drivers, 8 tracks, 792 obstacle encounters.   Yerim Mo",
            "Data: Miles & Strybel (2020), Harvard Dataverse.  https://doi.org/10.7910/DVN/BWCCET",
        ],
        anchor="start", fontSize=20, subtitleFontSize=11.5,
        subtitleColor=MUTED, offset=10)
).configure_view(
    stroke=None
).configure_axis(
    grid=True, gridColor=GRID, gridWidth=0.8,
    domainColor="#c3c2b7", tickColor="#c3c2b7",
    labelColor="#52514e", titleColor=INK,
    labelFontSize=10.5, titleFontSize=11
).configure_legend(
    labelColor="#52514e", titleColor=INK
).configure_title(
    color=INK
).configure(
    background="#ffffff"
)

poster.save(OUT)
print(f"saved {OUT}")


# In[ ]:




