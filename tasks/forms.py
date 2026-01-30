from django import forms
from django.core.exceptions import ValidationError
from datetime import date
from .models import (
    Task, DatosPersonales, ExperienciaLaboral, Reconocimiento,
    CursoRealizado, ProductoAcademico, ProductoLaboral, VentaGarage
)


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title','description','important']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control',
                                            'placeholder':'Write a title'}),
            'description': forms.Textarea(attrs={'class': 'form-control',
                                                 'placeholder':'Write a description'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }


# ============================
# FORMULARIOS PARA HOJA DE VIDA
# ============================

class DatosPersonalesForm(forms.ModelForm):
    """Formulario para datos personales"""
    
    class Meta:
        model = DatosPersonales
        fields = [
            'apellidos', 'nombres', 'nacionalidad', 'lugarnacimiento',
            'fechanacimiento', 'numerocedula', 'sexo', 'estadocivil',
            'licenciaconducir', 'telefonoconvencional', 'telefonofijo',
            'direcciondomiciliaria', 'direcciontrabajo', 'sitioweb',
            'descripcionperfil', 'fotoperfil', 'perfilactivo'
        ]
        widgets = {
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos',
                'required': 'required'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres',
                'required': 'required'
            }),
            'nacionalidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nacionalidad'
            }),
            'lugarnacimiento': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de Nacimiento'
            }),
            'fechanacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'numerocedula': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de Cédula (10 dígitos)',
                'required': 'required',
                'maxlength': '10',
                'pattern': '[0-9]{10}',
                'title': 'Debe ingresar exactamente 10 dígitos'
            }),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'estadocivil': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estado Civil'
            }),
            'licenciaconducir': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Licencia de Conducir'
            }),
            'telefonoconvencional': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono Convencional'
            }),
            'telefonofijo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono Fijo'
            }),
            'direcciondomiciliaria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección Domiciliaria'
            }),
            'direcciontrabajo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Dirección de Trabajo'
            }),
            'sitioweb': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sitio Web'
            }),
            'descripcionperfil': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del Perfil',
                'rows': 3
            }),
            'fotoperfil': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'perfilactivo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_fechanacimiento(self):
        """Validar que la fecha de nacimiento no sea mayor a la fecha actual"""
        fechanacimiento = self.cleaned_data.get('fechanacimiento')
        if fechanacimiento and fechanacimiento > date.today():
            raise ValidationError('La fecha de nacimiento no puede ser mayor a la fecha actual.')
        return fechanacimiento
    
    def clean_numerocedula(self):
        """Validar que el número de cédula tenga exactamente 10 dígitos"""
        numerocedula = self.cleaned_data.get('numerocedula')
        if numerocedula:
            # Eliminar espacios en blanco
            numerocedula = numerocedula.strip()
            # Validar que solo contenga dígitos
            if not numerocedula.isdigit():
                raise ValidationError('El número de cédula debe contener solo dígitos.')
            # Validar que tenga exactamente 10 dígitos
            if len(numerocedula) != 10:
                raise ValidationError('El número de cédula debe tener exactamente 10 dígitos.')
        return numerocedula


