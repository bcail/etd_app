# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.test import SimpleTestCase


class TestStaticViews(SimpleTestCase):

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, u'<title>Electronic Theses & Dissertations at Brown University')
        self.assertContains(response, u'Ph.D. candidates at Brown must file their dissertations electronically.')
