"""
Unit tests for list sharing
清单分享的单元测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from lists.models import List, Item

User = get_user_model()


class ListSharingModelTest(TestCase):
    """测试清单分享的模型功能"""

    def test_list_can_be_shared_with_user(self):
        """测试清单可以分享给用户"""
        # 创建用户A和用户B
        user_a = User.objects.create_user(email='a@example.com')
        user_b = User.objects.create_user(email='b@example.com')

        # 用户A创建清单
        list_ = List.objects.create(owner=user_a)
        Item.objects.create(list=list_, text='Buy peacock feathers')

        # 用户A分享清单给用户B
        list_.shared_with.add(user_b)

        # 验证分享成功
        self.assertIn(user_b, list_.shared_with.all())
        self.assertEqual(list_.shared_with.count(), 1)

    def test_shared_list_appears_in_user_shared_lists(self):
        """测试分享的清单出现在用户的shared_lists中"""
        user_a = User.objects.create_user(email='a@example.com')
        user_b = User.objects.create_user(email='b@example.com')

        list_ = List.objects.create(owner=user_a)
        list_.shared_with.add(user_b)

        # 验证用户B可以看到分享的清单
        self.assertIn(list_, user_b.shared_lists.all())
        self.assertEqual(user_b.shared_lists.count(), 1)

    def test_list_can_be_shared_with_multiple_users(self):
        """测试清单可以分享给多个用户"""
        user_a = User.objects.create_user(email='a@example.com')
        user_b = User.objects.create_user(email='b@example.com')
        user_c = User.objects.create_user(email='c@example.com')

        list_ = List.objects.create(owner=user_a)
        list_.shared_with.add(user_b, user_c)

        self.assertEqual(list_.shared_with.count(), 2)
        self.assertIn(user_b, list_.shared_with.all())
        self.assertIn(user_c, list_.shared_with.all())
