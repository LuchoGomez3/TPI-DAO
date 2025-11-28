from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from src.service.Reporte import ReportesService

reportes_router = APIRouter(prefix="/reportes", tags=["Reportes"])


@reportes_router.get("/pdf")
def descargar_reporte_pdf(service: ReportesService = Depends()):
    pdf_buffer = service.generar_reporte_pdf()

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=reporte_canchas.pdf"}
    )