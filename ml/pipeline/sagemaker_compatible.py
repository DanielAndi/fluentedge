"""SageMaker-compatible entry point mapping (FR-INF-005, design §7.1).

Local scripts map to managed SageMaker steps without requiring the SageMaker SDK
for the minimum demo.
"""

from __future__ import annotations

SAGEMAKER_MAPPING = {
    "processing_validate": {
        "local_entry": "python -m ml.pipeline.local_pipeline --stage validate",
        "sagemaker_step": "Processing",
        "notes": "Validate manifest schema and audio integrity.",
    },
    "processing_preprocess": {
        "local_entry": "python -m ml.pipeline.local_pipeline --stage preprocess",
        "sagemaker_step": "Processing",
        "notes": "Normalize audio/text and derive labels without source_status leakage.",
    },
    "processing_features": {
        "local_entry": "python -m ml.pipeline.local_pipeline --stage features",
        "sagemaker_step": "Processing",
        "notes": "Build feature matrix and schema hash.",
    },
    "training": {
        "local_entry": "python -m ml.pipeline.local_pipeline --stage train",
        "sagemaker_step": "Training",
        "notes": "Train logistic regression and random forest candidates.",
    },
    "evaluation": {
        "local_entry": "python -m ml.pipeline.local_pipeline --stage evaluate",
        "sagemaker_step": "Processing",
        "notes": "Evaluate metrics and quality gates.",
    },
    "register": {
        "local_entry": "python -m ml.pipeline.local_pipeline --stage register",
        "sagemaker_step": "Model Registry",
        "notes": "Register pending model in MLflow; approval remains manual.",
    },
}


def print_mapping() -> None:
    for name, info in SAGEMAKER_MAPPING.items():
        print(f"{name}: {info['sagemaker_step']} <- {info['local_entry']}")


if __name__ == "__main__":
    print_mapping()
