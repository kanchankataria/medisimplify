## The Problem

When patients receive medical reports they see:
HbA1c: 9.1%

eGFR: 38 mL/min

LDL: 158 mg/dL

Creatinine: 2.1 mg/dL

They have no idea what this means. They google it, find scary
information, misinterpret results, or simply ignore them.

### Why This Problem Got Worse

In 2021 the US government passed the **21st Century Cures Act**
requiring hospitals to release ALL test results to patients
**immediately** with no delay allowed.

This means:

- Patients receive lab results at 10 PM via patient portals
- Doctor offices are closed until next morning
- Patient is anxious all night with no explanation
- Results arrive before the doctor has even reviewed them

---

## The Gap

MyChart — the most widely used patient portal — provides access
to test results, a general health library, and a basic symptom
checker. However it does not provide:

- Plain English explanation of YOUR specific lab values
- Color coded risk classification (High / Medium / Low)
- ML based risk prediction from your actual results
- X-ray image analysis and simplification
- Personalized action plan based on your results

This project fills exactly that gap.

---

## What This Project Does

| Feature                                   | MyChart | This Project |
| ----------------------------------------- | ------- | ------------ |
| View lab results                          | Yes     | Yes          |
| General health library                    | Yes     | Yes          |
| Plain English explanation of YOUR results | No      | Yes          |
| Color coded risk level                    | No      | Yes          |
| ML risk classification model              | No      | Yes          |
| X-ray image analysis                      | No      | Yes          |
| Personalized action plan                  | No      | Yes          |
| Open source                               | No      | Yes          |
| Works without hospital login              | No      | Yes          |

---

## Real World Use Cases

| Patient Situation              | Problem                          | How This Helps                        |
| ------------------------------ | -------------------------------- | ------------------------------------- |
| Gets lab results at 10 PM      | Doctor unavailable               | Instant plain English explanation     |
| Immigrant patient              | Medical terms hard to understand | Simple clear language                 |
| No health insurance            | Minimal doctor explanation time  | Full report breakdown                 |
| Elderly patient                | Complex discharge summary        | Family can understand it              |
| Chronic condition patient      | Frequent lab reports             | Consistent plain English explanations |
| Preparing for specialist visit | Wants to ask better questions    | Understands their own report first    |
| No MyChart access              | Different hospital system        | Upload any PDF directly               |

## Features

### Core Features

- Upload lab reports (PDF) and get instant plain English explanation
- Upload X-ray images (JPG/PNG) and get AI-powered analysis
- Color coded risk classification — High, Medium, or Low
- Flagged abnormal values with normal range comparison
- Plain English explanation of what each abnormal value means
- Personalized action plan based on your results
- Report history — view all past uploaded reports
- Medical disclaimer on every report

### AI and ML Features

- LLM based text simplification (Groq LLaMA 3.3 70B)
- Vision AI for X-ray image analysis (Groq LLaMA 4 Scout)
- Trained ML risk classification models for 3 diseases:
  - Diabetes (SVM — 83.52% accuracy)
  - Heart Disease (Logistic Regression — 80.77% accuracy)
  - Kidney Disease (XGBoost — 98.18% accuracy)
- SMOTE balancing for imbalanced medical datasets
- Automatic disease type detection from lab values

### Supported File Types

- PDF lab reports
- PDF discharge summaries
- PDF radiology text reports
- JPG and PNG X-ray images
- Scanned PDF documents

### Technical Features

- RESTful FastAPI backend
- React frontend with responsive design
- PostgreSQL database for report history
- Full pipeline from upload to structured JSON response
- Modular architecture — swap AI models easily

## Tech Stack

### Backend

- **Python 3.11** — core language
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI server
- **PyMuPDF** — PDF text extraction
- **Pillow** — image processing
- **python-dotenv** — environment variable management

### Frontend

- **React 18** — UI framework
- **Tailwind CSS** — styling
- **Axios** — API calls

### Database

- **PostgreSQL 17** — report storage
- **psycopg2** — PostgreSQL connector

### AI and ML

- **Groq API** — LLM inference (free tier)
  - Text: llama-3.3-70b-versatile
  - Images: meta-llama/llama-4-scout-17b-16e-instruct
- **scikit-learn** — ML models
- **XGBoost** — gradient boosting
- **imbalanced-learn** — SMOTE oversampling
- **joblib** — model serialization
- **pandas + numpy** — data processing

