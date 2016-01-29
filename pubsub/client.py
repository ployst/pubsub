from base64 import b64encode, b64decode
import json

from oauth2client.client import GoogleCredentials
from googleapiclient import discovery


NUM_RETRIES = 3
PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']


def get_names(items):
    return [i['name'] for i in items]


def build_service_client():
    credentials = GoogleCredentials.get_application_default()
    if credentials.create_scoped_required():
        credentials = credentials.create_scoped(PUBSUB_SCOPES)

    return discovery.build('pubsub', 'v1', credentials=credentials)


class PubSub(object):
    """
    A client for the Google Cloud PubSub service.

    The public API is designed to isolate us from the actual service internals
    so that we may potentially swap providers more easily.

    It is also opinionated in some ways:
     - A client can only hold one subscription per topic
     - The subscription name is set to <topic_name>.<app_name>
    """
    def __init__(self, project, app_name):
        self.project = 'projects/' + project
        self.app_name = app_name
        self.service = build_service_client()
        projects = self.service.projects()
        self.topics = projects.topics()
        self.subscriptions = projects.subscriptions()

    # Public API

    def publish(self, topic_name, messages):
        fq_topic_name = self.ensure_topic(topic_name)
        payload = {
            'messages': [
                {'data': self._encode(message)} for message in messages
            ]
        }
        self.topics.publish(
            topic=fq_topic_name, body=payload
        ).execute()

    def pull(self, topic_name, wait=False):
        fq_subscription_name = self.ensure_subscription(topic_name)
        body = {'maxMessages': 50, 'returnImmediately': not wait}
        response = self.subscriptions.pull(
            subscription=fq_subscription_name, body=body
        ).execute()
        messages = response.get('receivedMessages', [])
        for message in messages:
            message['payload'] = self._decode(message['message']['data'])
        return messages

    def acknowledge(self, topic_name, messages):
        fq_subscription_name = self._get_subscription_name(topic_name)
        for message in messages:
            ack_msg = {'ackIds': [message['ackId']]}
            self.subscriptions.acknowledge(
                subscription=fq_subscription_name, body=ack_msg
            ).execute()

    def ensure_topic(self, topic_name):
        fq_topic_name = self._fqn('topics', topic_name)
        response = self.topics.list(project=self.project).execute()
        topics = response.get('topics', [])
        if fq_topic_name not in get_names(topics):
            self.topics.create(name=fq_topic_name, body={}).execute()
        return fq_topic_name

    def delete_topic(self, topic_name):
        self.topics.delete(topic=self._fqn('topics', topic_name)).execute()

    def ensure_subscription(self, topic_name):
        fq_subscription_name = self._get_subscription_name(topic_name)
        fq_topic_name = self._fqn('topics', topic_name)

        response = self.subscriptions.list(project=self.project).execute()
        subscriptions = response.get('subscriptions', [])
        if fq_subscription_name not in get_names(subscriptions):
            self.subscriptions.create(
                name=fq_subscription_name, body={'topic': fq_topic_name}
            ).execute()
        return fq_subscription_name

    def delete_subscription(self, topic_name):
        self.subscriptions.delete(
            subscription=self._get_subscription_name(topic_name)
        ).execute()

    # Private API, or very google-specific code

    def _encode(self, message):
        message = json.dumps(message).encode('utf-8')
        return b64encode(message).decode('ascii')

    def _decode(self, message):
        message = b64decode(message.encode('ascii'))
        return json.loads(message.decode('utf-8'))

    def _fqn(self, resource_type, name):
        return '{}/{}/{}'.format(self.project, resource_type, name)

    def _get_subscription_name(self, topic_name):
        subscription_name = '{}.{}'.format(topic_name, self.app_name)
        fq_subscription_name = self._fqn('subscriptions', subscription_name)
        return fq_subscription_name

