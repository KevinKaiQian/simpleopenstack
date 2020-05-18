'''
Created on 2014-11-1

@author: http://www.cnblogs.com/persevere/p/3611958.html
'''
import os  
import webob  
from webob import Request  
from webob import Response  
from paste.deploy import loadapp  
from wsgiref.simple_server import make_server 
import pika
import json
import sys



def msg_transfer(message):

    connection = pika.BlockingConnection(pika.ConnectionParameters(
                                host='127.0.0.1'))
    channel = connection.channel()

    channel.queue_declare(queue="task_queue", durable=True)

    channel.basic_publish(exchange='',
                          routing_key="task_queue",
                          body=message,
                          properties=pika.BasicProperties(
                           delivery_mode = 2, # make message persistent
                         ))


    connection.close()



def send_a_file(f):
    credentials = pika.PlainCredentials('test', 'test')
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            '127.0.0.1',5672,'/',credentials ))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)


    channel.basic_publish(exchange='',
                              routing_key='task_queue',
                              body=f,
                              properties=pika.BasicProperties(
                                 delivery_mode = 2, # make message persistent
                              ))
    
    connection.close()
    


class ShowVersion(object):
      '''
      app
      '''
      def __init__(self, version):
          self.version = version
      def __call__(self, environ, start_response):
          res = Response()
          res.status = '200 OK'
          res.content_type = "text/plain"
          content = []
          content.append("%s\n" % self.version)
          res.body = '\n'.join(content)
          return res(environ, start_response)
      @classmethod
      def factory(cls, global_conf, **kwargs):
          print 'factory'
          print "kwargs:", kwargs
          return ShowVersion(kwargs['version'])
      
class LogFilter(object):
      '''
      Log
      '''
      def __init__(self, app):
          self.app = app
          
      def __call__(self, environ, start_response):
          print "you can write log."
          return self.app(environ, start_response)
      @classmethod
      def factory(cls, global_conf, **kwargs):
          return LogFilter
 
class Sayhi(object):  
    '''
    '''
    def __init__(self, words):
        self.words = words
        
    def __call__(self, environ, start_response):   
        message = {'action':'deploy','params':'cloud platform'}
        send_a_file(json.dumps(message))
        #print message
        res = Response()
        res.status = '200 OK'
        res.content_type = "text/plain"
        content = []
        content.append("%s\n" % self.words)
        res.body = '\n'.join(content)
        return res(environ, start_response)


    @classmethod
    def factory(cls, global_conf, **kwargs):
        print kwargs
        return Sayhi(kwargs["words"])
        
if __name__ == '__main__':
    

    #message = {'action':'deploy','params':'cloud platform'}
    #send_a_file(json.dumps(message))
    #sys.exit(0)
    config = "python_paste.ini"
    appname = "common"
    wsgi_app = loadapp("config:%s" % os.path.abspath(config), appname)
    server = make_server('0.0.0.0', 8090, wsgi_app)
    server.serve_forever()
#http://192.168.1.3:8090/v1/test