class ExperienciaLaboralForm(forms.ModelForm):
    """Formulario para experiencia laboral"""
    
    def __init__(self, *args, **kwargs):
        self.datospersonales = kwargs.pop('datospersonales', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = ExperienciaLaboral
        fields = [
            'cargodesempenado', 'nombreempresa', 'lugarempresa',
            'emailempresa', 'sitiowebempresa', 'nombrecontactoempresarial',
            'telefonocontactoempresarial', 'fechainiciogestion', 'fechafingestion',
            'descripcionfunciones', 'certificado', 'activo'
        ]
        widgets = {
            'cargodesempenado': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cargo Desempeñado',
                'required': 'required'
            }),
            'nombreempresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la Empresa',
                'required': 'required'
            }),
            'lugarempresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lugar de la Empresa'
            }),
            'emailempresa': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email de la Empresa'
            }),
            'sitiowebempresa': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sitio Web de la Empresa'
            }),
            'nombrecontactoempresarial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de Contacto'
            }),
            'telefonocontactoempresarial': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de Contacto'
            }),
            'fechainiciogestion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'fechafingestion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'descripcionfunciones': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción de Funciones',
                'rows': 3
            }),
            'certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_fechainiciogestion(self):
        """Validar que la fecha de inicio no sea mayor a la fecha actual"""
        fechainiciogestion = self.cleaned_data.get('fechainiciogestion')
        if fechainiciogestion and fechainiciogestion > date.today():
            raise ValidationError('La fecha de inicio no puede ser mayor a la fecha actual.')
        return fechainiciogestion
    
    def clean_fechafingestion(self):
        """Validar que la fecha de fin no sea mayor a la fecha actual"""
        fechafingestion = self.cleaned_data.get('fechafingestion')
        if fechafingestion and fechafingestion > date.today():
            raise ValidationError('La fecha de fin no puede ser mayor a la fecha actual.')
        return fechafingestion
    
    def clean(self):
        """Validaciones adicionales que requieren comparar múltiples campos"""
        cleaned_data = super().clean()
        fechainiciogestion = cleaned_data.get('fechainiciogestion')
        fechafingestion = cleaned_data.get('fechafingestion')
        
        # Obtener la fecha de nacimiento del usuario
        fechanacimiento = None
        if self.datospersonales and self.datospersonales.fechanacimiento:
            fechanacimiento = self.datospersonales.fechanacimiento
        elif hasattr(self, 'instance') and self.instance.pk and self.instance.datospersonales:
            fechanacimiento = self.instance.datospersonales.fechanacimiento
        
        if fechanacimiento and fechainiciogestion:
            if fechainiciogestion < fechanacimiento:
                self.add_error('fechainiciogestion', 
                             'La fecha de inicio no puede ser menor a su fecha de nacimiento.')
        
        # Validar que fecha inicio no sea mayor a fecha fin
        if fechainiciogestion and fechafingestion:
            if fechainiciogestion > fechafingestion:
                self.add_error('fechainiciogestion', 
                             'La fecha de inicio no puede ser mayor a la fecha de fin.')
                self.add_error('fechafingestion', 
                             'La fecha de fin no puede ser menor a la fecha de inicio.')
        
        return cleaned_data


class ReconocimientoForm(forms.ModelForm):
    """Formulario para reconocimientos"""
    
    class Meta:
        model = Reconocimiento
        fields = [
            'tiporeconocimiento', 'fechareconocimiento', 'descripcionreconocimiento',
            'entidadpatrocinadora', 'nombrecontactoauspicia', 'telefonocontactoauspicia',
            'certificado', 'activo'
        ]
        widgets = {
            'tiporeconocimiento': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'fechareconocimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'descripcionreconocimiento': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del Reconocimiento',
                'rows': 3
            }),
            'entidadpatrocinadora': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entidad Patrocinadora',
                'required': 'required'
            }),
            'nombrecontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Contacto'
            }),
            'telefonocontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del Contacto'
            }),
            'certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_fechareconocimiento(self):
        """Validar que la fecha de reconocimiento no sea mayor a la fecha actual"""
        fechareconocimiento = self.cleaned_data.get('fechareconocimiento')
        if fechareconocimiento and fechareconocimiento > date.today():
            raise ValidationError('La fecha de reconocimiento no puede ser mayor a la fecha actual.')
        return fechareconocimiento


