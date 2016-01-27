from oauth2client.client import GoogleCredentials
from googleapiclient import discovery


PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']


def fqn(project, resource_type, name):
    return 'projects/{}/{}/{}'.format(project, resource_type, name)


def get_names(items):
    return [i['name'] for i in items]


def build_service_client():
    credentials = GoogleCredentials.get_application_default()
    if credentials.create_scoped_required():
        credentials = credentials.create_scoped(PUBSUB_SCOPES)

    return discovery.build('pubsub', 'v1', credentials=credentials)
