#!/usr/bin/env python3
import csv
import sys

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

# Map month abbreviations to integer indices 0..11
MONTHS = {
    "Jan": 0,
    "Feb": 1,
    "Mar": 2,
    "Apr": 3,
    "May": 4,
    "June": 5,   # note: some datasets use 'June' instead of 'Jun'
    "Jun": 5,
    "Jul": 6,
    "Aug": 7,
    "Sep": 8,
    "Oct": 9,
    "Nov": 10,
    "Dec": 11
}


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list
    of evidence lists and a list of labels.

    Return a tuple (evidence, labels).

    Each evidence row is a list with the following 17 values, in order:
        0 Administrative, int
        1 Administrative_Duration, float
        2 Informational, int
        3 Informational_Duration, float
        4 ProductRelated, int
        5 ProductRelated_Duration, float
        6 BounceRates, float
        7 ExitRates, float
        8 PageValues, float
        9 SpecialDay, float
       10 Month, int (0 = January, ... 11 = December)
       11 OperatingSystems, int
       12 Browser, int
       13 Region, int
       14 TrafficType, int
       15 VisitorType, int (1 if Returning_Visitor, else 0)
       16 Weekend, int (1 if TRUE, else 0)

    Labels are 1 if Revenue is True, otherwise 0.
    """
    evidence = []
    labels = []

    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Parse evidence fields in the required order and types
            # Integers
            admin = int(row["Administrative"])
            info = int(row["Informational"])
            product = int(row["ProductRelated"])
            osys = int(row["OperatingSystems"])
            browser = int(row["Browser"])
            region = int(row["Region"])
            traffic = int(row["TrafficType"])

            # Floats
            admin_dur = float(row["Administrative_Duration"])
            info_dur = float(row["Informational_Duration"])
            product_dur = float(row["ProductRelated_Duration"])
            bounce = float(row["BounceRates"])
            exitrate = float(row["ExitRates"])
            pagevalue = float(row["PageValues"])
            special = float(row["SpecialDay"])

            # Month -> map to 0..11. defensive: strip and capitalize first letter(s)
            month_str = row["Month"].strip()
            # Some CSVs might have 'June' while mapping uses 'Jun' -> handle both
            month_key = month_str[:3] if month_str else month_str
            # Try several possibilities
            month = None
            if month_str in MONTHS:
                month = MONTHS[month_str]
            elif month_key in MONTHS:
                month = MONTHS[month_key]
            else:
                # fallback: try capitalized full name
                month = MONTHS.get(month_str.capitalize(), 0)

            # VisitorType -> 1 if Returning_Visitor else 0
            visitor = 1 if row["VisitorType"].strip() == "Returning_Visitor" else 0

            # Weekend -> 'TRUE'/'FALSE' or 'True'/'False'
            weekend = 1 if row["Weekend"].strip() in ("TRUE", "True", "true") else 0

            # Build evidence in exact order required
            ev = [
                admin,
                admin_dur,
                info,
                info_dur,
                product,
                product_dur,
                bounce,
                exitrate,
                pagevalue,
                special,
                month,
                osys,
                browser,
                region,
                traffic,
                visitor,
                weekend
            ]
            evidence.append(ev)

            # Label: Revenue -> TRUE/False strings
            label = 1 if row["Revenue"].strip() in ("TRUE", "True", "true") else 0
            labels.append(label)

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Train a k-nearest neighbor classifier (k = 1) on the provided evidence and labels.

    Return the fitted KNeighborsClassifier.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and predicted labels (0 or 1),
    return a tuple (sensitivity, specificity).

    sensitivity = true positive rate = TP / P
    specificity = true negative rate = TN / N
    """
    # Count positives and negatives in actual labels
    positives = sum(1 for lab in labels if lab == 1)
    negatives = sum(1 for lab in labels if lab == 0)

    # True positives: actual 1 and predicted 1
    tp = sum(1 for actual, pred in zip(labels, predictions) if actual == 1 and pred == 1)
    # True negatives: actual 0 and predicted 0
    tn = sum(1 for actual, pred in zip(labels, predictions) if actual == 0 and pred == 0)

    sensitivity = tp / positives if positives else 0
    specificity = tn / negatives if negatives else 0

    return (sensitivity, specificity)


def main():
    # Check command-line usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data.csv")

    # Load data from spreadsheet
    evidence, labels = load_data(sys.argv[1])

    # Split into train and test sets (40% test)
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=0.4
    )

    # Train model
    model = train_model(X_train, y_train)

    # Make predictions on the test set
    predictions = model.predict(X_test)

    # Evaluate model
    sensitivity, specificity = evaluate(y_test, predictions)

    # Report results
    correct = sum(1 for actual, pred in zip(y_test, predictions) if actual == pred)
    incorrect = len(y_test) - correct

    print(f"Correct: {correct}")
    print(f"Incorrect: {incorrect}")
    print(f"True Positive Rate: {sensitivity:.2f}")
    print(f"True Negative Rate: {specificity:.2f}")


if __name__ == "__main__":
    main()
