from django import forms
from .models import Mascota

class DateInput(forms.DateInput):
      input_type = 'date'

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['nombre', 'especie', 'raza', 'fecha_nacimiento', 'propietario', 'telefono', 'direccion']
       
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_examen_sangre(self):
        examen = self.cleaned_data.get('examen_sangre')
        if examen:
            if examen.content_type != 'application/pdf':
                raise forms.ValidationError('El archivo debe ser un PDF.')
            if examen.size > 5*1024*1024:  # 5 MB limit
                raise forms.ValidationError('El tamaño del archivo no puede exceder 5 MB.')
        return examen
    enfermedad_predicha = forms.CharField(widget=forms.HiddenInput(), required=False)
    tratamiento_recomendado = forms.CharField(widget=forms.HiddenInput(), required=False)


 
from .models import ExamenMascota

class ExamenMascotaForm(forms.ModelForm):
    class Meta:
        model = ExamenMascota
        fields = ['titulo', 'archivo_pdf']


from django import forms
from .models import Mascota

class TratamientoForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['tratamiento']
        widgets = {
            'tratamiento': forms.Textarea(attrs={'rows': 4}),
        }