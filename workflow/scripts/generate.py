import numpy as np
import pandas as pd
import yaml

rows = int(snakemake.wildcards.rows)
cols = int(snakemake.wildcards.cols)
rng = np.random.default_rng(snakemake.params.seed + rows + cols)

categories = np.array(["missense", "frameshift", "nonsense", "splice", "inframe", ""])

data = {"id": [f"id_{i:09d}" for i in range(rows)]}
for column in range(cols):
    name = f"col_{column:04d}"
    if column % 2 == 0:
        data[name] = (rng.random(rows) * 1000).round(3)
    else:
        data[name] = rng.choice(categories, rows)

pd.DataFrame(data).to_csv(snakemake.output.table, index=False)

columns = {
    f"col_{column:04d}": {"plot": {"heatmap": {"scale": "linear", "color-scheme": "blues"}}}
    for column in range(cols)
    if column % 2 == 0
}

spec = {
    "name": "benchmark",
    "datasets": {"data": {"path": snakemake.output.table, "separator": ","}},
    "default-view": "data",
    "views": {"data": {"dataset": "data", "render-table": {"columns": columns}}},
}
with open(snakemake.output.spec, "w") as handle:
    yaml.dump(spec, handle, sort_keys=False)
