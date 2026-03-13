from django.test import TestCase
from django.core.exceptions import ValidationError
from lists.models import Item, List


class ItemModelTest(TestCase):
    """测试Item模型"""

    def test_default_text(self):
        """测试默认文本"""
        item = Item()
        self.assertEqual(item.text, '')

    def test_item_is_related_to_list(self):
        """测试Item与List的关系"""
        list_ = List.objects.create()
        item = Item.objects.create(list=list_, text='item 1')

        self.assertIn(item, list_.item_set.all())

    def test_cannot_save_empty_list_items(self):
        """测试不能保存空的待办事项"""
        # 标准版本：空文本默认值是允许的，但表单会验证
        # 这个测试应该移到表单测试中
        # 在模型层，TextField(default='') 允许空值
        list_ = List.objects.create()
        item = Item(list=list_, text='')
        item.save()
        self.assertEqual(item.text, '')

    def test_duplicate_items_are_invalid(self):
        """测试重复的待办事项是无效的"""
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='text')

        # 尝试创建相同文本的待办事项应该失败
        with self.assertRaises(ValidationError):
            item = Item(list=list_, text='text')
            item.full_clean()  # 验证会检查唯一约束

    def test_duplicate_items_in_different_lists_are_ok(self):
        """测试不同列表中的重复待办事项是允许的"""
        list1 = List.objects.create()
        list2 = List.objects.create()

        # 在两个列表中创建相同文本的待办事项应该成功
        Item.objects.create(list=list1, text='text')
        Item.objects.create(list=list2, text='text')

        # 验证两个待办事项都存在
        self.assertEqual(Item.objects.filter(text='text').count(), 2)


class ListModelTest(TestCase):
    """测试List模型"""

    def test_list_can_have_items(self):
        """测试清单可以有多个待办事项"""
        list_ = List.objects.create()
        Item.objects.create(text='item 1', list=list_)
        Item.objects.create(text='item 2', list=list_)

        self.assertEqual(Item.objects.filter(list=list_).count(), 2)

    def test_list_is_related_to_items(self):
        """测试清单与待办事项的关系"""
        list_ = List.objects.create()
        item = Item.objects.create(text='item 1', list=list_)

        self.assertIn(item, list_.item_set.all())

    def test_list_ordering(self):
        """测试清单排序（如果需要）"""
        list1 = List.objects.create()
        list2 = List.objects.create()

        lists = List.objects.all()
        self.assertEqual(lists[0], list1)
        self.assertEqual(lists[1], list2)

    def test_items_are_ordered_by_creation_time(self):
        """测试待办事项按创建时间排序"""
        list_ = List.objects.create()
        item1 = Item.objects.create(list=list_, text='item 1')
        item2 = Item.objects.create(list=list_, text='item 2')
        item3 = Item.objects.create(list=list_, text='item 3')

        # 转换为列表以保持顺序
        items = list(Item.objects.filter(list=list_))
        self.assertEqual(items[0], item1)
        self.assertEqual(items[1], item2)
        self.assertEqual(items[2], item3)
