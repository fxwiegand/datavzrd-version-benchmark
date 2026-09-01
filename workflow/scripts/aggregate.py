import statistics

import pandas as pd
import yaml


def summarise(path):
    frame = pd.read_csv(path, sep="\t")
    return statistics.median(frame["seconds"]), statistics.median(frame["peak_mb"])


rows = []
for (shape_rows, shape_cols), old_path, new_path in zip(
    snakemake.params.shapes, snakemake.input.old, snakemake.input.new
):
    old_seconds, old_mb = summarise(old_path)
    new_seconds, new_mb = summarise(new_path)
    rows.append(
        {
            "rows": shape_rows,
            "columns": shape_cols,
            "runtime_old_s": round(old_seconds, 1),
            "runtime_new_s": round(new_seconds, 1),
            "runtime_saved_s": round(old_seconds - new_seconds, 1),
            "runtime_saved_percent": round((old_seconds - new_seconds) / old_seconds * 100, 1),
            "memory_old_mb": round(old_mb),
            "memory_new_mb": round(new_mb),
            "memory_saved_mb": round(old_mb - new_mb),
            "memory_saved_percent": round((old_mb - new_mb) / old_mb * 100, 1),
        }
    )

comparison = pd.DataFrame(rows).sort_values(["rows", "columns"]).reset_index(drop=True)
comparison.to_csv(snakemake.output.table, index=False)

columns = {
    "runtime_saved_s": {"plot": {"bars": {"scale": "linear"}}},
    "runtime_saved_percent": {
        "plot": {"heatmap": {"scale": "linear", "color-scheme": "greens", "domain": [0, 100]}}
    },
    "memory_saved_mb": {"plot": {"bars": {"scale": "linear"}}},
    "memory_saved_percent": {
        "plot": {"heatmap": {"scale": "linear", "color-scheme": "greens", "domain": [0, 100]}}
    },
}

spec = {
    "name": f"datavzrd {snakemake.params.old_version} vs {snakemake.params.new_version}",
    "datasets": {"comparison": {"path": snakemake.output.table, "separator": ","}},
    "default-view": "comparison",
    "views": {
        "comparison": {"dataset": "comparison", "render-table": {"columns": columns}}
    },
}
with open(snakemake.output.spec, "w") as handle:
    yaml.dump(spec, handle, sort_keys=False)
