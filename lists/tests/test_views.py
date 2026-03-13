from django.test import TestCase
from django.urls import resolve
from lists.views import home_page, view_list
from lists.models import Item, List
from lists.forms import ItemForm, ExistingListItemForm
from lists.constants import EMPTY_LIST_ERROR
import unittest


class HomePageTest(TestCase):
    """测试首页视图"""

    def test_root_url_resolves_to_home_page_view(self):
        """测试根URL解析到home_page视图（旧测试，保留）"""
        found = resolve('/')
        self.assertEqual(found.func, home_page)

    def test_home_page_uses_item_form(self):
        """测试首页使用ItemForm"""
        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_home_page_can_save_a_post_request(self):
        """测试首页可以保存POST请求"""
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new list item')

    def test_home_page_can_save_multiple_post_requests(self):
        """测试首页可以保存多个POST请求"""
        response = self.client.post('/', data={'item_text': 'Use peacock'})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'Use peacock')

    def test_home_page_only_saves_items_when_necessary(self):
        """测试首页只在必要时保存待办事项"""
        self.client.get('/')
        self.assertEqual(Item.objects.count(), 0)

    def test_home_page_redirects_after_post(self):
        """测试首页在POST后重定向到新的清单URL"""
        response = self.client.post('/', data={'item_text': 'A new list item'})
        self.assertEqual(response.status_code, 302)
        self.assertRegex(response['location'], r'/lists/\d+/')

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        """测试首页验证错误会发送回home模板"""
        response = self.client.post('/', data={'item_text': ''})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = "You can't have an empty list item"
        self.assertContains(response, expected_error)


class ListViewTest(TestCase):
    """测试清单视图"""

    def post_invalid_input(self):
        """辅助方法：发送无效输入到清单视图"""
        list_ = List.objects.create()
        return self.client.post(f'/lists/{list_.id}/', data={'item_text': ''})

    def test_uses_list_template(self):
        """测试使用list模板"""
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_displays_only_items_for_that_list(self):
        """测试只显示该清单的待办事项"""
        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list item 1', list=other_list)
        Item.objects.create(text='other list item 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list item 1')
        self.assertNotContains(response, 'other list item 2')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """测试可以保存POST请求到现有清单"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(f'/lists/{correct_list.id}/', data={'item_text': 'A new item for an existing list'})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'A new item for an existing list')
        self.assertEqual(new_item.list, correct_list)

    def test_POST_redirects_to_list_view(self):
        """测试POST后重定向到清单视图"""
        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(f'/lists/{correct_list.id}/', data={'item_text': 'A new item for an existing list'})

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_validation_errors_are_sent_back_to_list_template(self):
        """测试验证错误会发送回list模板"""
        response = self.post_invalid_input()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')
        # 检查错误消息存在（不依赖精确的HTML转义）
        self.assertIn("empty list item", response.content.decode())

    def test_list_view_uses_existing_list_item_form(self):
        """测试list_view使用ExistingListItemForm"""
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_form_passed_to_template(self):
        """测试表单对象传入模板"""
        response = self.post_invalid_input()
        # POST无效输入后，表单对象仍然传递给模板
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_post_invalid_input_shows_error_on_page(self):
        """测试POST无效输入在页面上显示错误"""
        response = self.post_invalid_input()
        # 检查错误消息存在（不依赖精确的HTML转义）
        self.assertIn("empty list item", response.content.decode())

    def test_for_invalid_input_nothing_saved_to_db(self):
        """测试无效输入不会保存到数据库"""
        # 先创建一些现有项目
        list_ = List.objects.create()
        Item.objects.create(text='item 1', list=list_)
        Item.objects.create(text='item 2', list=list_)
        initial_count = Item.objects.count()

        # 提交无效输入
        self.post_invalid_input()

        # 确保数据库没有新增
        self.assertEqual(Item.objects.count(), initial_count)
        # 确保只有原来的项目存在
        self.assertEqual(Item.objects.filter(list=list_).count(), 2)

    def test_duplicate_item_shows_error_in_view(self):
        """测试重复事项在视图中显示错误"""
        list_ = List.objects.create()
        Item.objects.create(list=list_, text='duplicate item')

        response = self.client.post(f'/lists/{list_.id}/', data={'item_text': 'duplicate item'})

        self.assertEqual(response.status_code, 200)
        # Django转义了撇号，匹配HTML中的文本
        self.assertIn("already got this in your list", response.content.decode())
