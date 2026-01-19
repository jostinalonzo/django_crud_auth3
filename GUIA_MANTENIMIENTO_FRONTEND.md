# 🔧 GUÍA DE MANTENIMIENTO Y EXTENSIÓN - Frontend CV

## Descripción General

Este documento sirve como referencia para futuros cambios, mejoras y mantenimiento del frontend del sistema de hojas de vida.

---

## 📁 Estructura de Archivos

```
djangocrud/
├── settings.py                 # Configuración Django
├── urls.py                    # URLs principales
├── wsgi.py                    # WSGI config
│
tasks/
├── models.py                  # MODELOS (NO TOCAR)
├── views.py                   # VISTAS (NO TOCAR)
├── views_cv.py               # VISTAS CV (NO TOCAR)
├── forms.py                  # FORMULARIOS (NO TOCAR)
├── urls.py                   # URLS CV (NO TOCAR)
│
├── templates/
│   ├── base.html             # TEMPLATE BASE (común a toda la app)
│   │
│   ├── cv/                   # ✨ TEMPLATES DEL USUARIO (MODIFICADOS)
│   │   ├── form_datos_personales.html    # ✏️ Formulario datos personales
│   │   ├── form_generico.html            # ✏️ Formulario genérico (cursos, exp, etc)
│   │   └── mi_hoja_vida.html             # ✏️ Vista principal CV
│   │
│   ├── admin/                # ✨ TEMPLATES DEL ADMIN (MODIFICADOS)
│   │   ├── editar_hoja_vida.html         # ✏️ Editar desde admin
│   │   ├── hojas_vida.html               # ✏️ Lista de hojas de vida
│   │   └── ver_hoja_vida.html            # ✏️ Ver hoja de vida desde admin
│   │
│   ├── otras vistas...       # No modificadas
```

---

## 🎨 Estructura CSS

### Colores Principales

```css
/* USUARIO - Gradiente Púrpura */
--primary-color: #667eea;
--primary-dark: #764ba2;
gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* ADMIN - Gradiente Rojo */
--admin-color: #e74c3c;
--admin-dark: #c0392b;
gradient: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);

/* NEUTROS */
--bg-light: #f8f9fa;
--border-color: #e9ecef;
--text-dark: #212529;
--text-muted: #6c757d;
--white-50: rgba(255, 255, 255, 0.7);
```

### Clases Reutilizables

```html
<!-- Sombras -->
<div class="shadow-sm">Sombra suave</div>
<div class="shadow-lg">Sombra grande</div>

<!-- Bordes -->
<div class="rounded-4">Border radius 1rem</div>
<div class="rounded-3">Border radius 0.75rem</div>

<!-- Tipografía -->
<h3 class="fw-bold">Negrita</h3>
<h5 class="fw-600">Semi-negrita</h5>
<p class="text-muted">Texto gris</p>

<!-- Espaciado -->
<div class="mb-4">Margen inferior 1.5rem</div>
<div class="p-5">Padding 3rem</div>

<!-- Flexbox -->
<div class="d-flex justify-content-between align-items-center">
    Contenedor flex
</div>

<!-- Grid -->
<div class="row g-4">
    <div class="col-lg-3">1/3 en lg</div>
    <div class="col-lg-9">2/3 en lg</div>
</div>
```

---

## 🔨 Cómo Modificar Elementos

### 1. Cambiar Colores (Usuario)

En `form_datos_personales.html` y `mi_hoja_vida.html`:

```html
<!-- ANTES: Púrpura -->
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">

<!-- DESPUÉS: Azul (ejemplo) -->
<div style="background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);">
```

También actualizar en los estilos:
```css
.btn-primary {
    background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
}

.btn-primary:focus {
    box-shadow: 0 0 0 0.2rem rgba(52, 152, 219, 0.15);
}
```

### 2. Cambiar Colores (Admin)

En `hojas_vida.html`, `ver_hoja_vida.html`, `editar_hoja_vida.html`:

```html
<!-- ANTES: Rojo -->
<div style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">

<!-- DESPUÉS: Naranja (ejemplo) -->
<div style="background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);">
```

### 3. Agregar Nueva Sección en mi_hoja_vida.html