class CursoRealizadoForm(forms.ModelForm):
    """Formulario para cursos realizados"""
    
    def __init__(self, *args, **kwargs):
        self.datospersonales = kwargs.pop('datospersonales', None)
        super().__init__(*args, **kwargs)
    
    class Meta:
        model = CursoRealizado
        fields = [
            'nombrecurso', 'fechainicio', 'fechafin', 'totalhoras',
            'descripcioncurso', 'entidadpatrocinadora', 'nombrecontactoauspicia',
            'telefonocontactoauspicia', 'emailempresapatrocinadora',
            'certificado', 'activo'
        ]
        widgets = {
            'nombrecurso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Curso',
                'required': 'required'
            }),
            'fechainicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'fechafin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'totalhoras': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Total de Horas'
            }),
            'descripcioncurso': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción del Curso',
                'rows': 3
            }),
            'entidadpatrocinadora': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entidad Patrocinadora',
                'required': 'required'
            }),
            'nombrecontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Contacto'
            }),
            'telefonocontactoauspicia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono del Contacto'
            }),
            'emailempresapatrocinadora': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email de la Entidad'
            }),
            'certificado': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def clean_fechainicio(self):
        """Validar que la fecha de inicio no sea mayor a la fecha actual"""
        fechainicio = self.cleaned_data.get('fechainicio')
        if fechainicio and fechainicio > date.today():
            raise ValidationError('La fecha de inicio no puede ser mayor a la fecha actual.')
        return fechainicio
    
    def clean_fechafin(self):
        """Validar que la fecha de fin no sea mayor a la fecha actual"""
        fechafin = self.cleaned_data.get('fechafin')
        if fechafin and fechafin > date.today():
            raise ValidationError('La fecha de fin no puede ser mayor a la fecha actual.')
        return fechafin
    
    def clean(self):
        """Validaciones adicionales que requieren comparar múltiples campos"""
        cleaned_data = super().clean()
        fechainicio = cleaned_data.get('fechainicio')
        fechafin = cleaned_data.get('fechafin')
        
        # Obtener la fecha de nacimiento del usuario
        fechanacimiento = None
        if self.datospersonales and self.datospersonales.fechanacimiento:
            fechanacimiento = self.datospersonales.fechanacimiento
        elif hasattr(self, 'instance') and self.instance.pk and self.instance.datospersonales:
            fechanacimiento = self.instance.datospersonales.fechanacimiento
        
        if fechanacimiento and fechainicio:
            if fechainicio < fechanacimiento:
                self.add_error('fechainicio', 
                             'La fecha de inicio no puede ser menor a su fecha de nacimiento.')
        
        # Validar que fecha inicio no sea mayor a fecha fin
        if fechainicio and fechafin:
            if fechainicio > fechafin:
                self.add_error('fechainicio', 
                             'La fecha de inicio no puede ser mayor a la fecha de fin.')
                self.add_error('fechafin', 
                             'La fecha de fin no puede ser menor a la fecha de inicio.')
        
        return cleaned_data


class ProductoAcademicoForm(forms.ModelForm):
    """Formulario para productos académicos"""
    
    class Meta:
        model = ProductoAcademico
        fields = ['nombrerecurso', 'clasificador', 'descripcion', 'activo']
        widgets = {
            'nombrerecurso': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Recurso',
                'required': 'required'
            }),
            'clasificador': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Clasificador',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class ProductoLaboralForm(forms.ModelForm):
    """Formulario para productos laborales"""
    
    class Meta:
        model = ProductoLaboral
        fields = ['nombreproducto', 'fechaproducto', 'descripcion', 'activo']
        widgets = {
            'nombreproducto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Producto',
                'required': 'required'
            }),
            'fechaproducto': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class VentaGarageForm(forms.ModelForm):
    """Formulario para ventas garage"""
    
    class Meta:
        model = VentaGarage
        fields = ['nombreproducto', 'estadoproducto', 'descripcion', 'valordelbien', 'activo']
        widgets = {
            'nombreproducto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del Producto',
                'required': 'required'
            }),
            'estadoproducto': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Descripción',
                'rows': 3
            }),
            'valordelbien': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Valor del Bien',
                'step': '0.01',
                'required': 'required'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

