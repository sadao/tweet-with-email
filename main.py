# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './')

from google.appengine.api import urlfetch
from google.appengine.api import mail,users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
import logging
import re
import os

import urls
import models
from models import Twitter
from viewer import Viewer

# ポータルIndexページを表示するよ
TEMPLATE_PORTAL_INDEX_PATH = 'templates/portal/index.html'
class PortalIndexHandler(webapp.RequestHandler):
  def get(self):
    # 画面を表示する
    # http://morchin.sakura.ne.jp/effective_python/method.html
    Viewer.generate(Viewer(), self.response, TEMPLATE_PORTAL_INDEX_PATH, {})

# 管理画面Indexページを表示するよ
TEMPLATE_APP_INDEX_PATH = 'templates/app/index.html'
class AppIndexHandler(webapp.RequestHandler):
  def get(self):
    # 画面を表示する
    # http://morchin.sakura.ne.jp/effective_python/method.html
    Viewer.generate(
      Viewer(), 
      self.response, 
      TEMPLATE_APP_INDEX_PATH, 
      {
        'owned_twitters': models.get_owned_twitters( users.get_current_user() )
      })

# Twitter情報を登録・更新するよ
TWITTER_BASE_URL = 'http://twitter.com/'
class AppRegisterHandler(webapp.RequestHandler):
  def post(self):
    # パラメータを取得する
    twitter_id          = self.request.get("twitter_id")
    consumer_key        = self.request.get("consumer_key")
    consumer_secret     = self.request.get("consumer_secret")
    access_token        = self.request.get("access_token")
    access_token_secret = self.request.get("access_token_secret")

    # パラメータチェック
    if (twitter_id == '' or consumer_key == '' or consumer_secret == ''):
      self.redirect(urls.APP_INDEX_URL)
      return

    # データ登録 or 更新 and 取得
    twitter_obj = Twitter.get_or_insert(
                   users.get_current_user().user_id() + twitter_id,
                   owner               = users.get_current_user(),
                   twitter_id          = twitter_id,
                   consumer_key        = consumer_key,
                   consumer_secret     = consumer_secret,
                   access_token        = access_token,
                   access_token_secret = access_token_secret )
    twitter_obj.consumer_key = consumer_key
    twitter_obj.consumer_secret = consumer_secret
    twitter_obj.access_token = access_token
    twitter_obj.access_token_secret = access_token_secret
    twitter_obj.put()

    # 画面を表示する
    Viewer.generate(
      Viewer(),
      self.response,
      TEMPLATE_APP_INDEX_PATH,
      {
        'current_twitter': twitter_obj,
        'owned_twitters': models.get_owned_twitters( users.get_current_user() )
      })

# Twitter情報を削除するよ
class AppRemoveHandler(webapp.RequestHandler):
  # Twitter情報更新
  def post(self):
    # パラメータを取得する
    twitter_id      = self.request.get("twitter_id")

    # データ取得
    query = Twitter.all()
    query.filter( 'twitter_id = ', twitter_id )
    query.filter( 'owner = ', users.get_current_user() )
    twitter = query.fetch(limit = 1)

    # データがない！
    if not twitter:
      # 無言で一覧へいかせるのさ
      self.redirect(urls.APP_INDEX_URL)
      return

    # 削除
    twitter[0].delete()

    # AppIndex へリダイレクト
    self.redirect(urls.APP_INDEX_URL)

# 登録済みTwitter情報を表示するよ
class AppTwitterHandler(webapp.RequestHandler):
  # Twitter情報表示
  def get(self):
    # パラメータ取得
    twitter_id = self.request.get("id")

    # パラメータがなければ一覧へ
    if not twitter_id:
      self.redirect(urls.APP_INDEX_URL)
      return

    # データ取得
    twitter_obj = Twitter.get( twitter_id )

    # データがない！
    if not twitter_obj:
      # 無言で一覧へいかせるのさ
      self.redirect(urls.APP_INDEX_URL)
      return

    # 画面を表示する
    Viewer.generate(
      Viewer(),
      self.response,
      TEMPLATE_APP_INDEX_PATH,
      {
        'current_twitter': twitter_obj,
        'owned_twitters': models.get_owned_twitters( users.get_current_user() )
      })

