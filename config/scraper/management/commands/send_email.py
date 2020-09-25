from decouple import Csv, config
from django.core.mail import send_mail


def make_email_body(new_posts, updated_posts):
        if len(new_posts) > 0:
            new_title = 'The following new posts have been scraped:\n'
            new_posts.insert(0, new_title)

        if len(updated_posts) > 0:
            update_title = '\n\nThe following posts have been updated and scraped again:\n'
            updated_posts.insert(0, update_title)

        return '\n'.join(new_posts) + '\n'.join(updated_posts)

def send_email(email_body):
    send_mail(
        'New or updated posts scraped.',
        email_body,
        config('SENDER_EMAIL'),
        [config('RECEIVER_EMAIL')],
        fail_silently=False,
        )