```html
<!-- Copiar esta estructura -->
<div class="card shadow-sm border-0 rounded-4 mb-4">
    <div class="card-header bg-white border-0 pt-4 pb-0">
        <div class="d-flex justify-content-between align-items-center">
            <h5 class="fw-bold text-dark mb-0">
                <i class="bi bi-ICONO-AQUI me-2" style="color: #667eea;"></i>SECCIÓN NUEVA
            </h5>
            <a href="{% url 'crear_algo' %}" class="btn btn-sm btn-outline-primary rounded-3">
                <i class="bi bi-plus"></i> Agregar
            </a>
        </div>
    </div>
    <div class="card-body">
        <!-- Contenido aquí -->
    </div>
</div>
```

### 4. Personalizar Formulario Genérico

En `form_generico.html`, para agregar campos especiales:

```html
<!-- Antes del {% for field in form %} -->
{% for field in form %}
    {% if field.field.widget.input_type == 'checkbox' %}
        <!-- Especial para checkboxes -->
    {% elif field.field.widget.input_type == 'hidden' %}
        <!-- Ignorar hidden fields -->
    {% else %}
        <!-- Campos normales -->
    {% endif %}
{% endfor %}
```

### 5. Cambiar Iconos

Todos los iconos usan Bootstrap Icons. Referencia: https://icons.getbootstrap.com/

```html
<!-- Ejemplos de iconos -->
<i class="bi bi-person-fill"></i>                    <!-- Persona -->
<i class="bi bi-briefcase-fill"></i>                <!-- Maletín (trabajo) -->
<i class="bi bi-mortarboard-fill"></i>              <!-- Sombrero académico -->
<i class="bi bi-award-fill"></i>                    <!-- Trofeo (reconocimiento) -->
<i class="bi bi-files-alt"></i>                     <!-- Documentos -->
<i class="bi bi-bag-check-fill"></i>                <!-- Bolsa (productos) -->
<i class="bi bi-shop"></i>                          <!-- Tienda (ventas) -->
<i class="bi bi-calendar-event"></i>                <!-- Calendario -->
<i class="bi bi-telephone"></i>                     <!-- Teléfono -->
<i class="bi bi-envelope"></i>                      <!-- Email -->
<i class="bi bi-globe"></i>                         <!-- Globe/web -->
<i class="bi bi-pencil"></i>                        <!-- Editar -->
<i class="bi bi-trash"></i>                         <!-- Eliminar -->
<i class="bi bi-eye"></i>                           <!-- Ver -->
<i class="bi bi-download"></i>                      <!-- Descargar -->
<i class="bi bi-plus"></i>                          <!-- Agregar -->
<i class="bi bi-check-circle"></i>                  <!-- Completado -->
<i class="bi bi-x-circle"></i>                      <!-- Cancelar -->
```

---

## 📱 Media Queries (Responsividad)

Mantener en todos los templates:

```html
<!-- Bootstrap toma esto automáticamente -->
<!-- col-lg-3, col-lg-9 = 2 columnas en desktop -->
<!-- col-md-6 = 2 columnas en tablet -->
<!-- sin clase = 1 columna en móvil -->

<!-- Sticky top -->
<div class="sticky-top" style="top: 20px;">
    <!-- En móvil se iguala a static -->
</div>

<!-- Estilos media query adicionales -->
<style>
@media (max-width: 991px) {
    .sticky-top {
        position: static;
    }
}
</style>
```

---

## 🧪 Testing y Validación

### Antes de Deploy

1. **Chrome/Edge** - Principal
   ```
   - Desktop: F12, vista normal
   - Móvil: F12, Device Emulation
   ```

2. **Firefox** - Compatibilidad
   ```
   - Verificar colores
   - Verificar animaciones
   ```

3. **Safari** - Compatibilidad
   ```
   - Especialmente en móvil
   ```

### Checklist

- ✅ Gradientes se ven correctos
- ✅ Botones funcionan al hover
- ✅ Fotos se cargan y previsan
- ✅ Timeline está alineado
- ✅ Responsive en móvil/tablet/desktop
- ✅ Formularios validan
- ✅ PDF descarga correctamente
- ✅ Admin panel funciona