# テストつぶやきをするよ
TWITTER_BASE_URL = 'http://twitter.com'
class AppTestTweetHandler(webapp.RequestHandler):
  # Twitter情報表示
  def post(self):
    # パラメータを取得する
    twitter_id          = self.request.get("twitter_id")
    consumer_key        = self.request.get("consumer_key")
    consumer_secret     = self.request.get("consumer_secret")
    access_token        = self.request.get("access_token")
    access_token_secret = self.request.get("access_token_secret")

    # パラメータチェック
    if (twitter_id == '' or consumer_key == '' or consumer_secret == ''):
      self.redirect(urls.APP_INDEX_URL)
      return

    # データ登録 or 更新 and 取得
    twitter_obj = Twitter.get_or_insert(
                   users.get_current_user().user_id() + twitter_id,
                   owner               = users.get_current_user(),
                   twitter_id          = twitter_id,
                   consumer_key        = consumer_key,
                   consumer_secret     = consumer_secret,
                   access_token        = access_token,
                   access_token_secret = access_token_secret )
    twitter_obj.consumer_key = consumer_key
    twitter_obj.consumer_secret = consumer_secret
    twitter_obj.access_token = access_token
    twitter_obj.access_token_secret = access_token_secret
    twitter_obj.put()

    # Twitterアカウント有無確認
#    result_test_tweet = ''
#    try:
#      result = urlfetch.fetch(TWITTER_BASE_URL + twitter_id)
#      if not (result.status_code == 200):
#        result_test_tweet = 'Twitterアカウントが間違っているかもしれません'
#    except urlfetch.DownloadError, e: 
#      logging.error('Download error: %s', e)
#      result_test_tweet = e

    # つぶやく
    import oauth
    client = oauth.TwitterClient(twitter_obj.consumer_key,
                                 twitter_obj.consumer_secret, None)
    try:
      client.make_request('http://twitter.com/statuses/update.json',
                          token = twitter_obj.access_token,
                          secret = twitter_obj.access_token_secret,
                          additional_params = {'status': u"test"},
                          protected = True,
                          method = 'POST')
      result_test_tweet = 'SET (SuccEss Tweet)'
    except e:
      logging.error('Tweet error: %s', e)

    # 画面を表示する
    Viewer.generate(
      Viewer(),
      self.response,
      TEMPLATE_APP_INDEX_PATH,
      {
        'current_twitter': twitter_obj,
        'owned_twitters': models.get_owned_twitters( users.get_current_user() ),
        'result_test_tweet': result_test_tweet
      })

# TEM TEM するよ♪
class AppRecentMailHandler(InboundMailHandler):
  def receive(self, message):
    # 送信元メールアドレスの @ の左側を取得する
    twitter_id = self.get_user_id( message.to )

    # twitter_id が登録済みかな？
    query = Twitter.all()
    query.filter( 'twitter_id = ', twitter_id )
    twitter_obj = query.fetch(limit = 1)

    # 未登録なら、はいここまでよ
    if not twitter_obj:
      logging.error( twitter_id + 'is not registered' )
      return

    # メール本文だけ使います。Subject はスルー
    body = self.get_body( message )
    if not body:
      logging.error( 'Nothing Mail Body' )
      return

    # TEMるのだ
    import oauth
    client = oauth.TwitterClient(twitter_obj[0].consumer_key,
                                 twitter_obj[0].consumer_secret, None)
    try:
      client.make_request('http://twitter.com/statuses/update.json',
                          token = twitter_obj[0].access_token,
                          secret = twitter_obj[0].access_token_secret,
                          additional_params = {'status': body},
#                          additional_params = {'status': u"body"},
                          protected = True,
                          method = 'POST')
      logging.info('Success Tweet : %s', twitter_id)
    except e:
      logging.error('Tweet error: %s', e)

  # あて先メールアドレスの @ の左辺を取得するよ
  # http://www40.atwiki.jp/geiinbashoku/pages/23.html#id_93404844
  def get_user_id(self, to_address):
    m = re.search(r"(\w+)@(\w+)", to_address)
    return m.group(1)

  # メール本文を取得解析するよ
  def get_body(self, message):
    bodies = message.bodies(content_type='text/plain')
    first_line_of_bodies = "";
    for body in bodies:
      first_line_of_bodies = body[1].decode()
      first_line_of_bodies = first_line_of_bodies.rstrip()
      break

    return first_line_of_bodies

# webapp フレームワークのURLマッピングです
application = webapp.WSGIApplication([
                (urls.PORTAL_INDEX_URL, PortalIndexHandler),
                (urls.APP_INDEX_URL, AppIndexHandler),
                (urls.APP_REGISTER_URL, AppRegisterHandler),
                (urls.APP_REMOVE_URL, AppRemoveHandler),
                (urls.APP_TWITTER_URL, AppTwitterHandler),
                (urls.APP_TEST_TWEET_URL, AppTestTweetHandler),
                AppRecentMailHandler.mapping(),
              ], debug=True)

# WebApp フレームワークのメインメソッドです
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
