from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
import pandas as pd
import numpy as np
import logging
import json
import traceback
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Patient Cohort Simulator")

# Enable CORS with more specific options
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://patient-cohort-simulator-frontend.onrender.com"  # Deployed frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

class LabResults(BaseModel):
    glucose: float = Field(default=100.0)
    cholesterol: float = Field(default=200.0)

class PatientData(BaseModel):
    age: int
    gender: str
    conditions: List[str]
    medications: List[str]
    lab_results: LabResults

class CohortCriteria(BaseModel):
    age_mean: float = Field(default=50.0)
    age_std: float = Field(default=15.0)
    glucose_mean: float = Field(default=100.0)
    glucose_std: float = Field(default=20.0)
    cholesterol_mean: float = Field(default=200.0)
    cholesterol_std: float = Field(default=40.0)
    conditions: List[str] = Field(default=["Diabetes", "Hypertension", "Asthma", "Arthritis"])
    medications: List[str] = Field(default=["Metformin", "Lisinopril", "Albuterol", "Ibuprofen"])

    @validator('age_std', 'glucose_std', 'cholesterol_std')
    def validate_std(cls, v):
        if v <= 0:
            raise ValueError('Standard deviation must be positive')
        return v

class CohortRequest(BaseModel):
    criteria: CohortCriteria
    size: int = Field(gt=0, le=1000)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "detail": str(exc),
        "traceback": traceback.format_exc()
    }
    logger.error(f"Global error handler caught: {error_detail}")
    return JSONResponse(
        status_code=500,
        content=error_detail
    )

@app.get("/")
async def root():
    return {"message": "Patient Cohort Simulator API"}

@app.post("/simulate-cohort")
async def simulate_cohort(request: CohortRequest):
    start_time = time.time()
    try:
        logger.info(f"Received cohort simulation request with size: {request.size}")
        logger.info(f"Criteria: {request.criteria.dict()}")
        
        # Generate synthetic patient data based on criteria
        patients = generate_synthetic_patients(request.criteria.dict(), request.size)
        logger.info(f"Generated {len(patients)} synthetic patients in {time.time() - start_time:.2f} seconds")
        
        # Generate summary statistics
        summary = generate_cohort_summary(patients)
        logger.info(f"Generated cohort summary in {time.time() - start_time:.2f} seconds")
        
        # Simple clustering based on age ranges
        clusters = perform_simple_clustering(patients)
        logger.info(f"Completed clustering analysis in {time.time() - start_time:.2f} seconds")
        
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        
        return {
            "cohort": patients,
            "clusters": clusters,
            "summary": summary,
            "processing_time": total_time
        }
    except Exception as e:
        error_detail = {
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error in simulate_cohort: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)

def generate_synthetic_patients(criteria: dict, size: int) -> List[dict]:
    try:
        logger.info(f"Generating {size} patients with criteria: {criteria}")
        # Pre-generate random numbers for better performance
        ages = np.random.normal(
            criteria.get("age_mean", 50),
            criteria.get("age_std", 15),
            size=size
        ).astype(int)
        
        genders = np.random.choice(["M", "F"], size=size, p=[0.5, 0.5])
        
        # Pre-generate condition and medication counts
        condition_counts = np.random.randint(1, 4, size=size)
        medication_counts = np.random.randint(1, 3, size=size)
        
        # Pre-generate lab results
        glucose_values = np.random.normal(
            criteria.get("glucose_mean", 100),
            criteria.get("glucose_std", 20),
            size=size
        )
        cholesterol_values = np.random.normal(
            criteria.get("cholesterol_mean", 200),
            criteria.get("cholesterol_std", 40),
            size=size
        )
        
        patients = []
        for i in range(size):
            patient = {
                "id": f"P{i+1}",
                "age": int(ages[i]),
                "gender": genders[i],
                "conditions": np.random.choice(
                    criteria.get("conditions", ["Diabetes", "Hypertension", "Asthma", "Arthritis"]),
                    size=condition_counts[i],
                    replace=False
                ).tolist(),
                "medications": np.random.choice(
                    criteria.get("medications", ["Metformin", "Lisinopril", "Albuterol", "Ibuprofen"]),
                    size=medication_counts[i],
                    replace=False
                ).tolist(),
                "lab_results": {
                    "glucose": float(glucose_values[i]),
                    "cholesterol": float(cholesterol_values[i])
                }
            }
            patients.append(patient)
        return patients
    except Exception as e:
        error_detail = {
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error in generate_synthetic_patients: {error_detail}")
        raise

def perform_simple_clustering(patients: List[dict]) -> dict:
    try:
        logger.info("Starting simple clustering analysis")
        # Simple clustering based on age ranges
        age_clusters = {
            "young": {"min": 0, "max": 30},
            "middle": {"min": 31, "max": 60},
            "senior": {"min": 61, "max": 100}
        }
        
        # Use numpy for faster array operations
        ages = np.array([p["age"] for p in patients])
        cluster_assignments = np.zeros(len(patients), dtype=int)
        cluster_assignments[ages > 60] = 2
        cluster_assignments[(ages > 30) & (ages <= 60)] = 1
        
        # Calculate cluster centers
        cluster_centers = []
        for cluster_id in range(3):
            cluster_ages = ages[cluster_assignments == cluster_id]
            if len(cluster_ages) > 0:
                avg_age = float(np.mean(cluster_ages))
                cluster_centers.append([avg_age, 0, 0, 0, 0])
            else:
                cluster_centers.append([0, 0, 0, 0, 0])
        
        return {
            "cluster_assignments": cluster_assignments.tolist(),
            "cluster_centers": cluster_centers,
            "cluster_labels": ["Young", "Middle-aged", "Senior"]
        }
    except Exception as e:
        error_detail = {
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error in perform_simple_clustering: {error_detail}")
        raise

def generate_cohort_summary(patients: List[dict]) -> dict:
    try:
        logger.info("Generating cohort summary")
        # Use numpy for faster array operations
        ages = np.array([p["age"] for p in patients])
        conditions = [c for p in patients for c in p["conditions"]]
        medications = [m for p in patients for m in p["medications"]]
        
        return {
            "total_patients": len(patients),
            "age_stats": {
                "mean": float(np.mean(ages)),
                "std": float(np.std(ages)),
                "min": int(np.min(ages)),
                "max": int(np.max(ages))
            },
            "condition_frequency": pd.Series(conditions).value_counts().to_dict(),
            "medication_frequency": pd.Series(medications).value_counts().to_dict()
        }
    except Exception as e:
        error_detail = {
            "detail": str(e),
            "traceback": traceback.format_exc()
        }
        logger.error(f"Error in generate_cohort_summary: {error_detail}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 