import csv
import os
import re


# ============================================================
# CSV DATABASE
# ============================================================

CSV_PATH = os.path.join(
    os.path.dirname(__file__),
    "cropiq_pestcides.csv"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(value):
    """
    Makes crop/disease matching tolerant of:
    - uppercase/lowercase differences
    - spaces
    - hyphens
    """

    return (
        str(value)
        .strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


# ============================================================
# SEVERITY CALCULATION
# ============================================================

def calculate_severity(fruit_area, diseased_area):
    """
    Severity (%) =
        Diseased Area / Fruit Area × 100
    """

    fruit_area = float(fruit_area)
    diseased_area = float(diseased_area)

    if fruit_area <= 0:
        raise ValueError(
            "Fruit area must be greater than 0."
        )

    if diseased_area < 0:
        raise ValueError(
            "Diseased area cannot be negative."
        )

    if diseased_area > fruit_area:
        raise ValueError(
            "Diseased area cannot be greater than fruit area."
        )

    severity = (
        diseased_area
        / fruit_area
        * 100.0
    )

    return round(severity, 2)


# ============================================================
# BASE DOSAGE PARSER
# ============================================================

def parse_base_dosage(value):
    """
    Converts CSV dosage values into millilitres.

    Examples:

        650 ml  -> 650 ml
        0.65 L  -> 650 ml
        2.8 L   -> 2800 ml
        0.09 L  -> 90 ml
    """

    text = str(value).strip().lower()

    if text in {
        "",
        "none",
        "nan",
        "no treatment"
    }:
        return 0.0

    match = re.search(
        r"([0-9]+(?:\.[0-9]+)?)",
        text
    )

    if not match:
        raise ValueError(
            f"Invalid base dosage value: {value}"
        )

    amount = float(match.group(1))

    if "ml" in text:
        return amount

    if "l" in text:
        return amount * 1000.0

    raise ValueError(
        f"Unsupported dosage unit: {value}"
    )


# ============================================================
# CSV RULE LOOKUP
# ============================================================

def get_rule(crop, disease):
    """
    Finds the matching Crop + Disease rule
    from cropiq_pestcides.csv.
    """

    crop_key = normalize_text(crop)
    disease_key = normalize_text(disease)

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"Dosage CSV not found: {CSV_PATH}"
        )

    with open(
        CSV_PATH,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as csv_file:

        reader = csv.DictReader(csv_file)

        required_columns = {
            "Crop",
            "disease",
            "product",
            "Base dosage/spray volume"
        }

        if not required_columns.issubset(
            reader.fieldnames or []
        ):
            raise ValueError(
                "Pesticide CSV is missing required columns."
            )

        for row in reader:

            row_crop = normalize_text(
                row["Crop"]
            )

            row_disease = normalize_text(
                row["disease"]
            )

            if (
                row_crop == crop_key
                and
                row_disease == disease_key
            ):

                return {
                    "crop": row["Crop"].strip(),
                    "disease": row["disease"].strip(),
                    "pesticide": row["product"].strip(),
                    "base_dosage": row[
                        "Base dosage/spray volume"
                    ].strip(),
                }

    raise ValueError(
        f"No dosage rule found for "
        f"{crop} / {disease}."
    )


# ============================================================
# FINAL DOSAGE CALCULATION
# ============================================================

def calculate_dosage(
    crop,
    disease,
    fruit_area,
    diseased_area
):
    """
    Complete CropIQ dosage rule engine.

    Pipeline:

        Segmentation
             ↓
        Fruit area
             +
        Disease area
             ↓
        Severity %
             ↓
        CSV rule lookup
             ↓
        Base dosage
             ↓
        Final dosage
    """

    # --------------------------------------------------------
    # 1. Calculate severity
    # --------------------------------------------------------

    severity = calculate_severity(
        fruit_area,
        diseased_area
    )

    # --------------------------------------------------------
    # 2. Find CSV rule
    # --------------------------------------------------------

    rule = get_rule(
        crop,
        disease
    )

    # --------------------------------------------------------
    # 3. Convert base dosage to ml
    # --------------------------------------------------------

    base_dosage_ml = parse_base_dosage(
        rule["base_dosage"]
    )

    # --------------------------------------------------------
    # 4. Check for no-treatment rule
    # --------------------------------------------------------

    no_treatment = (
        rule["pesticide"]
        .strip()
        .lower()
        == "no treatment"
    )

    if no_treatment:

        final_dosage_ml = 0.0

    else:

        # ----------------------------------------------------
        # Final Dose =
        # Base Dose × Severity / 100
        # ----------------------------------------------------

        final_dosage_ml = (
            base_dosage_ml
            * severity
            / 100.0
        )

    # --------------------------------------------------------
    # 5. Return complete result
    # --------------------------------------------------------

    return {
        "crop": rule["crop"],
        "disease": rule["disease"],
        "severity_percentage": severity,
        "pesticide": rule["pesticide"],
        "base_dosage": rule["base_dosage"],
        "base_dosage_ml": round(
            base_dosage_ml,
            2
        ),
        "final_dosage_ml": round(
            final_dosage_ml,
            2
        ),
        "treatment_required": not no_treatment,
    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    result = calculate_dosage(
        crop="Guava",
        disease="Anthracnose",
        fruit_area=100000,
        diseased_area=12000,
    )

    print("\nCropIQ Dosage Engine Test")
    print("=" * 50)

    for key, value in result.items():
        print(f"{key}: {value}")
