import numpy as np
import pandas as pd
import yaml

size = int(snakemake.wildcards.size)
rng = np.random.default_rng(snakemake.params.seed + size)

genes = np.array([f"GENE{i}" for i in range(500)])
samples = np.array([f"S{i:03d}" for i in range(50)])
chromosomes = np.array([f"chr{c}" for c in list(range(1, 23)) + ["X", "Y"]])
conditions = np.array(["control", "treated", "mutant", "wildtype"])
tissues = np.array(["liver", "brain", "lung", "kidney", "heart", "skin", "blood", "muscle"])
notes = np.array(["ok", "recheck", "borderline", "flagged", "clean"])

table = pd.DataFrame(
    {
        "id": [f"id_{i:09d}" for i in range(size)],
        "gene": rng.choice(genes, size),
        "sample": rng.choice(samples, size),
        "chromosome": rng.choice(chromosomes, size),
        "condition": rng.choice(conditions, size),
        "tissue": rng.choice(tissues, size),
        "p_value": rng.random(size).round(6),
        "adj_p_value": rng.random(size).round(6),
        "log2_fold_change": (rng.standard_normal(size) * 2).round(4),
        "expression": (rng.random(size) * 1000).round(3),
        "score": (rng.random(size) * 100).round(2),
        "count": rng.integers(0, 100000, size),
        "depth": rng.integers(0, 5000, size),
        "significant": rng.choice(["true", "false"], size),
        "note": rng.choice(notes, size),
    }
)
table.to_csv(snakemake.output.table, index=False)

palette = {
    "p_value": "blues",
    "adj_p_value": "reds",
    "expression": "greens",
    "score": "viridis",
    "depth": "purples",
}
columns = {
    column: {"plot": {"heatmap": {"scale": "linear", "color-scheme": scheme}}}
    for column, scheme in palette.items()
}
columns["count"] = {"plot": {"bars": {"scale": "linear"}}}
columns["log2_fold_change"] = {"plot": {"ticks": {"scale": "linear"}}}

spec = {
    "name": "benchmark",
    "datasets": {"data": {"path": snakemake.output.table, "separator": ","}},
    "default-view": "data",
    "views": {"data": {"dataset": "data", "render-table": {"columns": columns}}},
}
with open(snakemake.output.spec, "w") as handle:
    yaml.dump(spec, handle, sort_keys=False)
