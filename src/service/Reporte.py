import io
import matplotlib.pyplot as plt
from fpdf import FPDF
from sqlmodel import Session, select, func
from fastapi import Depends
from database import get_session
from src.models.Reserva import Reserva
from src.models.Cancha import Cancha
from src.models.Cliente import Cliente
from sqlalchemy import desc


class ReportesService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def _generar_grafico_canchas_mas_usadas(self):
        # Consulta: Contar reservas agrupadas por cancha
        query = (
            select(Cancha.nombre, func.count(Reserva.id).label("total"))
            .join(Reserva)
            .group_by(Cancha.id)
            .order_by(desc("total"))
            .limit(5)
        )
        resultados = self.session.exec(query).all()

        if not resultados:
            return None

        nombres = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        # Configurar Matplotlib
        plt.figure(figsize=(6, 4))
        plt.bar(nombres, totales, color='#1E88E5')
        plt.title('Top Canchas Más Utilizadas')
        plt.xlabel('Cancha')
        plt.ylabel('Cantidad de Reservas')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Guardar en buffer de memoria
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        return img_buffer

    def _generar_grafico_mensual(self):
        # Consulta para SQLite: Agrupar por mes (strftime '%Y-%m')
        query = (
            select(func.strftime('%m', Reserva.fecha).label("mes"), func.count(Reserva.id))
            .group_by("mes")
            .order_by("mes")
        )
        resultados = self.session.exec(query).all()

        if not resultados:
            return None

        meses = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        plt.figure(figsize=(6, 4))
        plt.plot(meses, totales, marker='o', linestyle='-', color='#FFC107')
        plt.title('Evolución Mensual de Reservas')
        plt.xlabel('Mes')
        plt.ylabel('Cantidad')
        plt.grid(True)

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight')
        plt.close()
        img_buffer.seek(0)
        return img_buffer

    def generar_reporte_pdf(self) -> io.BytesIO:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)

        # --- TÍTULO ---
        pdf.set_font("helvetica", "B", 20)
        pdf.cell(0, 10, "Reporte de Gestión - Canchas Deportivas", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(10)

        # --- SECCIÓN 1: Listado de Reservas por Cliente ---
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "1. Reservas por Cliente (Detalle)", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("helvetica", size=10)
        clientes = self.session.exec(select(Cliente)).all()

        # Encabezado de tabla
        pdf.set_fill_color(200, 220, 255)
        pdf.cell(60, 8, "Cliente", border=1, fill=True)
        pdf.cell(80, 8, "Email", border=1, fill=True)
        pdf.cell(50, 8, "Total Reservas", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        for cliente in clientes:
            # Contar reservas de este cliente
            total = self.session.exec(select(func.count(Reserva.id)).where(Reserva.cliente_id == cliente.id)).one()
            pdf.cell(60, 8, f"{cliente.nombre} {cliente.apellido}", border=1)
            pdf.cell(80, 8, f"{cliente.email}", border=1)
            pdf.cell(50, 8, str(total), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(10)

        # --- SECCIÓN 2: Canchas más utilizadas (Gráfico) ---
        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "2. Canchas Más Utilizadas", new_x="LMARGIN", new_y="NEXT")

        img_barras = self._generar_grafico_canchas_mas_usadas()
        if img_barras:
            pdf.image(img_barras, w=150, x=30)
        else:
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, "No hay datos suficientes para generar el gráfico.")

        pdf.ln(10)

        # --- SECCIÓN 3: Utilización Mensual (Gráfico) ---
        # Verificamos si entra en la página, si no, salto de página
        if pdf.get_y() > 200:
            pdf.add_page()

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "3. Evolución Mensual de Reservas", new_x="LMARGIN", new_y="NEXT")

        img_lineas = self._generar_grafico_mensual()
        if img_lineas:
            pdf.image(img_lineas, w=150, x=30)
        else:
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, "No hay datos suficientes para generar el gráfico.")

        # --- SALIDA ---
        # Guardar PDF en un buffer de bytes para enviar por API
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        return pdf_output