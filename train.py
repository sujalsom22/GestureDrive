import pandas as pd, joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report

df = pd.read_csv("data/samples.csv", header=None)
y, X = df[0], df.iloc[:, 2:].values
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)

models = {"RandomForest": RandomForestClassifier(n_estimators=200, random_state=0),
          "kNN": KNeighborsClassifier(n_neighbors=5)}
best, best_f1 = None, -1
for name, m in models.items():
    m.fit(Xtr, ytr)
    p = m.predict(Xte)
    f1 = f1_score(yte, p, average="macro")
    print(f"\n=== {name}: accuracy {accuracy_score(yte, p):.3f}, macro-F1 {f1:.3f}")
    print(classification_report(yte, p))
    print(confusion_matrix(yte, p, labels=sorted(y.unique())))
    if f1 > best_f1:
        best, best_f1 = (name, m), f1
joblib.dump(best[1], "gesture_model.pkl")
print("\nSaved best model:", best[0])
