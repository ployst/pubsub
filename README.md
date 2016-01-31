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


> *WARNING*: under
> [`Delivery contract`](https://cloud.google.com/pubsub/subscriber),
> Google PubSub documentation states:
>
> For the most part Pub/Sub delivers each message once, and in the order in
> which it was published. However, once-only and in-order delivery are not
> guaranteed: it may happen that a message is delivered more than once, and out
> of order. Therefore, your subscriber should be idempotent when processing
> messages, and, if necessary, able to handle messages received out of order. If
> ordering is important, we recommend that the publisher of the topic to which
> you subscribe include some kind of sequence information in the message.


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

    # or acknowledge individual messages:
    for message in pulled_messages:
        do_stuff(message)
        message.ack()
```

Unacknowledged messages will not be deleted, and may be retrieved at a later
point (although not necessarily in the original sequence).

> For more examples, look at the included tests.
