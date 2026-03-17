"""
Unit tests for list sharing views
清单分享视图的单元测试
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from lists.models import List, Item

User = get_user_model()


class ListViewSharingTest(TestCase):
    """测试清单视图的分享功能"""

    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user_a = User.objects.create_user(email='a@example.com')
        self.user_b = User.objects.create_user(email='b@example.com')

    def test_shared_user_can_view_list(self):
        """测试被分享的用户可以查看清单"""
        # 用户A创建清单并添加项目
        list_ = List.objects.create(owner=self.user_a)
        Item.objects.create(list=list_, text='Buy peacock feathers')

        # 用户A分享给用户B
        list_.shared_with.add(self.user_b)

        # 用户B访问清单（需要登录）
        self.client.force_login(self.user_b, backend='accounts.views.EmailBackend')
        response = self.client.get(f'/lists/{list_.id}/')

        # 验证响应成功
        self.assertEqual(response.status_code, 200)

        # 验证清单内容在响应中
        self.assertIn('Buy peacock feathers', response.content.decode())

    def test_shared_user_can_add_item(self):
        """测试被分享的用户可以添加项目"""
        list_ = List.objects.create(owner=self.user_a)
        Item.objects.create(list=list_, text='Buy peacock feathers')
        list_.shared_with.add(self.user_b)

        # 用户B登录并添加项目
        self.client.force_login(self.user_b, backend='accounts.views.EmailBackend')
        response = self.client.post(f'/lists/{list_.id}/', data={'item_text': 'Buy milk'})

        # 验证重定向
        self.assertEqual(response.status_code, 302)

        # 验证项目被添加
        self.assertEqual(Item.objects.filter(list=list_).count(), 2)
        self.assertTrue(Item.objects.filter(list=list_, text='Buy milk').exists())

    def test_share_list_via_post(self):
        """测试通过POST分享清单"""
        list_ = List.objects.create(owner=self.user_a)

        # 用户A登录并分享清单
        self.client.force_login(self.user_a, backend='accounts.views.EmailBackend')
        response = self.client.post(f'/lists/{list_.id}/', data={'share_email': 'b@example.com'})

        # 验证重定向
        self.assertEqual(response.status_code, 302)

        # 验证清单被分享
        list_.refresh_from_db()
        self.assertIn(self.user_b, list_.shared_with.all())