### ML Datasets

- Pima Indians Diabetes Database (Kaggle)
- Cleveland Heart Disease Dataset (UCI)
- Chronic Kidney Disease Dataset (Kaggle)

### Development Tools

- **Git + GitHub** — version control
- **VS Code** — code editor
- **pgAdmin 4** — database management

### Planned

- **Docker** — containerization
- **Render** — cloud deployment
- **Claude API** — upgraded AI (Anthropic)

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 17
- Groq API key (free at https://console.groq.com)

### 1. Clone the Repository

```bash
git clone https://github.com/kanchankataria/medisimplify.git
cd medisimplify
```

### 2. Set Up Environment Variables

Create a `.env` file inside the `backend/` folder:

### 3. Install Backend Dependencies

```bash
cd backend
pip install fastapi uvicorn psycopg2-binary python-dotenv
pip install pymupdf pillow groq joblib
pip install pandas numpy scikit-learn xgboost imbalanced-learn
```

### 4. Set Up Database

- Install PostgreSQL 17
- Create a database named `medisimplify`
- Tables are created automatically on first run

### 5. Train ML Models

```bash
cd ml
pip install pandas numpy scikit-learn xgboost imbalanced-learn joblib
python fix_heart.py
python train_model.py
```

This creates `risk_models.pkl` in the `ml/` folder.

### 6. Start the Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
ML models loaded: ['diabetes', 'heart', 'kidney']

Database connected!

Application startup complete.

### 7. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 8. Start the Frontend

```bash
cd frontend
npm start
```

App opens at **http://localhost:3000**

---

## Usage

1. Open **http://localhost:3000** in your browser
2. Click the upload area or drag and drop a file
3. Supported formats: PDF lab reports, JPG/PNG X-ray images
4. Click **Analyze Report**
5. View your plain English summary, risk level, and action plan
6. Click **History** to see all past reports



## ML Model Results

### Overview
Three separate risk classification models were trained — one for 
each disease type. The system automatically detects which model 
to use based on the lab values present in the report.

### Pipeline Steps
1. Load raw data from CSV files
2. Create risk labels before feature engineering (prevents data leakage)
3. Handle missing values (median imputation)
4. Remove outliers (IQR method, 3x threshold)
5. Feature engineering (BMI category, glucose category, age groups, interaction features)
6. Encode categorical variables (LabelEncoder)
7. Scale features (StandardScaler)
8. Select best features (SelectKBest, top 15)
9. Apply SMOTE to fix class imbalance
10. Compare 5 models and select winner by CV score

### Models Compared
For each dataset, 5 models were trained and compared:
- Logistic Regression
- Random Forest
- XGBoost
- SVM (Support Vector Machine)
- KNN (K-Nearest Neighbors)

Winner selected by highest cross-validation score with 
no overfitting (train-CV gap below 10%).

### Final Results

| Dataset | Best Model | Test Accuracy | CV Score | Overfit? |
|---|---|---|---|---|
| Diabetes | SVM | 83.52% | 91.41% | No |
| Heart Disease | Logistic Regression | 80.77% | 84.74% | No |
| Kidney Disease | XGBoost | 98.18% | 99.17% | No |

### Risk Classification
Each model classifies patients into 3 risk levels:

| Risk Level | Color | Action |
|---|---|---|
| High | Red | See doctor within 7 days |
| Medium | Yellow | Schedule a follow-up |
| Low | Green | Continue regular checkups |

### Datasets Used

| Dataset | Source | Records | Target |
|---|---|---|---|
| Pima Indians Diabetes | Kaggle / UCI | 768 rows | Diabetes risk |
| Cleveland Heart Disease | UCI Machine Learning Repository | 303 rows | Heart disease risk |
| Chronic Kidney Disease | Kaggle | 400 rows | Kidney disease risk |

### Key ML Decisions

**Why median imputation not mean?**
Medical data always contains outliers. Median is not 
affected by extreme values unlike mean.

**Why SMOTE?**
Medical datasets are naturally imbalanced — far fewer 
High Risk patients than Low Risk. SMOTE creates synthetic 
minority samples to balance training data.

**Why compare 5 models?**
No single model performs best on all datasets. By comparing 
5 models we let the data decide the winner instead of 
assuming XGBoost always wins.

**Why create risk labels before feature engineering?**
Creating labels after feature engineering can cause data 
leakage — where the model indirectly learns from the target 
variable during training.