from base64 import b64decode
from unittest import TestCase

from pubsub.client import PubSub


class TestPubSubClientForGoogle(TestCase):

    def setUp(self):
        self.pubsub = PubSub('ployst-proto', 'integration-tests')

    def test_publish_pull_and_acknowledge(self):
        topic = 'tests.publish_and_pull'
        message = 'I will be sent'.encode('utf-8')

        self.pubsub.publish(topic, [message])
        pulled_messages = self.pubsub.pull(topic)

        data = pulled_messages[0]['message']['data']
        try:
            self.assertEqual(b64decode(data), message)
            self.assertEqual(len(pulled_messages), 1)
        finally:
            self.pubsub.acknowledge(topic, pulled_messages)

    def test_pull_doesnt_wait_if_no_messages(self):
        topic = 'tests.publish_and_pull'

        pulled_messages = self.pubsub.pull(topic)

        self.assertEqual(pulled_messages, [])
