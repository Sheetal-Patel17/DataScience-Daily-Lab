python -m dslab.provenance create `
  --input data/day-08/orders_snapshot.csv `
  --config configs/day-08-provenance.json `
  --output reports/day-08/provenance-manifest.json

python -m dslab.provenance verify `
  --manifest reports/day-08/provenance-manifest.json `
  --output reports/day-08/verification.json