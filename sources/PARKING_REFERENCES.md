# Outdoor parking references

Every model-scope grouped surface parking area was checked against public Esri World Imagery. `parking_satellite_review.json` retains stable export URLs, exact returned image extents, original lot IDs and individual observations. Imagery is reference-only and is not redistributed.

`parking_rows.json` records explicit visible row paths, with approximate bay spacing/depth. The model preserves aisles and current building clearance, uses asphalt, and leaves faded, obscured or unmarked areas without an invented stripe grid. `output/parking_validation.json` records the rendered rows.
