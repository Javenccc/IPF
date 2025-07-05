# **Iterative Proportional Fitting (IPF) for Top-Down Forecast Reconciliation**

## 🔍 Use Case
This project solves a common forecasting challenge: translating high-level strategic targets (e.g., total sales by channel, segment, or region) into consistent, 
actionable forecasts at a lower level of granularity (e.g., product lines, store-level sales, or customer segments).

## 📌 Problem Context
- Top-level targets are defined by leadership or strategic planning.
- These targets need to be allocated down the hierarchy so execution teams can take action.
- Forecasting each leaf node independently is noisy, redundant, and may lead to inconsistencies.
- Hierarchy reconciliation ensures forecasts remain aligned from top to bottom.

## 🧠 Solution: A Two-Step Workflow
1. Top-Down Projection
    Start from strategic inputs and define targets at higher levels (e.g., Channel or Segment level).
2. Reconciliation via IPF
    Use Iterative Proportional Fitting to allocate targets down the hierarchy using historical distribution patterns, ensuring:
    * Leaf-level forecasts add up to top-level targets.
    * Growth assumptions are distributed realistically across dimensions.

## ✅ Why IPF?
We use IPF as the reconciliation method because:
1. The business is stable with no major structural changes expected.
2. Historical data provides strong, reliable distribution patterns.
3. We have a two-dimensional constraint (e.g., Channel × Segment) to satisfy, which IPF handles well.
