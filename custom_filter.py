from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
register = webapp.template.create_template_register()

def getOddEven(_val):
  if _val % 2==0:
    return 'even'
  else:
    return 'odd'

def isOdd(_val):
  if _val % 2==0:
    return True
  else:
    return False

def isEven(_val):
  if _val % 2==0:
    return False
  else:
    return True

register.filter(getOddEven)
register.filter(isOdd)
register.filter(isEven)
