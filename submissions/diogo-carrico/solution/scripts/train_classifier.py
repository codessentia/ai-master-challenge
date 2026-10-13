"""Train, choose, calibrate and evaluate the ticket classifier; measure domain shift on Dataset 1.

Writes outputs/classifier/metrics.json and confusion_matrix.csv, and the model to outputs/model/ (not committed).
Run from the solution folder:  uv run python scripts/train_classifier.py
"""

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, f1_score

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from support_triage.classifier import (
    calibrate,
    candidate_models,
    classification_report,
    cost_threshold,
    coverage_at_threshold,
    expected_calibration_error,
    near_duplicate_groups,
    normalize_text,
    per_class_thresholds,
    route,
    routed_quality,
    split_indices,
    threshold_for_precision,
)
from support_triage.paths import IT_TICKETS_DIR, OUTPUTS_DIR, TICKETS_DIR

OUT = OUTPUTS_DIR / "classifier"
MODEL_DIR = OUTPUTS_DIR / "model"
CACHE = OUTPUTS_DIR / "cache"
TARGET_PRECISION = 0.95  # hypothesis 3.2: at least 95% precision on auto-routed tickets
TRIAGE_MINUTES, REWORK_MINUTES = 4, 10  # base values of the waste model


def vocabulary_coverage(texts: pd.Series, vocab: set[str]) -> np.ndarray:
    """Share of each text's tokens that the model saw in training."""
    return np.array(
        [np.mean([t in vocab for t in s.split()]) if s else 0.0 for s in texts]
    )


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(IT_TICKETS_DIR / "all_tickets_processed_improved_v3.csv")
    x = df["Document"].fillna("").map(normalize_text)
    y = df["Topic_group"].to_numpy()
    classes = sorted(df["Topic_group"].unique())

    # 1. near duplicates: kept in one partition, and a first look at label conflicts
    groups = near_duplicate_groups(x)
    sizes = pd.Series(groups).value_counts()
    multi = sizes[sizes > 1].index
    conflicting = [g for g in multi if len(set(y[groups == g])) > 1]
    near_dups = {
        "similarity_threshold": 0.9,
        "groups_with_more_than_one_ticket": len(multi),
        "tickets_in_those_groups": int(sizes[multi].sum()),
        "groups_with_conflicting_labels": len(conflicting),
        "tickets_in_conflicting_groups": int(np.isin(groups, conflicting).sum()),
    }
    pd.DataFrame({"group": groups, "label": y, "text": x}).loc[
        np.isin(groups, conflicting)
    ].sort_values("group").to_csv(OUT / "near_duplicate_conflicts.csv", index=False)

    # 2. split
    idx = split_indices(df["Topic_group"], groups)
    xs = {k: x.iloc[v] for k, v in idx.items()}
    ys = {k: y[v] for k, v in idx.items()}

    # 3. choose a model on validation macro-F1
    scores = {}
    fitted = {}
    for name, model in candidate_models().items():
        model.fit(xs["train"], ys["train"])
        scores[name] = float(
            f1_score(ys["validation"], model.predict(xs["validation"]), average="macro")
        )
        fitted[name] = model
    best = max(scores, key=scores.get)
    model = fitted[best]

    # 4. calibrate on the calibration split
    calibrated = calibrate(model, xs["calibration"], ys["calibration"])

    # 5. thresholds chosen on validation
    pv = calibrated.predict_proba(xs["validation"])
    conf_v = pv.max(axis=1)
    correct_v = calibrated.classes_[pv.argmax(axis=1)] == ys["validation"]
    pred_v = calibrated.classes_[pv.argmax(axis=1)]
    t_precision = threshold_for_precision(conf_v, correct_v, TARGET_PRECISION)
    t_class = per_class_thresholds(conf_v, pred_v, correct_v, classes, TARGET_PRECISION)
    t_cost = cost_threshold(TRIAGE_MINUTES, REWORK_MINUTES)

    # 6. test: touched once, here
    pt = calibrated.predict_proba(xs["test"])
    pred_t = calibrated.classes_[pt.argmax(axis=1)]
    conf_t = pt.max(axis=1)
    correct_t = pred_t == ys["test"]
    report = classification_report(ys["test"], pred_t, classes)

    def per_class(routed: np.ndarray) -> dict:
        out = {}
        for c in classes:
            mask = routed & (pred_t == c)
            out[c] = {
                "predicted": int((pred_t == c).sum()),
                "routed": int(mask.sum()),
                **{
                    k: v
                    for k, v in routed_quality(
                        mask[pred_t == c], correct_t[pred_t == c]
                    ).items()
                    if k != "coverage"
                },
            }
        return out

    routed_global = conf_t >= t_precision
    routed_class = route(conf_t, pred_t, t_class)

    # Cache the split and the test predictions so later steps (label review, model comparison) use the same tickets.
    CACHE.mkdir(parents=True, exist_ok=True)
    np.savez(CACHE / "split.npz", **idx)
    pd.DataFrame(
        {
            "row": idx["test"],
            "text": xs["test"].to_numpy(),
            "label": ys["test"],
            "predicted": pred_t,
            "confidence": conf_t,
            "routed": routed_class,
        }
    ).to_csv(CACHE / "test_predictions.csv", index=False)
    # The words that weigh most for each class: a reading guide for the human label review.
    clf, terms = model.named_steps["clf"], model.named_steps["tfidf"].get_feature_names_out()
    if hasattr(clf, "coef_"):
        class_terms = {c: [str(t) for t in terms[np.argsort(clf.coef_[i])[::-1][:15]]] for i, c in enumerate(clf.classes_)}
        (OUT / "class_terms.json").write_text(json.dumps(class_terms, indent=2, ensure_ascii=False), encoding="utf-8")
    uncal_conf = None
    if hasattr(model, "predict_proba"):
        pu = model.predict_proba(xs["test"])
        uncal_conf = expected_calibration_error(
            pu.max(axis=1), model.classes_[pu.argmax(axis=1)] == ys["test"]
        )

    # 7. domain shift: the Dataset 2 model on Dataset 1 descriptions
    d1 = pd.read_csv(TICKETS_DIR / "customer_support_tickets.csv")
    x1 = (
        d1["Ticket Description"]
        .fillna("")
        .str.replace(r"\{[a-z_]+\}", " ", regex=True)
        .map(normalize_text)
    )
    p1 = calibrated.predict_proba(x1)
    vocab = set(model.named_steps["tfidf"].vocabulary_)
    cov_val = vocabulary_coverage(xs["validation"], vocab)
    cov_d1 = vocabulary_coverage(x1, vocab)
    guard = float(np.quantile(cov_val, 0.01))
    d1_pred = pd.Series(calibrated.classes_[p1.argmax(axis=1)]).value_counts(
        normalize=True
    )

    result = {
        "data": {
            "rows": len(df),
            "classes": classes,
            "near_duplicates": near_dups,
            "split_sizes": {k: len(v) for k, v in idx.items()},
        },
        "model_selection": {"validation_macro_f1": scores, "chosen": best},
        "test": report,
        "calibration": {
            "method": "sigmoid, fitted on the calibration split",
            "ece_test_before": uncal_conf,
            "ece_test_after": expected_calibration_error(conf_t, correct_t),
        },
        "thresholds": {
            "target_precision": TARGET_PRECISION,
            "precision_threshold": t_precision,
            "cost_threshold": t_cost,
            "cost_threshold_inputs": {
                "triage_minutes": TRIAGE_MINUTES,
                "rework_minutes": REWORK_MINUTES,
            },
            "validation_at_precision_threshold": coverage_at_threshold(
                conf_v, correct_v, t_precision
            ),
            "test_at_precision_threshold": coverage_at_threshold(
                conf_t, correct_t, t_precision
            ),
            "test_at_cost_threshold": coverage_at_threshold(conf_t, correct_t, t_cost),
            "test_per_class_at_precision_threshold": per_class(routed_global),
            "per_class_thresholds": t_class,
            "validation_at_per_class_thresholds": routed_quality(
                route(conf_v, pred_v, t_class), correct_v
            ),
            "test_at_per_class_thresholds": routed_quality(routed_class, correct_t),
            "test_per_class_at_per_class_thresholds": per_class(routed_class),
        },
        "domain_shift_dataset1": {
            "tickets": len(d1),
            "predicted_class_shares": {k: float(v) for k, v in d1_pred.items()},
            "median_confidence": float(np.median(p1.max(axis=1))),
            "share_above_precision_threshold": float(
                (p1.max(axis=1) >= t_precision).mean()
            ),
            "share_above_per_class_thresholds": float(
                route(
                    p1.max(axis=1), calibrated.classes_[p1.argmax(axis=1)], t_class
                ).mean()
            ),
            "vocabulary_coverage_median_dataset2_validation": float(np.median(cov_val)),
            "vocabulary_coverage_median_dataset1": float(np.median(cov_d1)),
            "guard_threshold_vocabulary_coverage": guard,
            "share_of_dataset1_stopped_by_guard": float((cov_d1 < guard).mean()),
            "share_of_dataset2_test_stopped_by_guard": float(
                (vocabulary_coverage(xs["test"], vocab) < guard).mean()
            ),
        },
    }
    (OUT / "metrics.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    pd.DataFrame(
        confusion_matrix(ys["test"], pred_t, labels=classes),
        index=classes,
        columns=classes,
    ).to_csv(OUT / "confusion_matrix.csv")
    joblib.dump(
        {
            "model": calibrated,
            "thresholds": t_class,
            "guard": guard,
            "vocabulary": vocab,
        },
        MODEL_DIR / "triage.joblib",
    )
    print(
        f"chosen {best}; test accuracy {report['accuracy']:.4f}, macro-F1 {report['macro_f1']:.4f}"
    )
    print(f"wrote {OUT / 'metrics.json'}")


if __name__ == "__main__":
    main()
