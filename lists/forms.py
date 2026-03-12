from django import forms
from lists.models import Item


class ItemForm(forms.Form):
    """用于新清单的表单"""
    item_text = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a to-do item',
            'class': 'form-control form-control-lg',
            'id': 'id_new_item'
        })
    )

    def save(self, for_list):
        """保存表单并创建新的待办事项"""
        if hasattr(self, 'cleaned_data') and 'item_text' in self.cleaned_data:
            return Item.objects.create(
                text=self.cleaned_data['item_text'],
                list=for_list
            )
        raise ValueError("Form is not validated")


class ExistingListItemForm(forms.Form):
    """用于已有清单的表单"""
    item_text = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a to-do item',
            'class': 'form-control form-control-lg',
            'id': 'id_new_item'
        })
    )

    def __init__(self, for_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.for_list = for_list

    def save(self):
        """保存表单并创建新的待办事项"""
        if hasattr(self, 'cleaned_data') and 'item_text' in self.cleaned_data:
            return Item.objects.create(
                text=self.cleaned_data['item_text'],
                list=self.for_list
            )
        raise ValueError("Form is not validated")
