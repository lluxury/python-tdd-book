from django import forms
from lists.models import Item
from lists.constants import EMPTY_LIST_ERROR
from django.core.exceptions import ValidationError


class ItemForm(forms.ModelForm):
    """用于新清单的表单 - 使用ModelForm"""
    item_text = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a to-do item',
            'class': 'form-control form-control-lg',
            'id': 'id_new_item'
        }),
        error_messages={'required': EMPTY_LIST_ERROR}
    )

    class Meta:
        model = Item
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 将label设为空字符串
        self.fields['item_text'].label = ''
        # 隐藏原来的text字段
        self.fields.pop('text')

    def save(self, for_list):
        """保存表单并创建新的待办事项"""
        self.instance.list = for_list
        # 将item_text映射到text字段
        if hasattr(self, 'cleaned_data') and 'item_text' in self.cleaned_data:
            self.instance.text = self.cleaned_data['item_text']
        return super().save()


class ExistingListItemForm(forms.ModelForm):
    """用于已有清单的表单 - 使用ModelForm"""
    item_text = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter a to-do item',
            'class': 'form-control form-control-lg',
            'id': 'id_new_item'
        }),
        error_messages={'required': EMPTY_LIST_ERROR}
    )

    class Meta:
        model = Item
        fields = ('text',)

    def __init__(self, for_list=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.for_list = for_list
        self.fields['item_text'].label = ''
        self.fields.pop('text')

    def clean(self):
        """验证待办事项在列表中是唯一的"""
        cleaned_data = super().clean()
        if 'item_text' in cleaned_data:
            item_text = cleaned_data['item_text']
            # 检查是否已存在相同文本的待办事项
            if Item.objects.filter(list=self.for_list, text=item_text).exists():
                self.add_error(None, "You've already got this in your list")
        return cleaned_data

    def save(self):
        """保存表单并创建新的待办事项"""
        self.instance.list = self.for_list
        if hasattr(self, 'cleaned_data') and 'item_text' in self.cleaned_data:
            self.instance.text = self.cleaned_data['item_text']
        return super().save()
