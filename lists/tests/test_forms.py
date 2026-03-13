from django.test import TestCase
from lists.forms import ItemForm, ExistingListItemForm
from lists.models import Item, List
from lists.constants import EMPTY_LIST_ERROR


class ItemFormTest(TestCase):
    """测试ItemForm表单"""

    def test_form_item_text_input_has_placeholder_and_css(self):
        """测试表单item_text输入框有placeholder和CSS类"""
        form = ItemForm()
        # 通过TDD探索发现：form.as_p() 输出包含 label, input with id_new_item
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control form-control-lg"', form.as_p())
        self.assertIn('name="item_text"', form.as_p())
        self.assertIn('id="id_new_item"', form.as_p())  # 探索发现的实际ID

    def test_form_validation_for_blank_items_applies_model_rules(self):
        """测试表单验证应用了模型中定义的验证规则"""
        # TextField(blank=False) 会在ModelForm中自动验证
        form = ItemForm(data={'item_text': ''})
        self.assertFalse(form.is_valid())
        # ModelForm应该应用模型验证
        self.assertIn('item_text', form.errors)

    def test_form_validation_for_blank_items(self):
        """测试表单验证空待办事项"""
        form = ItemForm(data={'item_text': ''})
        self.assertFalse(form.is_valid())
        # 使用常量来验证错误消息
        self.assertEqual(form.errors['item_text'], [EMPTY_LIST_ERROR])

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
        # 使用常量来验证错误消息
        self.assertEqual(form.errors['item_text'], [EMPTY_LIST_ERROR])

    def test_form_save(self):
        """测试表单保存"""
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'item_text': 'A new item'})
        self.assertTrue(form.is_valid())
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'A new item')
        self.assertEqual(new_item.list, list_)

    def test_form_validation_for_duplicate_items(self):
        """测试表单验证重复待办事项"""
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='duplicate')

        form = ExistingListItemForm(for_list=list_, data={'item_text': 'duplicate'})
        self.assertFalse(form.is_valid())
        # 验证应该包含重复错误
        self.assertIn('__all__', form.errors)  # Non-field errors
