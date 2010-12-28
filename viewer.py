# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './')

import os
import custom_filter
from google.appengine.api import users
from google.appengine.ext.webapp import template

# Django template custom_filter library
template.register_template_library('custom_filter')

# Baseとなる値をセットして Viewer します
CONTENT_TYPE = 'text/html; charset=utf-8'
DEFAULT_URL = '/app/'
class Viewer:
  def generate(self, response, template_path, template_parameter):
    path = os.path.join( os.path.dirname(__file__), template_path )

    # ログイン済み情報を設定する
    if users.get_current_user():
      template_parameter['user_id'] = users.get_current_user().user_id()
      template_parameter['nickname'] = users.get_current_user().nickname()
      template_parameter['logout_url'] = users.create_logout_url(DEFAULT_URL)

    response.headers['Content-Type'] = CONTENT_TYPE
    response.out.write( template.render(path, template_parameter) )
