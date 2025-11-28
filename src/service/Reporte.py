import io
from datetime import datetime, timedelta
import pandas as pd
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

        # --- MEJORA VISUAL: Etiquetas en Diagonal ---

        plt.figure(figsize=(8, 5))
        bars = plt.bar(nombres, totales, color='grey', edgecolor='black', width=0.6)

        plt.title('Top 5 Canchas Más Utilizadas', fontsize=12, fontweight='bold')
        plt.xlabel('Cancha')
        plt.ylabel('Reservas')
        plt.grid(axis='y', linestyle='--', alpha=0.5)

        plt.xticks(rotation=45, ha='right')

        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}',
                     ha='center', va='bottom')

        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        img_buffer.seek(0)
        return img_buffer

    def _generar_grafico_mensual(self):
        query = (
            select(func.strftime('%Y-%m', Reserva.fecha).label("mes"), func.count(Reserva.id))
            .group_by("mes")
            .order_by("mes")
        )
        resultados = self.session.exec(query).all()

        if not resultados:
            return None

        meses = [r[0] for r in resultados]
        totales = [r[1] for r in resultados]

        plt.figure(figsize=(8, 4))
        plt.plot(meses, totales, marker='o', linestyle='-', color='#FFC107', linewidth=2)

        plt.title('Evolución Mensual de Reservas', fontsize=12, fontweight='bold')
        plt.xlabel('Mes')
        plt.ylabel('Cantidad')
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.xticks(rotation=45)
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
        plt.close()
        img_buffer.seek(0)
        return img_buffer

    def _generar_grafico_reservas_por_periodo(self):
        fecha_limite = datetime.now().date() - timedelta(days=30)

        query = (
            select(Reserva.fecha, Cancha.nombre)
            .join(Cancha)
            .where(Reserva.fecha >= fecha_limite)
            .order_by(Reserva.fecha)
        )
        resultados = self.session.exec(query).all()

        if not resultados:
            return None

        data = [{"Fecha": r[0], "Cancha": r[1]} for r in resultados]
        df = pd.DataFrame(data)
        df["Fecha"] = pd.to_datetime(df["Fecha"]).dt.date


        df_pivot = df.groupby(['Fecha', 'Cancha']).size().unstack(fill_value=0)


        plt.figure(figsize=(10, 6))

        ax = df_pivot.plot(kind='bar', stacked=True, figsize=(10, 5), width=0.8, colormap='tab20')

        plt.title('Distribución Diaria de Reservas por Cancha (Últimos 30 días)', fontsize=12, fontweight='bold')
        plt.xlabel('Fecha')
        plt.ylabel('Cantidad de Reservas')
        plt.grid(axis='y', linestyle='--', alpha=0.3)

        n = len(df_pivot.index)
        step = max(1, n // 10)
        labels = [d.strftime('%Y-%m-%d') for d in df_pivot.index[::step]]
        
        plt.xticks(
            ticks=range(0, n, step),
            labels=labels,
            rotation=45,
            ha='right'
        )

        plt.legend(title='Cancha', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', bbox_inches='tight', dpi=100)
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
        pdf.ln(5)

        # --- SECCIÓN 1: Listado de Reservas por Cliente ---

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "1. Reservas por Cliente (Top 15)", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("helvetica", size=10)

        clientes = self.session.exec(select(Cliente).limit(15)).all()


        pdf.set_fill_color(200, 220, 255)
        pdf.cell(60, 8, "Cliente", border=1, fill=True)
        pdf.cell(80, 8, "Email", border=1, fill=True)
        pdf.cell(30, 8, "Reservas", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        for cliente in clientes:
            total = self.session.exec(select(func.count(Reserva.id)).where(Reserva.cliente_id == cliente.id)).one()
            pdf.cell(60, 8, f"{cliente.nombre} {cliente.apellido}", border=1)
            pdf.cell(80, 8, f"{cliente.email}", border=1)
            pdf.cell(30, 8, str(total), border=1, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(5)

        # --- SECCIÓN 2: Canchas más utilizadas (Gráfico Barras) ---

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "2. Canchas Más Utilizadas", new_x="LMARGIN", new_y="NEXT")

        img_barras = self._generar_grafico_canchas_mas_usadas()
        if img_barras:
            pdf.image(img_barras, w=160, x=25)
        else:
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, "No hay datos suficientes para generar el gráfico.")

        pdf.ln(5)

        # --- SECCIÓN 3: Utilización Mensual (Gráfico Líneas) ---

        pdf.add_page()

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "3. Evolución Mensual de Reservas", new_x="LMARGIN", new_y="NEXT")

        img_lineas = self._generar_grafico_mensual()
        if img_lineas:
            pdf.image(img_lineas, w=170, x=20)
        else:
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, "No hay datos suficientes.")

        pdf.ln(5)

        # --- SECCIÓN 4: Reservas por Período (Apiladas) ---

        pdf.set_font("helvetica", "B", 14)
        pdf.cell(0, 10, "4. Distribución Diaria (Últimos 30 días)", new_x="LMARGIN", new_y="NEXT")

        img_apiladas = self._generar_grafico_reservas_por_periodo()
        if img_apiladas:
            pdf.image(img_apiladas, w=170, x=20)
        else:
            pdf.set_font("helvetica", "I", 10)
            pdf.cell(0, 10, "No hay datos recientes para este período.")

        # --- SALIDA ---
        pdf_output = io.BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)
        return pdf_output