---

## 🚀 Optimizaciones Posibles

### 1. Agregar Transiciones de Página
```html
<style>
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.page-content {
    animation: fadeIn 0.3s ease;
}
</style>
```

### 2. Mejorar Tema Oscuro (Dark Mode)
```html
<!-- En base.html agregar toggle -->
<button id="darkModeToggle">🌙</button>

<style>
:root {
    --bg-primary: #ffffff;
    --text-primary: #212529;
}

body.dark-mode {
    --bg-primary: #1a1a1a;
    --text-primary: #f8f9fa;
}
</style>
```

### 3. Exportar a Word/Excel (además de PDF)
```python
# En views_cv.py
from docx import Document
from openpyxl import Workbook

def exportar_cv_word(request):
    doc = Document()
    # Agregar contenido del CV
    return FileResponse(open('cv.docx', 'rb'))
```

### 4. Agregar Búsqueda en Admin
```html
<div class="mb-4">
    <input type="text" class="form-control" placeholder="Buscar hojas de vida...">
</div>
```

### 5. Agregar Filtros en Admin
```html
<div class="mb-4">
    <select class="form-select">
        <option>Todos</option>
        <option>Activos</option>
        <option>Inactivos</option>
    </select>
</div>
```

---

## 🐛 Problemas Comunes y Soluciones

### Problema: Las fotos no se cargan
**Solución**: Verificar `MEDIA_ROOT` y `MEDIA_URL` en settings.py

### Problema: Gradientes no se ven en PDF
**Solución**: Los gradientes en HTML no aparecen en PDF. Usar colores sólidos en views_pdf.py

### Problema: Responsive no funciona
**Solución**: Verificar que en base.html esté el viewport meta:
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### Problema: Iconos no aparecen
**Solución**: Verificar que Bootstrap Icons CSS esté en base.html:
```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
```

---

## 📝 Guía de Cambios Futuros

### Cambio Simple: Color de Botones
1. Ir al template específico
2. Cambiar `btn-primary` a `btn-success` (u otro)
3. Actualizar estilos CSS si es necesario
4. Probar en navegador

### Cambio Medio: Agregar Nueva Sección
1. Copiar estructura de section existente
2. Cambiar nombres y icono
3. Ajustar datos mostrados
4. Probar responsividad

### Cambio Complejo: Nuevo Layout
1. Crear sketch del nuevo layout
2. Actualizar HTML estructura
3. Adaptar CSS para grid/flexbox
4. Probar en todos los tamaños
5. Testing en navegadores
6. Verificar en PDF

---

## 📚 Referencias

- Bootstrap 5: https://getbootstrap.com/docs/5.3/
- Bootstrap Icons: https://icons.getbootstrap.com/
- CSS Grid: https://developer.mozilla.org/es/docs/Web/CSS/CSS_Grid_Layout
- Flexbox: https://developer.mozilla.org/es/docs/Web/CSS/CSS_Flexible_Box_Layout

---

## 📞 Notas Importantes

⚠️ **NO MODIFICAR**:
- models.py
- views.py
- views_cv.py
- forms.py
- urls.py (en tasks/)
- manage.py

✅ **SEGURO MODIFICAR**:
- Templates HTML (en tasks/templates/)
- CSS inline
- Iconos
- Colores
- Layout
- Textos y etiquetas

---

## 📋 Checklist para Nuevo Developer

- ✅ Entender estructura de templates
- ✅ Familiarizarse con Bootstrap 5
- ✅ Conocer colores base (púrpura y rojo)
- ✅ Entender sistema de grid
- ✅ Probar cambios en múltiples navegadores
- ✅ Revisar responsividad
- ✅ Documentar cualquier cambio importante
- ✅ No romper funcionalidad existente

---

## 🎓 Conclusión

Los templates están diseñados para ser:
- **Mantenibles**: Estructura clara y documentada
- **Escalables**: Fácil agregar nuevas secciones
- **Consistentes**: Mismo lenguaje visual en toda la app
- **Responsive**: Funcionan en cualquier dispositivo
- **Bonitos**: Diseño moderno y profesional

**¡A disfrutar del nuevo frontend! 🚀**
