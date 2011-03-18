# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users

# Twitterモデル
class Twitter(db.Model):
  owner = db.UserProperty(required=True)
  mailaddress = db.StringProperty()
  twitter_id = db.StringProperty()
  consumer_key = db.StringProperty()
  consumer_secret = db.StringProperty()
  access_token = db.StringProperty()
  access_token_secret = db.StringProperty()
  created_on = db.DateTimeProperty(auto_now_add=True)
  modified_on = db.DateTimeProperty(auto_now_add=True)

# 所有する情報を全て(100件)取得する
def get_owned_twitters(user):
  query = Twitter.all()
  query.filter( 'owner = ', user )
  query.order('-created_on')
  owned_twitters = query.fetch(limit = 100)

  return owned_twitters
