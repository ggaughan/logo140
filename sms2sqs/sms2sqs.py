import ConfigParser
import cgi
import simplejson as json
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import boto

config = ConfigParser.ConfigParser()
config.read('boto.cfg')

QUEUE_ID = config.get('SQS', 'queue_id')
ACCESS_KEY = config.get('Credentials', 'aws_access_key_id')
SECRET_KEY = config.get('Credentials', 'aws_secret_access_key')

config = boto.config
config.add_section('Credentials')
config.set('Credentials', 'aws_access_key_id', ACCESS_KEY)
config.set('Credentials', 'aws_secret_access_key', SECRET_KEY)

class Sms2Sqs(webapp.RequestHandler):
    '''Push SMS to Amazon's SQS.'''

    def get(self):
        qs = self.request.query_string

        if qs:
            sqs = boto.connect_sqs()
            q = sqs.get_queue(QUEUE_ID)
            message = q.new_message(json.dumps(cgi.parse_qs(qs)))
            q.write(message)

        return None

application = webapp.WSGIApplication(
                [('/', Sms2Sqs),],
                debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
