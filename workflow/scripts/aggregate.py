import statistics

import pandas as pd
import yaml


def summarise(path):
    frame = pd.read_csv(path, sep="\t")
    return statistics.median(frame["seconds"]), statistics.median(frame["peak_mb"])


def label(version):
    return version.replace(".", "_")


versions = snakemake.params.versions
baseline = versions[0]
latest = versions[-1]
shapes = [tuple(shape) for shape in snakemake.params.shapes]

metrics = list(snakemake.input.metrics)
paths = {}
index = 0
for version in versions:
    for shape in shapes:
        paths[(version, shape)] = metrics[index]
        index += 1

rows = []
for shape in shapes:
    shape_rows, shape_cols, shape_tables = shape
    record = {"rows": shape_rows, "columns": shape_cols, "tables": shape_tables}
    seconds = {}
    memory = {}
    for version in versions:
        s, m = summarise(paths[(version, shape)])
        seconds[version] = s
        memory[version] = m
        record[f"runtime_{label(version)}_s"] = round(s, 1)
        record[f"memory_{label(version)}_mb"] = round(m)
    record["runtime_saved_percent"] = round(
        (seconds[baseline] - seconds[latest]) / seconds[baseline] * 100, 1
    )
    record["memory_saved_percent"] = round(
        (memory[baseline] - memory[latest]) / memory[baseline] * 100, 1
    )
    rows.append(record)

comparison = (
    pd.DataFrame(rows).sort_values(["rows", "columns", "tables"]).reset_index(drop=True)
)
comparison.to_csv(snakemake.output.table, index=False)

columns = {}
for version in versions:
    columns[f"runtime_{label(version)}_s"] = {"plot": {"bars": {"scale": "linear"}}}
for version in versions:
    columns[f"memory_{label(version)}_mb"] = {"plot": {"bars": {"scale": "linear"}}}
for column in ("runtime_saved_percent", "memory_saved_percent"):
    columns[column] = {
        "plot": {"heatmap": {"scale": "linear", "color-scheme": "greens", "domain": [0, 100]}}
    }

spec = {
    "name": f"datavzrd {baseline} → {latest}",
    "datasets": {"comparison": {"path": snakemake.output.table, "separator": ","}},
    "default-view": "comparison",
    "views": {
        "comparison": {"dataset": "comparison", "render-table": {"columns": columns}}
    },
}
with open(snakemake.output.spec, "w") as handle:
    yaml.dump(spec, handle, sort_keys=False)
