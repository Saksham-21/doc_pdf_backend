from fastapi import FastAPI, File, UploadFile,Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from docx2pdf import convert
import io
import os
import pikepdf
import uuid
import aiofiles
import subprocess
import boto3
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def convert_to_pdf_libreoffice(docx_path, output_dir):
    pdf_path = docx_path.replace(".docx", ".pdf")
    command = ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", output_dir, docx_path]
    subprocess.run(command, check=True)
    return pdf_path


@app.post("/convert-to-pdf")
async def convert_to_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        return {"error": "Only .docx files are supported"}
    unique_filename = str(uuid.uuid4()) + ".docx"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    pdf_path = file_path.replace(".docx", ".pdf")
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())
        # convert(file_path)
        pdf_path =convert_to_pdf_libreoffice(file_path, UPLOAD_DIR)
        async with aiofiles.open(pdf_path, "rb") as f:
            pdf_content = await f.read()
        return StreamingResponse(io.BytesIO(pdf_content), media_type="application/pdf")
            
    except Exception as e:
        return {"error": str(e)}

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            
            
            
@app.post("/convert-to-encrypted-pdf")
async def convert_to_encrypted_pdf(file: UploadFile = File(...), password: str = Form(...)):
    if not file.filename.endswith(".docx"):
        return {"error": "Only .docx files are supported"}
    
    unique_filename = str(uuid.uuid4()) + ".docx"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    pdf_path = file_path.replace(".docx", ".pdf")
    encrypted_pdf_path = file_path.replace(".docx", "_encrypted.pdf")
    
    try:
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(await file.read())
        # convert(file_path)
        pdf_path =convert_to_pdf_libreoffice(file_path, UPLOAD_DIR)
        pdf=pikepdf.Pdf.open(pdf_path)
        pdf.save(
                encrypted_pdf_path,
                encryption=pikepdf.Encryption(owner=password,user="xyz",allow=pikepdf.Permissions(extract=False))
            )
        async with aiofiles.open(encrypted_pdf_path, "rb") as encrypted_pdf:
            pdf.close()
            pdf_content = await encrypted_pdf.read()
        return StreamingResponse(io.BytesIO(pdf_content),media_type="application/pdf")
            
    except Exception as e:
        return {"error": str(e)}

    finally:
        for path in [file_path, pdf_path, encrypted_pdf_path]:
            if os.path.exists(path):
                os.remove(path)