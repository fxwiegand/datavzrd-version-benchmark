import numpy as np
import pandas as pd
import yaml

rows = int(snakemake.wildcards.rows)
cols = int(snakemake.wildcards.cols)
rng = np.random.default_rng(snakemake.params.seed + rows + cols)

MAX_IN_MEMORY_ROWS = 1500

categories = np.array(["missense", "frameshift", "nonsense", "splice", "inframe", ""])

data = {"id": [f"id_{i:09d}" for i in range(rows)]}
for column in range(cols):
    name = f"col_{column:04d}"
    if column % 2 == 0:
        data[name] = (rng.random(rows) * 1000).round(3)
    else:
        data[name] = rng.choice(categories, rows)

pd.DataFrame(data).to_csv(snakemake.output.table, index=False)

numeric_columns = [f"col_{column:04d}" for column in range(cols) if column % 2 == 0]
categorical_columns = [f"col_{column:04d}" for column in range(cols) if column % 2 == 1]

columns = {}
if rows <= MAX_IN_MEMORY_ROWS and categorical_columns:
    for name in categorical_columns:
        columns[name] = {
            "plot": {
                "heatmap": {
                    "scale": "ordinal",
                    "color-scheme": "category20",
                    "aux-domain-columns": [
                        other for other in categorical_columns if other != name
                    ],
                }
            }
        }
else:
    for name in numeric_columns:
        columns[name] = {"plot": {"heatmap": {"scale": "linear", "color-scheme": "blues"}}}

spec = {
    "name": "benchmark",
    "max-in-memory-rows": MAX_IN_MEMORY_ROWS,
    "datasets": {"data": {"path": snakemake.output.table, "separator": ","}},
    "default-view": "data",
    "views": {"data": {"dataset": "data", "render-table": {"columns": columns}}},
}
with open(snakemake.output.spec, "w") as handle:
    yaml.dump(spec, handle, sort_keys=False)
