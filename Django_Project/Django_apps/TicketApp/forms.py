from django import forms
from .models import LtlStorageRecord


class LtlStorageForm(forms.ModelForm):
    # By using ModelForm, we get free validation based on our model definition.
    # We can add custom validation here as well.

    class Meta:
        model = LtlStorageRecord
        fields = ['picking_no', 'bol_no', 'location_code', 'pallet_qty', 'note']
        widgets = {
            'picking_no': forms.TextInput(attrs={'class': 'pda-input', 'autofocus': True}),
            'bol_no': forms.TextInput(attrs={'class': 'pda-input'}),
            'location_code': forms.TextInput(attrs={'class': 'pda-input'}),
            'pallet_qty': forms.NumberInput(attrs={'class': 'pda-input'}),
            'note': forms.Textarea(attrs={'class': 'pda-input', 'rows': 3, 'style': 'font-size: 1.2rem;'}),
        }

    # def clean_picking_no(self):
    #     """
    #     Custom validation to ensure the picking_no is unique.
    #     """
    #     picking_no = self.cleaned_data.get('picking_no')
    #     if LtlStorageRecord.objects.filter(picking_no=picking_no).exists():
    #         raise forms.ValidationError(f"Picking Slip # {picking_no} already exists in the system.")
    #     return picking_no
