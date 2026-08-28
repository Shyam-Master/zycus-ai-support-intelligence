# Reporting and Analytics Exports

## Overview
This document covers the report generation and export functionalities across the platform.

## Common Issues

### Report generation failure
If reports fail to generate, it may be due to complex queries timing out. 
- Reduce the date range.
- Try running the report during off-peak hours.

### CSV / PDF export failure
Users may encounter failures when exporting large datasets to CSV or PDF.
- The maximum export limit is 100,000 rows for CSV and 50 pages for PDF.
- If the export button is greyed out, verify permissions.

### Dashboard/report loading issues
If dashboards are slow to load, it is usually a performance issue related to the underlying data source (e.g., Snowflake warehouse size).
