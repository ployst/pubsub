# -*- coding: utf-8 -*-
from unittest import TestCase

from pubsub.client import PubSub


class TestPubSubClientForGoogle(TestCase):

    def setUp(self):
        self.pubsub = PubSub('ployst-proto', 'integration-tests')
        self.topic = 'tests.publish_and_pull'

    def test_publish_pull_and_acknowledge(self):
        message = {'content': 'I will be sent'}

        self.pubsub.publish(self.topic, [message])
        pulled_messages = self.pubsub.pull(self.topic)

        payload = pulled_messages[0]['payload']
        try:
            self.assertEqual(payload, message)
            self.assertEqual(len(pulled_messages), 1)
        finally:
            self.pubsub.acknowledge(self.topic, pulled_messages)

    def test_pull_doesnt_wait_if_no_messages(self):
        pulled_messages = self.pubsub.pull(self.topic)

        self.assertEqual(pulled_messages, [])

    def test_encoded_messages_are_decoded_correctly(self):
        def encode_decode(message):
            return self.pubsub._decode(self.pubsub._encode(message))

        for message in ['hello', 'Barrobés', 12, {'too': True}]:
            self.assertEqual(message, encode_decode(message))
