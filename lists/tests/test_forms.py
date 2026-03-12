from django.test import TestCase
from lists.forms import ItemForm, ExistingListItemForm
from lists.models import Item, List


class ItemFormTest(TestCase):
    """测试ItemForm表单"""

    def test_form_renders_item_text_input(self):
        """测试表单渲染item_text输入框"""
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control form-control-lg"', form.as_p())
        self.assertIn('name="item_text"', form.as_p())

    def test_form_validation_for_blank_items(self):
        """测试表单验证空待办事项"""
        form = ItemForm(data={'item_text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['item_text'], ["This field is required."])

    def test_form_save(self):
        """测试表单保存"""
        list_ = List.objects.create()
        form = ItemForm(data={'item_text': 'A new item'})
        self.assertTrue(form.is_valid())
        new_item = form.save(for_list=list_)
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'A new item')
        self.assertEqual(new_item.list, list_)


class ExistingListItemFormTest(TestCase):
    """测试ExistingListItemForm表单"""

    def test_form_renders_item_text_input(self):
        """测试表单渲染item_text输入框"""
        form = ExistingListItemForm(for_list=List.objects.create())
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('name="item_text"', form.as_p())

    def test_form_validation_for_blank_items(self):
        """测试表单验证空待办事项"""
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'item_text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['item_text'], ["This field is required."])

    def test_form_save(self):
        """测试表单保存"""
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'item_text': 'A new item'})
        self.assertTrue(form.is_valid())
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'A new item')
        self.assertEqual(new_item.list, list_)
