# Regression and Baselines

## Baseline philosophy

A baseline records observed behavior; it does not sanctify it.

Each metric has:
- direction (`higher` or `lower` is better);
- minimum/maximum acceptance threshold;
- regression tolerance relative to baseline;
- criticality.

A new version fails the gate if it crosses a critical threshold even when it improves another metric.

## Frozen corpora

Dataset files are versioned and hashed. Changes to the dataset require a new corpus version or explicit changelog entry; otherwise scores are not comparable.
