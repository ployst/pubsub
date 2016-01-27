import base64
from .google import build_service_client, fqn, get_names


NUM_RETRIES = 3
PROJECT = 'ployst-proto'


class PubSub(object):

    def __init__(self, project, app_name):
        self.app_name = app_name
        self.service = build_service_client()
        projects_endpoint = self.service.projects()
        self.topics_endpoint = projects_endpoint.topics()
        self.subscriptions_endpoint = projects_endpoint.subscriptions()

    def ensure_topic(self, fq_topic_name):
        response = self.topics_endpoint.list(project=PROJECT).execute()
        topics = response['topics']
        if fq_topic_name not in get_names(topics):
            self.topics_endpoint.create(name=fq_topic_name, body={}).execute()

    def publish(self, topic_name, messages):
        fq_topic_name = fqn('topics', topic_name)
        self.ensure_topic(fq_topic_name)

        payload = {
            'messages': [
                {'data': base64.b64encode(message)} for message in messages
            ]
        }
        self.topics_endpoint.publish(
            topic=fq_topic_name, body=payload
        ).execute()

    def ensure_subscription(self, topic_name):
        subscription_name = '{}.{}'.format(self.app_name, topic_name)
        fq_subscription_name = fqn('subscriptions', subscription_name)
        fq_topic_name = fqn('topics', topic_name)

        response = self.subscriptions_endpoint.list(project=PROJECT).execute()
        subscriptions = response['subscriptions']
        if fq_subscription_name not in get_names(subscriptions):
            self.subscriptions_endpoint.create(
                name=fq_subscription_name, body={'topic': fq_topic_name}
            ).execute()
        return fq_subscription_name

    def pull(self, topic_name):
        fq_subscription_name = self.ensure_subscription(topic_name)
        messages = self.subscriptions_endpoint.pull(
            subscription=fq_subscription_name,
            body={'maxMessages': 50, 'returnImmediately': False}
        ).execute()
        return fq_subscription_name, messages

    def acknowledge(self, messages, fq_subscription_name):
        for message in messages['receivedMessages']:
            ack_msg = {'ackIds': [message['ackId']]}
            self.subscriptions_endpoint.acknowledge(
                subscription=fq_subscription_name, body=ack_msg
            ).execute()
