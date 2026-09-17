"""
Precision/recall/F1 hesaplama - consensus sonucu ile gercek etiketi
(is_violation) karsilastirmak icin kullanilir.
"""
from dataclasses import dataclass


@dataclass
class ClassificationMetrics:
    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int

    @property
    def precision(self) -> float:
        denom = self.true_positive + self.false_positive
        return self.true_positive / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.true_positive + self.false_negative
        return self.true_positive / denom if denom else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if (p + r) else 0.0

    @property
    def accuracy(self) -> float:
        total = self.true_positive + self.false_positive + self.false_negative + self.true_negative
        correct = self.true_positive + self.true_negative
        return correct / total if total else 0.0

    def as_dict(self) -> dict:
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "accuracy": round(self.accuracy, 4),
            "tp": self.true_positive,
            "fp": self.false_positive,
            "fn": self.false_negative,
            "tn": self.true_negative,
        }


def compute_metrics(y_true: list[bool], y_pred: list[bool]) -> ClassificationMetrics:
    """y_true/y_pred: True = 'ihlal var', False = 'gecerli'."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true ve y_pred ayni uzunlukta olmali")

    tp = fp = fn = tn = 0
    for actual, predicted in zip(y_true, y_pred):
        if actual and predicted:
            tp += 1
        elif not actual and predicted:
            fp += 1
        elif actual and not predicted:
            fn += 1
        else:
            tn += 1

    return ClassificationMetrics(tp, fp, fn, tn)
