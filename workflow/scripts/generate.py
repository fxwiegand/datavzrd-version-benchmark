import os

import numpy as np
import pandas as pd
import yaml

rows = int(snakemake.wildcards.rows)
cols = int(snakemake.wildcards.cols)
tables = int(snakemake.wildcards.tables)
rng = np.random.default_rng(snakemake.params.seed + rows + cols + tables)

MAX_IN_MEMORY_ROWS = 1500

categories = np.array(["missense", "frameshift", "nonsense", "splice", "inframe", ""])

data_dir = snakemake.output.data
os.makedirs(data_dir, exist_ok=True)

keys = [f"id_{index:09d}" for index in range(rows)]


def write_table(name, link_keys=None):
    frame = {"id": keys}
    if link_keys is not None:
        frame["link_key"] = rng.choice(link_keys, rows)
    for column in range(cols):
        frame[f"col_{column:04d}"] = rng.choice(categories, rows)
    pd.DataFrame(frame).to_csv(os.path.join(data_dir, f"{name}.csv"), index=False)


def heatmaps():
    categorical = [f"col_{column:04d}" for column in range(cols)]
    columns = {}
    for name in categorical:
        columns[name] = {
            "plot": {
                "heatmap": {
                    "scale": "ordinal",
                    "color-scheme": "category20",
                    "aux-domain-columns": [
                        other for other in categorical if other != name
                    ],
                }
            }
        }
    return columns


write_table("target")

datasets = {"target": {"path": os.path.join(data_dir, "target.csv"), "separator": ","}}
views = {"target": {"dataset": "target", "render-table": {"columns": heatmaps()}}}

for table in range(tables):
    name = f"source_{table:04d}"
    write_table(name, link_keys=keys)
    datasets[name] = {
        "path": os.path.join(data_dir, f"{name}.csv"),
        "separator": ",",
        "links": {
            "to target": {
                "column": "link_key",
                "table-row": "target/id",
                "optional": True,
            }
        },
    }
    views[name] = {"dataset": name, "render-table": {"columns": heatmaps()}}

spec = {
    "name": "benchmark",
    "max-in-memory-rows": MAX_IN_MEMORY_ROWS,
    "default-view": "target",
    "datasets": datasets,
    "views": views,
}
with open(snakemake.output.spec, "w") as handle:
    yaml.dump(spec, handle, sort_keys=False)
