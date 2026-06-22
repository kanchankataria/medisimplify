from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pdf_parser import extract_text_from_pdf, is_scanned_pdf, pdf_to_images
from image_handler import prepare_image_for_claude, validate_image
from claude_service import simplify_text_report, simplify_image_report
from database import (
    create_tables,
    save_report,
    get_all_reports,
    get_report_by_id,
    delete_report,
)

app = FastAPI(
    title="MediSimplify API",
    description="AI-Powered Medical Report Analyzer",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Create database tables when server starts
@app.on_event("startup")
async def startup_event():
    try:
        create_tables()
        print("Database connected!")
    except Exception as e:
        print(f"Database not connected: {e}")
        print("Running without database for now...")


@app.get("/")
def root():
    return {"message": "MediSimplify API is running!", "version": "1.0.0"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_report(file: UploadFile = File(...)):
    """
    Main endpoint - accepts PDF or image
    and returns simplified medical report
    """
    file_bytes = await file.read()
    filename = file.filename.lower()
    result = None
    raw_text = ""
    file_type = ""

    try:
        # --- CASE 1: PDF file ---
        if filename.endswith(".pdf"):
            file_type = "pdf"

            if is_scanned_pdf(file_bytes):
                # Scanned PDF → convert to images → Claude Vision
                file_type = "scanned_pdf"
                images = pdf_to_images(file_bytes)
                # Use first page for analysis
                result = simplify_image_report(images[0], "image/png")
            else:
                # Text PDF → extract text → Claude
                raw_text = extract_text_from_pdf(file_bytes)
                result = simplify_text_report(raw_text)

        # --- CASE 2: Image file (X-ray, MRI) ---
        elif validate_image(filename):
            file_type = "image"
            base64_img, media_type = prepare_image_for_claude(file_bytes, filename)
            result = simplify_image_report(file_bytes, media_type)

        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, JPG, or PNG.",
            )

        # --- Save to database ---
        try:
            report_id = save_report(
                filename=file.filename,
                file_type=file_type,
                raw_text=raw_text,
                simplified_text=result.get("simplified_text", ""),
                risk_level=result.get("risk_level", "Unknown"),
                abnormal_values=result.get("abnormal_values", []),
                action_plan=result.get("action_plan", ""),
                disclaimer=result.get("disclaimer", ""),
            )
            result["report_id"] = report_id
        except Exception as db_error:
            print(f"Database save failed: {db_error}")
            result["report_id"] = None

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@app.get("/report/{report_id}")
def get_report(report_id: str):
    """Get a specific report by ID"""
    report = get_report_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@app.get("/history")
def get_history():
    """Get all past reports"""
    try:
        reports = get_all_reports()
        return {"reports": reports}
    except Exception as e:
        return {"reports": [], "error": str(e)}


@app.delete("/report/{report_id}")
def remove_report(report_id: str):
    """Delete a report"""
    deleted = delete_report(report_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
