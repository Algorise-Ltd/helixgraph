## Risk Scoring Model

The supplier risk score is a value between 0 and 100, calculated from four factors. Each factor is assigned a score, and the final score is a weighted average of the factor scores.

### Risk Factors

#### 1. Country Risk (Weight: 30%)
- **Description:** Assesses the risk associated with the supplier's country of operation.
- **Scoring Logic:**
  - **High-Risk Countries:** Countries with significant political instability, sanctions, or poor economic outlook. (e.g., a predefined list of countries).
  - **Medium-Risk Countries:** Countries with moderate political or economic risks.
  - **Low-Risk Countries:** Politically stable countries with strong economies.
- **Point Allocation:**
  - High Risk: 30 points
  - Medium Risk: 15 points
  - Low Risk: 0 points

#### 2. Single Sourcing Risk (Weight: 25%)
- **Description:** Evaluates dependence on a single supplier for critical materials or services. This measure is calculated based on the number of critical items that are single-sourced or partially-sourced from the supplier.
- **Scoring Logic:**
  - A critical item is considered **Single-Sourced** if the supplier accounts for ≥ 90% of the annual spend for that specific item (SKU) across all suppliers in the last 12 months.
  - A critical item is considered **Partially-Sourced** if the supplier accounts for 50% to 89% of the annual spend for that specific item (SKU) across all suppliers in the last 12 months.
- **Point Allocation:**
  - If there is at least one single-sourced critical item:
    - **25 points** for the first single-sourced item.
    - **15 points** for each additional single-sourced item.
    - **7.5 points** for each partially-sourced item.
  - If there are no single-sourced items, but at least one partially-sourced item:
    - **10 points** for the first partially-sourced item.
    - **7.5 points** for each additional partially-sourced item.
  - If there are no single-sourced or partially-sourced items, the score is **0 points**.

#### 3. Financial Health Risk (Weight: 25%)
- **Description:** Assesses the supplier’s financial stability reliability. This factor becomes more critical for high-spend suppliers. The financial health should be calculated based on supplier’s credit rating, liquidity ratio, debt ratio, payment history.
- **Scoring Logic:**
  - **High Risk:** Poor credit rating (CCC or below), weak liquidity
  - **Medium Risk:** Moderate financial performance
  - **Low Risk:** Strong financials
- **Point Allocation:**
  - High Risk: 25 points
  - Medium Risk: 10 points
  - Low Risk: 0 points

#### 4. Spend Concentration Risk (Weight: 20%)
- **Description:** Measures the risk of over-reliance on a single supplier across the entire organization.
- **Scoring Logic:**
  - **High Concentration:** Spend with the supplier is ≥ 20% of the total company spend in the last 12 months.
  - **Medium Concentration:** Spend with the supplier is between 10% and 20% of the total company spend in the last 12 months.
  - **Low Concentration:** Spend with the supplier is < 10% of the total company spend in the last 12 months.
- **Point Allocation:**
  - High Concentration: 20 points
  - Medium Concentration: 10 points
  - Low Concentration: 0 points

### Final Score Calculation

The final risk score is the sum of the points from each of the four risk factors.
`Final Score = Country Risk Points + Single Sourcing Risk Points + Financial Health Risk Points + Spend Concentration Risk Points`

Because of the additive nature of the Single Sourcing Risk calculation, the total risk score may increase beyond 100. However, the final risk score is capped at 100.

**Interpretation:**

- **Low Risk:** <=25 points. Yearly monitoring.
- **Medium Risk:** 26–50 points. Periodic review, diversification advised.
- **High Risk:** 51–75 points. Risk mitigation required
- **Critical Risk:** 76–100 points. Immediate management attention required.

## Baseline Risk Flag Detection Logic

This section defines the conditions for triggering specific risk flags.

### Single-Sourcing
- **Trigger:** A supplier is flagged for single-sourcing risk if they are the only supplier used for a *critical* item in the last 12 months.

### Financial Health
- **Trigger:** A supplier is flagged for financial health risk if they have a 'High Risk' financial health status and the total spend with this supplier in the last 12 months exceeds a defined threshold (e.g., > 1,000,000 EUR).

### Spend Concentration
- **Trigger:** A supplier is flagged for spend concentration risk if the total spend with them over the last 12 months is ≥ 20% of the company's total procurement spend.

### Country-Level Risks
- **Trigger:** A supplier is flagged for country-level risk if their country of operation is on the 'High Risk' list.