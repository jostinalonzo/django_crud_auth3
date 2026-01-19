"""
Generador de PDFs de hojas de vida usando ReportLab
Incluye referencias a certificados en el PDF
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    BaseDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Frame,
    PageTemplate,
    FrameBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
from PIL import Image as PILImage
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tempfile
from django.core.files.storage import default_storage
from django.conf import settings


class CVPDFGenerator:
    """Generador de PDFs para hojas de vida con ReportLab"""
    
    def __init__(self, datos_personales):
        self.datos = datos_personales
        self.user = datos_personales.user
        self.story = []
        self.styles = getSampleStyleSheet()
        self.certificados_para_incrustar = []  # Lista de PDFs a incrustar
        self.temp_files = []  # Lista de archivos temporales para limpiar
        self._create_custom_styles()
        # Configuración visual (colores y dimensiones)
        self.sidebar_bg = colors.HexColor('#6b6bf3')  # aproximación del gradiente púrpura
        self.sidebar_text = colors.white
        self.accent = colors.HexColor('#667eea')
        self.sidebar_width = 2.2*inch
        self.page_size = letter
    
    def _create_custom_styles(self):
        """Crea estilos personalizados para el PDF"""
        # Estilo para títulos de secciones
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading1'],
            fontSize=15,
            textColor=colors.HexColor('#1a5490'),
            spaceAfter=12,
            spaceBefore=12,
            borderBottom=1,
            borderColor=colors.HexColor('#1a5490'),
            paddingBottom=6
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='SubTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=6,
            bold=True
        ))
        
        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            alignment=TA_JUSTIFY
        ))
    
    def _download_file_from_storage(self, file_field):
        """
        Descarga un archivo desde el storage (local o Azure) y retorna una ruta temporal.
        Funciona tanto con archivos locales como con Azure Storage.
        
        Args:
            file_field: Campo de archivo de Django (ImageField, FileField, etc.)
            
        Returns:
            tuple: (ruta_temporal, content_bytes) - la ruta y los bytes del archivo
        """
        try:
            # Si el archivo está vacío
            if not file_field or not file_field.name:
                return None, None
            
            content = None

            # Normalizar el nombre para evitar rutas absolutas (Windows/Linux)
            original_name = str(file_field.name)
            norm_name = original_name.replace('\\', '/').lstrip('/')

            # Candidatos a probar con default_storage
            candidates = []
            candidates.append(norm_name)

            # Si incluye unidad (p. ej. C:/...) o es absoluta, intentar recortar
            if ':' in norm_name:
                after_drive = norm_name.split(':', 1)[1].lstrip('/')
                candidates.append(after_drive)

            # Si contiene 'media/', probar desde ahí hacia delante
            if 'media/' in norm_name:
                after_media = norm_name.split('media/', 1)[1]
                candidates.append(after_media)

            # Fallback al nombre base
            candidates.append(os.path.basename(norm_name))

            # Intentar abrir con default_storage usando los candidatos
            opened = False
            last_err = None
            for name in candidates:
                try:
                    with default_storage.open(name, 'rb') as f:
                        content = f.read()
                        opened = True
                        break
                except Exception as e:
                    last_err = e
                    continue

            if not opened:
                # Fallback: intentar ruta absoluta bajo MEDIA_ROOT
                try:
                    abs_path = os.path.join(settings.MEDIA_ROOT, os.path.basename(norm_name))
                    if os.path.exists(abs_path):
                        with open(abs_path, 'rb') as f:
                            content = f.read()
                            opened = True
                except Exception as e:
                    last_err = e

                if not opened:
                    print(f"Error leyendo archivo desde storage: {last_err}")
                    return None, None
            
            # Crear archivo temporal
            if content:
                # Obtener extensión del archivo
                _, ext = os.path.splitext(os.path.basename(norm_name))
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_path = temp_file.name
                temp_file.write(content)
                temp_file.close()
                
                # Guardar path temporal para limpieza posterior
                self.temp_files.append(temp_path)
                
                return temp_path, content
        
        except Exception as e:
            print(f"Error descargando archivo desde storage: {e}")
        
        return None, None

    def _add_inline_certificate_image(self, file_field, max_width=3.6*inch):
        """Inserta una imagen de certificado dentro del contenido principal."""
        try:
            temp_path, content = self._download_file_from_storage(file_field)
            if not temp_path or not content:
                return

            # Calcular tamaño manteniendo proporción
            try:
                pil_img = PILImage.open(temp_path)
                w, h = pil_img.size
                # Convertir de px a inches aproximando 96 dpi si no hay info
                # Escalamos por ancho
                scale = (max_width) / (w / 96.0 * inch)
                # Si el dpi no está, asumimos 96; usaremos proporciones con ReportLab directamente
            except Exception:
                pil_img = None

            try:
                img = Image(temp_path)
                if pil_img:
                    # Escalar por ancho
                    iw, ih = pil_img.size
                    target_w = max_width
                    target_h = ih * (target_w / iw)
                    img._restrictSize(target_w, target_h)
                else:
                    img._restrictSize(max_width, max_width*0.75)
                self.story.append(img)
                self.story.append(Spacer(1, 0.1*inch))
            except Exception as e:
                print(f"Error añadiendo imagen de certificado: {e}")
        except Exception as e:
            print(f"Error procesando imagen de certificado: {e}")
    
    def _add_header(self):
        """Añade encabezado (lado derecho) con nombre y descripción de perfil"""
        # Título con nombre completo
        nombre_completo = f"{self.datos.nombres} {self.datos.apellidos}".upper()
        title_style = ParagraphStyle(
            'RightTitle',
            parent=self.styles['Title'],
            textColor=self.accent,
            fontSize=18,
            spaceAfter=6,
        )
        self.story.append(Paragraph(f"<b>{nombre_completo}</b>", title_style))

        # Descripción del perfil
        if self.datos.descripcionperfil:
            descripcion = Paragraph(
                f"<i>{self.datos.descripcionperfil}</i>",
                self.styles['NormalText']
            )
            self.story.append(descripcion)
            self.story.append(Spacer(1, 0.12*inch))
    
    def _add_datos_personales(self):
        """Añade sección de datos personales (lado derecho)"""
        self.story.append(Paragraph("DATOS PERSONALES", self.styles['SectionTitle']))
        
        datos = [
            ['Cédula de Identidad:', self.datos.numerocedula],
            ['Sexo:', 'Hombre' if self.datos.sexo == 'H' else 'Mujer' if self.datos.sexo else 'No especificado'],
            ['Fecha de Nacimiento:', str(self.datos.fechanacimiento) if self.datos.fechanacimiento else 'N/A'],
            ['Nacionalidad:', self.datos.nacionalidad or 'N/A'],
            ['Lugar de Nacimiento:', self.datos.lugarnacimiento or 'N/A'],
            ['Estado Civil:', self.datos.estadocivil or 'N/A'],
            ['Licencia de Conducir:', self.datos.licenciaconducir or 'N/A'],
        ]
        
        direccion_data = []
        if self.datos.direcciondomiciliaria:
            direccion_data.append(['Dirección Domiciliaria:', self.datos.direcciondomiciliaria])
        if self.datos.direcciontrabajo:
            direccion_data.append(['Dirección de Trabajo:', self.datos.direcciontrabajo])
        
        tabla_datos = Table(datos + direccion_data, colWidths=[1.8*inch, 3.2*inch])
        tabla_datos.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        self.story.append(tabla_datos)
        self.story.append(Spacer(1, 0.2*inch))

    def _build_sidebar(self):
        """Construye el contenido del sidebar izquierdo (perfil + contacto)."""
        sidebar_story = []

        # Imagen de perfil
        if self.datos.fotoperfil:
            try:
                temp_path, _ = self._download_file_from_storage(self.datos.fotoperfil)
                if temp_path and os.path.exists(temp_path):
                    try:
                        # Crear imagen circular con máscara
                        from reportlab.graphics.shapes import Drawing, Circle
                        from reportlab.graphics import renderPDF
                        
                        img = Image(temp_path, width=1.4*inch, height=1.4*inch, mask='auto')
                        # Aplicar máscara circular manualmente recortando la imagen
                        try:
                            pil_img = PILImage.open(temp_path)
                            # Crear máscara circular
                            from PIL import ImageDraw
                            mask = PILImage.new('L', pil_img.size, 0)
                            draw = ImageDraw.Draw(mask)
                            draw.ellipse((0, 0) + pil_img.size, fill=255)
                            # Aplicar máscara
                            pil_img.putalpha(mask)
                            # Guardar temporalmente
                            circular_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
                            pil_img.save(circular_temp.name, 'PNG')
                            circular_temp.close()
                            self.temp_files.append(circular_temp.name)
                            # Usar la imagen circular
                            img = Image(circular_temp.name, width=1.4*inch, height=1.4*inch)
                        except Exception:
                            pass  # Si falla, usar imagen normal
                        
                        sidebar_story.append(img)
                        sidebar_story.append(Spacer(1, 0.15*inch))
                    except Exception as e:
                        print(f"Error creando imagen para PDF: {e}")
            except Exception as e:
                print(f"Error cargando foto de perfil: {e}")

        # Nombre
        nombre_completo = f"{self.datos.nombres} {self.datos.apellidos}".upper()
        name_style = ParagraphStyle(
            'SidebarName',
            parent=self.styles['Heading2'],
            textColor=self.sidebar_text,
            fontSize=12,
            alignment=TA_LEFT,
            spaceAfter=4,
        )
        sidebar_story.append(Paragraph(f"<b>{nombre_completo}</b>", name_style))

        # Contacto
        contact_style = ParagraphStyle(
            'SidebarContact',
            parent=self.styles['Normal'],
            textColor=self.sidebar_text,
            fontSize=9,
            leading=12,
        )
        if self.user.email:
            sidebar_story.append(Paragraph(f"✉ {self.user.email}", contact_style))
        if self.datos.telefonoconvencional:
            sidebar_story.append(Paragraph(f"☎ {self.datos.telefonoconvencional}", contact_style))
        if self.datos.telefonofijo:
            sidebar_story.append(Paragraph(f"☎ {self.datos.telefonofijo}", contact_style))
        if self.datos.sitioweb:
            sidebar_story.append(Paragraph(f"🌐 {self.datos.sitioweb}", contact_style))
        sidebar_story.append(Spacer(1, 0.12*inch))

        # Resumen personal clave
        info_style = ParagraphStyle(
            'SidebarInfo',
            parent=self.styles['Normal'],
            textColor=self.sidebar_text,
            fontSize=8.5,
            leading=11,
        )
        if self.datos.nacionalidad:
            sidebar_story.append(Paragraph(f"Nacionalidad: {self.datos.nacionalidad}", info_style))
        if self.datos.lugarnacimiento:
            sidebar_story.append(Paragraph(f"Lugar de nacimiento: {self.datos.lugarnacimiento}", info_style))
        if self.datos.estadocivil:
            sidebar_story.append(Paragraph(f"Estado civil: {self.datos.estadocivil}", info_style))

        return sidebar_story

    def _draw_sidebar_background(self, canvas, doc):
        """Dibuja el fondo del sidebar en cada página."""
        canvas.saveState()
        canvas.setFillColor(self.sidebar_bg)
        width, height = self.page_size
        canvas.rect(0, 0, self.sidebar_width, height, stroke=0, fill=1)
        canvas.restoreState()
    
    def _add_experiencia_laboral(self):
        """Añade sección de experiencia laboral"""
        experiencias = self.datos.experiencias_laborales.filter(activo=True)
        
        if not experiencias.exists():
            return
        
        self.story.append(Paragraph("EXPERIENCIA LABORAL", self.styles['SectionTitle']))
        
        for exp in experiencias:
            # Cargo y empresa
            exp_title = f"<b>{exp.cargodesempenado}</b>"
            if exp.nombreempresa:
                exp_title += f" - {exp.nombreempresa}"
            exp_style = ParagraphStyle(
                'ExpTitle',
                parent=self.styles['NormalText'],
                leftIndent=12,
            )
            self.story.append(Paragraph(exp_title, exp_style))
            
            # Fechas y lugar
            fecha_inicio = exp.fechainiciogestion.strftime('%b %Y') if exp.fechainiciogestion else ''
            fecha_fin = exp.fechafingestion.strftime('%b %Y') if exp.fechafingestion else 'Presente'
            periodos = f"<i>{fecha_inicio} - {fecha_fin}</i>"
            if exp.lugarempresa:
                periodos += f" | {exp.lugarempresa}"
            periodos_style = ParagraphStyle(
                'ExpPeriodos',
                parent=self.styles['Normal'],
                leftIndent=12,
            )
            self.story.append(Paragraph(periodos, periodos_style))
            
            # Descripción
            if exp.descripcionfunciones:
                desc_style = ParagraphStyle(
                    'ExpDesc',
                    parent=self.styles['NormalText'],
                    leftIndent=12,
                )
                self.story.append(Paragraph(
                    exp.descripcionfunciones,
                    desc_style
                ))
            
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_reconocimientos(self):
        """Añade sección de reconocimientos con imágenes de certificados"""
        reconocimientos = self.datos.reconocimientos.filter(activo=True)
        
        if not reconocimientos.exists():
            return
        
        self.story.append(Paragraph("RECONOCIMIENTOS", self.styles['SectionTitle']))
        
        for reco in reconocimientos:
            # Tipo y entidad
            titulo = f"<b>{reco.get_tiporeconocimiento_display()}</b> - {reco.entidadpatrocinadora}"
            titulo_style = ParagraphStyle(
                'RecoTitle',
                parent=self.styles['NormalText'],
                leftIndent=12,
            )
            self.story.append(Paragraph(titulo, titulo_style))
            
            # Fecha
            if reco.fechareconocimiento:
                fecha = reco.fechareconocimiento.strftime('%d de %B de %Y')
                fecha_style = ParagraphStyle(
                    'RecoFecha',
                    parent=self.styles['Normal'],
                    leftIndent=12,
                )
                self.story.append(Paragraph(f"<i>Fecha: {fecha}</i>", fecha_style))
            
            # Descripción
            if reco.descripcionreconocimiento:
                desc_style = ParagraphStyle(
                    'RecoDesc',
                    parent=self.styles['NormalText'],
                    leftIndent=12,
                )
                self.story.append(Paragraph(
                    reco.descripcionreconocimiento,
                    desc_style
                ))
            
            # Certificado
            if reco.certificado:
                cert_name = os.path.basename(reco.certificado.name)
                
                # Verificar que sea un PDF
                if cert_name.lower().endswith('.pdf'):
                    self.certificados_para_incrustar.append({
                        'file_field': reco.certificado,
                        'titulo': f"{reco.get_tiporeconocimiento_display()} - {reco.entidadpatrocinadora}"
                    })
                    self.story.append(Paragraph(
                        f"<b>📎 Certificado:</b> {cert_name} (Incrustado abajo)",
                        self.styles['Normal']
                    ))
                else:
                    # Insertar imagen en el contenido
                    self.story.append(Paragraph(f"<b>📎 Certificado:</b> {cert_name}", self.styles['Normal']))
                    self._add_inline_certificate_image(reco.certificado)
            
            self.story.append(Spacer(1, 0.15*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_cursos(self):
        """Añade sección de cursos realizados con imágenes de certificados"""
        cursos = self.datos.cursos_realizados.filter(activo=True)
        
        if not cursos.exists():
            return
        
        self.story.append(Paragraph("CURSOS Y CAPACITACIONES", self.styles['SectionTitle']))
        
        for curso in cursos:
            # Nombre del curso
            titulo = f"<b>{curso.nombrecurso}</b>"
            self.story.append(Paragraph(titulo, self.styles['NormalText']))
            
            # Entidad y fechas
            entidad = f"<i>{curso.entidadpatrocinadora}</i>"
            if curso.fechainicio or curso.fechafin:
                fecha_inicio = curso.fechainicio.strftime('%b %Y') if curso.fechainicio else ''
                fecha_fin = curso.fechafin.strftime('%b %Y') if curso.fechafin else ''
                fechas = f" | {fecha_inicio} - {fecha_fin}"
                entidad += fechas
            self.story.append(Paragraph(entidad, self.styles['Normal']))
            
            # Horas
            if curso.totalhoras:
                self.story.append(Paragraph(f"Horas: {curso.totalhoras}", self.styles['Normal']))
            
            # Descripción
            if curso.descripcioncurso:
                self.story.append(Paragraph(
                    curso.descripcioncurso,
                    self.styles['NormalText']
                ))
            
            # Certificado
            if curso.certificado:
                cert_name = os.path.basename(curso.certificado.name)
                
                # Verificar que sea un PDF
                if cert_name.lower().endswith('.pdf'):
                    self.certificados_para_incrustar.append({
                        'file_field': curso.certificado,
                        'titulo': f"Curso: {curso.nombrecurso}"
                    })
                    self.story.append(Paragraph(
                        f"<b>📎 Certificado:</b> {cert_name} (Incrustado abajo)",
                        self.styles['Normal']
                    ))
                else:
                    # Insertar imagen en el contenido
                    self.story.append(Paragraph(f"<b>📎 Certificado:</b> {cert_name}", self.styles['Normal']))
                    self._add_inline_certificate_image(curso.certificado)
            
            self.story.append(Spacer(1, 0.15*inch))

        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_productos_academicos(self):
        """Añade sección de productos académicos"""
        productos = self.datos.productos_academicos.filter(activo=True)
        
        if not productos.exists():
            return
        
        self.story.append(Paragraph("PRODUCTOS ACADÉMICOS", self.styles['SectionTitle']))
        
        for prod in productos:
            titulo = f"<b>{prod.nombrerecurso}</b> ({prod.clasificador})"
            self.story.append(Paragraph(titulo, self.styles['NormalText']))
            
            if prod.descripcion:
                self.story.append(Paragraph(prod.descripcion, self.styles['Normal']))
            
            self.story.append(Spacer(1, 0.05*inch))
        
        self.story.append(Spacer(1, 0.1*inch))
    
    def _add_footer(self):
        """Añade pie de página"""
        self.story.append(Spacer(1, 0.15*inch))
        fecha_generacion = datetime.now().strftime('%d de %B de %Y')
        footer = Paragraph(
            f"<i>Generado el: {fecha_generacion}</i>",
            ParagraphStyle(
                'Footer',
                parent=self.styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        self.story.append(footer)
    
    def generate(self):
        """
        Genera el PDF y lo retorna como BytesIO
        Incluye certificados incrustados al final
        
        Returns:
            BytesIO con el contenido del PDF
        """
        try:
            # Crear documento en memoria
            pdf_buffer = BytesIO()
            # Definir frames para layout tipo "sidebar + contenido"
            width, height = self.page_size
            margin = 0.5*inch

            left_frame = Frame(
                x1=margin/2,
                y1=margin,
                width=self.sidebar_width - margin/2,
                height=height - 2*margin,
                leftPadding=6,
                rightPadding=6,
                topPadding=6,
                bottomPadding=6,
                showBoundary=0,
            )

            right_frame = Frame(
                x1=self.sidebar_width + margin/2,
                y1=margin,
                width=width - (self.sidebar_width + margin) ,
                height=height - 2*margin,
                leftPadding=24,
                rightPadding=6,
                topPadding=6,
                bottomPadding=6,
                showBoundary=0,
            )

            # Plantilla de página con fondo de sidebar
            page_template = PageTemplate(
                id='SidebarTemplate',
                frames=[left_frame, right_frame],
                onPage=self._draw_sidebar_background,
            )

            doc = BaseDocTemplate(
                pdf_buffer,
                pagesize=self.page_size,
                rightMargin=margin,
                leftMargin=margin,
                topMargin=margin,
                bottomMargin=margin,
            )
            doc.addPageTemplates([page_template])

            # Construir el contenido: primero el sidebar, luego el contenido principal
            sidebar_story = self._build_sidebar()
            main_story = []

            # Encabezado y secciones (derecha)
            # Se construyen en una lista temporal y se concatenan luego
            # Header derecha
            temp_story = []
            # Usar los métodos existentes para llenar contenido
            # Encabezado
            self.story = temp_story
            self._add_header()
            self._add_datos_personales()

            if self.datos.experiencias_laborales.filter(activo=True).exists():
                self._add_experiencia_laboral()
            if self.datos.reconocimientos.filter(activo=True).exists():
                self._add_reconocimientos()
            if self.datos.cursos_realizados.filter(activo=True).exists():
                self._add_cursos()
            if self.datos.productos_academicos.filter(activo=True).exists():
                self._add_productos_academicos()
            self._add_footer()

            main_story.extend(temp_story)

            # Historia final con FrameBreak para cambiar de columna
            final_story = []
            final_story.extend(sidebar_story)
            final_story.append(FrameBreak())
            final_story.extend(main_story)

            # Generar el PDF principal
            doc.build(final_story)
            
            # Si hay certificados, incrustarlos
            if self.certificados_para_incrustar:
                pdf_buffer.seek(0)
                pdf_buffer = self._incrustar_certificados(pdf_buffer)
            
            # Limpiar archivos temporales (imágenes descargadas de Azure)
            if hasattr(self, 'temp_files'):
                for temp_file in self.temp_files:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
            
            # Retornar al inicio del buffer
            pdf_buffer.seek(0)
            return pdf_buffer
        
        except Exception as e:
            print(f"Error generando PDF: {e}")
            # Limpiar temporales en caso de error
            if hasattr(self, 'temp_files'):
                for temp_file in self.temp_files:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
            return None
    
    def _incrustar_certificados(self, pdf_principal_buffer):
        """
        Incrustra los PDFs de certificados al final del PDF principal.
        Funciona automáticamente con archivos locales y Azure Storage.
        """
        try:
            # Lector del PDF principal
            pdf_reader = PdfReader(pdf_principal_buffer)
            writer = PdfWriter()
            
            # Copiar todas las páginas del PDF principal
            for page_num in range(len(pdf_reader.pages)):
                writer.add_page(pdf_reader.pages[page_num])
            
            # Agregar los certificados
            for cert_info in self.certificados_para_incrustar:
                # Obtener el objeto del archivo (puede tener 'url' o 'path')
                cert_field = cert_info.get('file_field')
                cert_titulo = cert_info.get('titulo', 'Certificado')
                
                if not cert_field:
                    continue
                
                try:
                    # Descargar el certificado desde storage (local o Azure)
                    temp_path, content = self._download_file_from_storage(cert_field)
                    
                    if not temp_path or not content:
                        print(f"No se pudo descargar certificado: {cert_titulo}")
                        continue
                    
                    # Leer el PDF descargado
                    try:
                        cert_buffer = BytesIO(content)
                        cert_buffer.seek(0)
                        cert_reader = PdfReader(cert_buffer)
                        
                        # Agregar todas las páginas del certificado
                        for page_num in range(len(cert_reader.pages)):
                            writer.add_page(cert_reader.pages[page_num])
                        
                        print(f"Certificado incrustado: {cert_titulo}")
                    
                    except Exception as e:
                        print(f"Error leyendo PDF de certificado: {e}")
                        continue
                
                except Exception as e:
                    print(f"Error procesando certificado {cert_titulo}: {e}")
                    continue
            
            # Crear un nuevo buffer con el PDF combinado
            output_buffer = BytesIO()
            writer.write(output_buffer)
            
            return output_buffer
        
        except Exception as e:
            print(f"Error incrustando certificados: {e}")
            return pdf_principal_buffer
