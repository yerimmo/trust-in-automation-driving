# Does Trust in Automation Change How People Drive?

Everyone asks whether self-driving cars are safer. I asked something smaller: does what a driver *believes* about automation show up in how they actually drive?

📊 **[View the poster](Poster.pdf)** | 📓 **[View the notebook](Analysis.ipynb)**

## Data

Public replication data from a driving-simulator study on Harvard Dataverse ([doi:10.7910/DVN/BWCCET](https://doi.org/10.7910/DVN/BWCCET)): 33 drivers, 794 obstacle encounters, a 16-item automation questionnaire, and NASA-TLX workload ratings.

## Key Findings

- **Trust changes how the drive feels.** Drivers who trust the system find the take-over hand-off less mentally demanding.
- **Views change what people choose.** Drivers with positive views of automation chose faster speeds when driving manually, with no automation involved.
- **Trust does not change performance.** Trust did not predict wrong-lane errors once outliers were checked.

## EDA Decisions

- **Questioned a column name.** `Self-Driving` turned out to be a take-over condition, not the car driving itself, so both conditions are human maneuvers.
- **Checked whether missing data was random.** All 84 wrong-lane maneuvers had blank time-to-collision, so speed results describe successful maneuvers only.
- **Verified before trusting.** Confirmed unnamed workload columns by recomputing them, and replicated the source paper's published correlations from the raw files.
- **Dropped a chart that did not work.** The original manual vs. take-over comparison differed in scatter, not slope, which readers cannot see side by side.
- **Stress-tested a correlation.** The trust and wrong-lane correlation fell from -0.35 to -0.11 after removing four high-error drivers.
- **Let the data confirm the subscales.** Clustering all 16 questionnaire items reproduced the report's trust and views groupings.

## Limitations

- Speed units are not labeled in the data, and half of manual maneuvers sit at the simulator's speed cap of 100.
- The source report analyzed 32 participants; the public files contain 33.
- The report's text and table disagree on which items form the trust scale.

## Tools

Python · pandas · Altair

*Final project for ISOM 675 Data Visualization, Emory University, Fall 2026.*
