# pubsub

A client library for a publish-subscribe service.
- It exposes a simplified API to clients that suits ployst conventions.
- Serves as an anticorruption layer to isolate us from the chosen provider.

Current implementation supports Google Cloud PubSub.

`pubsub` automatically handles the creation of topics and subscriptions,
as well as making sure subscription names do not clash, based on the
`app_name` provided when instantiating `PubSub`.

Messages may be anything that is JSON-serializable (can be fed to
`json.dumps`). `pubsub` will take care of encoding and decoding messages in a
format compatible with the service used.

## Example usage

```python
    from pubsub.client import PubSub
    project = 'ployst-proto'
    app_name = 'integration-tests'
    pubsub = PubSub(project, app_name)

    topic = 'tests.onetwothree'
    payload = 'I will be sent'

    # publish
    pubsub.publish(topic, [payload])

    # pull and acknowledge messages
    pulled_messages = self.pubsub.pull(topic)
    payload = pulled_messages[0]['payload']
    pubsub.acknowledge(topic, pulled_messages)
```

Unacknowledged messages will not be deleted, and may be retrieved at a later
point (although not necessarily in the original sequence).

> For more examples, look at the included tests.
