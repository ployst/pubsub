# -*- coding: utf-8 -*-
from random import randint, seed
from unittest import TestCase
from unittest.mock import patch

from pubsub.client import PubSub


class TestPubSubClientForGoogle(TestCase):

    @classmethod
    def setUpClass(cls):
        seed()
        cls.app_name = 'integration-tests-{}'.format(randint(0, 10**6))
        cls.topic = 'tests.publish_and_pull-{}'.format(randint(0, 10**6))
        cls.pubsub = PubSub('ployst-proto', cls.app_name)
        cls.pubsub.ensure_topic(cls.topic)
        cls.pubsub.ensure_subscription(cls.topic)

    @classmethod
    def tearDownClass(cls):
        cls.pubsub.delete_topic(cls.topic)
        cls.pubsub.delete_subscription(cls.topic)

    def test_publish_pull_and_acknowledge(self):
        message = {'content': 'I will be sent'}

        self.pubsub.publish(self.topic, [message])
        pulled_messages = self.pubsub.pull(self.topic, wait=True)

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

    def test_known_topics_are_not_retrieved(self):
        with patch.object(self.pubsub.topics, 'list') as list_topics:
            self.pubsub.ensure_topic(self.topic)
            self.assertEquals(list_topics.call_count, 0)

    def test_known_subscriptions_are_not_retrieved(self):
        with patch.object(self.pubsub.subscriptions, 'list') as list_subs:
            self.pubsub.ensure_subscription(self.topic)
            self.assertEquals(list_subs.call_count, 0)
