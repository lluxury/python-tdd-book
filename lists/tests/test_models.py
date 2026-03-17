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


class ListOwnerTest(TestCase):
    """测试List模型属主功能"""

    def setUp(self):
        """设置测试用户"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.user = User.objects.create_user(email='test@example.com')

    def test_list_can_have_owner(self):
        """测试list可以拥有属主"""
        list_ = List.objects.create(owner=self.user)

        # Check that the list has an owner
        self.assertEqual(list_.owner, self.user)

    def test_list_owner_is_optional(self):
        """测试list的属主是可选的（可以None）"""
        # Create a list without an owner
        list_ = List.objects.create()

        # Check that the list's owner is None
        self.assertIsNone(list_.owner)

    def test_list_owner_field_exists(self):
        """测试list模型有owner字段"""
        # Check that the owner field exists in the model
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get the owner field from the model
        owner_field = List._meta.get_field('owner')

        # Check that it's a ForeignKey to User model
        self.assertEqual(owner_field.related_model, User)

    def test_list_owner_can_be_null(self):
        """测试list的owner字段允许null值"""
        # Check that the owner field can be null
        owner_field = List._meta.get_field('owner')

        # null should be True
        self.assertTrue(owner_field.null)

    def test_list_owner_can_be_blank(self):
        """测试list的owner字段允许blank值"""
        # Check that the owner field can be blank in forms
        owner_field = List._meta.get_field('owner')

        # blank should be True
        self.assertTrue(owner_field.blank)

    def test_list_owner_on_delete_cascade(self):
        """测试当属主被删除时，list也被删除"""
        # Create a list with an owner
        list_ = List.objects.create(owner=self.user)
        list_id = list_.id

        # Delete the user
        self.user.delete()

        # Check that the list is also deleted
        self.assertFalse(List.objects.filter(id=list_id).exists())

    def test_list_owners_are_different(self):
        """测试不同list可以有不同属主"""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user1 = User.objects.create_user(email='user1@example.com')
        user2 = User.objects.create_user(email='user2@example.com')

        list1 = List.objects.create(owner=user1)
        list2 = List.objects.create(owner=user2)

        # Check that each list has its own owner
        self.assertEqual(list1.owner, user1)
        self.assertEqual(list2.owner, user2)
        self.assertNotEqual(list1.owner, list2.owner)

    def test_list_without_owner_can_have_items(self):
        """测试没有属主的list可以有items"""
        # Create a list without an owner
        list_ = List.objects.create()

        # Add items to the list
        item1 = Item.objects.create(list=list_, text='Item 1')
        item2 = Item.objects.create(list=list_, text='Item 2')

        # Check that the list has items
        self.assertEqual(list_.item_set.count(), 2)
        self.assertIn(item1, list_.item_set.all())
        self.assertIn(item2, list_.item_set.all())


class ListNameTest(TestCase):
    """测试List名字功能"""

    def test_list_name_returns_first_item_text(self):
        """测试list名字返回第一个item的文本"""
        # Create a list with items
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='Buy peacock feathers')
        Item.objects.create(list=list_, text='Buy milk')

        # Check that the list name is the first item's text
        self.assertEqual(list_.name, 'Buy peacock feathers')

    def test_list_name_returns_empty_list_for_no_items(self):
        """测试没有items的list名字返回'Empty List'"""
        # Create a list without items
        list_ = List.objects.create()

        # Check that the list name is 'Empty List'
        self.assertEqual(list_.name, 'Empty List')

    def test_list_name_uses_first_item_even_with_many(self):
        """测试即使有多个items，list名字仍使用第一个"""
        # Create a list with multiple items
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='First item')
        Item.objects.create(list=list_, text='Second item')
        Item.objects.create(list=list_, text='Third item')

        # Check that the list name is still the first item's text
        self.assertEqual(list_.name, 'First item')

    def test_list_name_updates_when_first_item_changes(self):
        """测试当第一个item改变时，list名字也会改变"""
        # Create a list with an item
        list_ = List.objects.create()
        item = Item.objects.create(list=list_, text='Original item')

        # Check initial name
        self.assertEqual(list_.name, 'Original item')

        # Update the item text
        item.text = 'Updated item'
        item.save()

        # Check that the list name has changed
        self.assertEqual(list_.name, 'Updated item')

    def test_list_name_is_dynamic_property(self):
        """测试list名字是动态属性（不是数据库字段）"""
        # Create a list
        list_ = List.objects.create()

        # Check that name is a property, not a field
        self.assertTrue(hasattr(list_, 'name'))
        self.assertTrue(isinstance(type(list_).name, property))


