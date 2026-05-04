"""
=============================================================
ML MODEL TRAINING SCRIPT
=============================================================
File: backend/ml_models/train_models.py

HOW TO RUN:
  cd backend
  pip install -r requirements.txt
  python ml_models/train_models.py

This script:
1. Downloads/uses crop recommendation dataset
2. Trains a Random Forest classifier for crops
3. Trains a Gradient Boosting regressor for land prices
4. Saves both models as .pkl files
5. Prints accuracy reports

DATASETS USED:
- Crop: https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
- Land: Custom dataset (generate synthetic or use state agriculture data)
=============================================================
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
import pickle
import os

print("=" * 60)
print("SMART AGRI — Model Training Script")
print("=" * 60)

# ============================================================
# SECTION 1: CROP RECOMMENDATION MODEL
# ============================================================
print("\n📊 Training Crop Recommendation Model...")

# Load dataset — download from Kaggle link above
# Expected columns: N, P, K, temperature, humidity, ph, rainfall, label
CROP_CSV = os.path.join(os.path.dirname(__file__), "data/crop_data.csv")

try:
    df = pd.read_csv(CROP_CSV)
    print(f"   Dataset loaded: {df.shape[0]} rows, {df['label'].nunique()} crop types")
except FileNotFoundError:
    print("   ⚠️  Dataset not found. Generating synthetic data for demo...")
    # Generate synthetic data that follows realistic agricultural patterns
    np.random.seed(42)
    n_samples = 2200
    data = {
        "N":           np.random.randint(0,   200, n_samples),
        "P":           np.random.randint(5,   145, n_samples),
        "K":           np.random.randint(5,   205, n_samples),
        "temperature": np.random.uniform(8,   44,  n_samples),
        "humidity":    np.random.uniform(14,  100, n_samples),
        "ph":          np.random.uniform(3.5, 9.9, n_samples),
        "rainfall":    np.random.uniform(20,  300, n_samples),
    }
    # Assign crops using rule-based logic (mirrors real dataset distribution)
    crops = []
    for i in range(n_samples):
        h, r, t, ph = data["humidity"][i], data["rainfall"][i], data["temperature"][i], data["ph"][i]
        if h > 80 and r > 200 and t > 22:  crops.append("rice")
        elif t < 20 and 100 < r < 200:     crops.append("wheat")
        elif h < 70 and r < 150 and t > 18: crops.append("maize")
        elif ph > 5.5 and t > 25 and r < 150: crops.append("groundnut")
        elif t > 24 and r > 150 and h > 65: crops.append("sugarcane")
        elif h > 70 and t > 20 and r > 200: crops.append("coffee")
        elif t > 25 and r < 200:           crops.append("mango")
        elif ph > 6 and t > 20 and t < 30: crops.append("tomato")
        else:                              crops.append("rice")
    data["label"] = crops
    df = pd.DataFrame(data)
    print(f"   Synthetic data created: {df.shape[0]} rows")

# Prepare features and target
X = df[["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]].values
y = df["label"].values

# Encode string labels to integers (for model training)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Split 80% train, 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Train Random Forest
# n_estimators=100 → 100 decision trees (higher = more accurate but slower)
# max_depth=None → trees grow until pure (good for this problem)
crop_clf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1      # Use all CPU cores
)
crop_clf.fit(X_train, y_train)

# Evaluate
y_pred = crop_clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"   ✅ Crop Model Accuracy: {accuracy*100:.2f}%")

# Important: save the label encoder WITH the model so we can decode predictions
crop_model_data = {
    "model":   crop_clf,
    "encoder": le,
    "classes": le.classes_  # ["coffee", "groundnut", "maize", ...]
}

# Save model
os.makedirs(os.path.dirname(__file__), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "crop_model.pkl"), "wb") as f:
    pickle.dump(crop_model_data, f)
print("   💾 Saved: ml_models/crop_model.pkl")


# ============================================================
# SECTION 2: LAND PRICE PREDICTION MODEL
# ============================================================
print("\n🏡 Training Land Price Model...")

# Generate synthetic land price dataset
# In production: collect real transaction data from state registration offices
np.random.seed(123)
n = 3000
STATE_CODES = ["AP", "TS", "KA", "TN", "MH", "UP"]
BASE = {"AP": 800000, "TS": 750000, "KA": 950000, "TN": 1100000, "MH": 1200000, "UP": 450000}
SOIL  = {1: 1.2, 2: 0.9, 3: 1.1, 4: 0.8, 5: 1.3}
IRR   = {1: 1.3, 2: 1.1, 3: 0.8, 4: 1.2}

rows = []
for _ in range(n):
    state    = np.random.choice(STATE_CODES)
    area     = np.random.uniform(0.5, 20)
    soil_t   = np.random.randint(1, 6)
    irr_t    = np.random.randint(1, 5)
    road_km  = np.random.uniform(0, 15)
    noise    = np.random.normal(1.0, 0.08)  # ±8% market variability
    road_f   = max(0.65, 1 - road_km * 0.04)
    price    = BASE[state] * area * SOIL[soil_t] * IRR[irr_t] * road_f * noise

    rows.append({
        "state_code": hash(state) % 20,
        "area":       area,
        "soil_type":  soil_t,
        "irrigation": irr_t,
        "road_km":    road_km,
        "price":      price
    })

land_df = pd.DataFrame(rows)
X_land = land_df[["state_code", "area", "soil_type", "irrigation", "road_km"]].values
y_land = land_df["price"].values

X_tr, X_te, y_tr, y_te = train_test_split(X_land, y_land, test_size=0.2, random_state=42)

# Gradient Boosting Regressor — excellent for tabular regression
land_reg = GradientBoostingRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=5,
    random_state=42
)
land_reg.fit(X_tr, y_tr)

y_pred_land = land_reg.predict(X_te)
mae = mean_absolute_error(y_te, y_pred_land)
r2  = r2_score(y_te, y_pred_land)
print(f"   ✅ Land Model R²: {r2:.4f}, MAE: ₹{mae:,.0f}")

with open(os.path.join(os.path.dirname(__file__), "land_model.pkl"), "wb") as f:
    pickle.dump(land_reg, f)
print("   💾 Saved: ml_models/land_model.pkl")


# ============================================================
# SECTION 3: CNN DISEASE DETECTION — TRAINING GUIDE
# ============================================================
print("""
📷 Disease Detection CNN Training Guide:
   (Run separately — requires GPU/Colab recommended)

   1. Download PlantVillage dataset from Kaggle:
      https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset

   2. Run this code in Google Colab (free GPU):

   from tensorflow.keras.applications import MobileNetV2
   from tensorflow.keras import layers, models
   from tensorflow.keras.preprocessing.image import ImageDataGenerator

   # Load pre-trained MobileNetV2 (transfer learning)
   base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
   base.trainable = False  # Freeze base layers

   # Add custom classification head
   model = models.Sequential([
       base,
       layers.GlobalAveragePooling2D(),
       layers.Dense(256, activation='relu'),
       layers.Dropout(0.4),
       layers.Dense(38, activation='softmax')  # 38 disease classes
   ])
   model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

   # Data augmentation to prevent overfitting
   datagen = ImageDataGenerator(
       rescale=1./255,
       rotation_range=30,
       horizontal_flip=True,
       zoom_range=0.2,
       validation_split=0.2
   )
   train_gen = datagen.flow_from_directory('PlantVillage', target_size=(224,224),
                                            batch_size=32, subset='training')
   val_gen   = datagen.flow_from_directory('PlantVillage', target_size=(224,224),
                                            batch_size=32, subset='validation')

   model.fit(train_gen, validation_data=val_gen, epochs=20)
   model.save('disease_model.h5')
   # Copy disease_model.h5 to backend/ml_models/
""")

print("\n✅ Training complete! Models saved in ml_models/")
print("   Next: Run 'uvicorn main:app --reload' to start the API server")
