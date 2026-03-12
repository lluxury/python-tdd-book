from django.test import TestCase
from django.core.exceptions import ValidationError
from lists.models import Item, List


class ItemModelTest(TestCase):
    """测试Item模型"""

    def test_saving_and_retrieving_items(self):
        """测试保存和检索待办事项"""
        list_ = List()
        list_.save()

        first_item = Item()
        first_item.text = 'The first (ever) list item'
        first_item.list = list_
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.list = list_
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) list item')
        self.assertEqual(first_saved_item.list, list_)
        self.assertEqual(second_saved_item.text, 'Item the second')
        self.assertEqual(second_saved_item.list, list_)

    def test_cannot_save_empty_list_items(self):
        """测试不能保存空的待办事项"""
        list_ = List.objects.create()
        item = Item(list=list_, text='')

        # 尝试保存空的待办事项应该失败
        with self.assertRaises(ValidationError):
            item.save()


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
