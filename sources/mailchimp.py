import requests
import json
import logging

from django.core.mail import send_mail
import mandrill

from Vestivise.config import allowed_hosts
from Vestivise.settings import EMAIL_HOST_USER, DEBUG, OPERATIONS
from Vestivise.keys import (mailchimp_api_key, mailchimp_list_id, mandrill_api_key, mailchimp_sales_id, github_password,
                            github_username)
from mailchimp_styles import holding_processing


mandrill_client = mandrill.Mandrill(mandrill_api_key)
MAILCHIMP_URL = "https://us13.api.mailchimp.com/3.0/"
SUBSCRIBE_LIST = MAILCHIMP_URL + "lists/" + mailchimp_list_id + "/members"
SALES_LIST = MAILCHIMP_URL + "lists/" + mailchimp_sales_id + "/members"


def subscribe_to_mailchimp(email, should_not_send=DEBUG):
    if should_not_send:
        return {"info" : "In debug mode: skipping"}

    data = {
        "status": "pending",
        "email_address": email,
        "merge_fields": {
        }
    }
    headers = {
        'Authorization': 'apikey ' + mailchimp_api_key
    }
    r = requests.post(SUBSCRIBE_LIST, data=json.dumps(data), headers=headers)
    return r.json()


def subscribe_to_sales_lead(full_name, company, email, should_not_send=DEBUG):
    if should_not_send:
        return {"info": "In debug mode: skipping"}

    data = {
        "status": "pending",
        "email_address": email,
        "merge_fields": {
            "FNAME": full_name,
            "COMP": company
        }
    }
    headers = {
        'Authorization': 'apikey ' + mailchimp_api_key
    }
    r = requests.post(SALES_LIST, data=json.dumps(data), headers=headers)
    return r.json()


def send_processing_holding_notification(email, should_not_send=DEBUG):

    if should_not_send: return

    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': 'Our Number Monkeys Are Processing Your Holdings',
            'merge_language' : 'mailchimp',
            'html' : holding_processing.style
        }

        result = mandrill_client.messages.send_template(
            template_name='Holdings Processing', 
            message=message, 
            async=False, 
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)


def send_holding_processing_complete_notification(email, should_not_send=DEBUG):

    if should_not_send: return
    
    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': 'Your Dashboard Is Updated',
            'merge_language' : 'mailchimp',
            'html' : holding_processing.style,
            "merge": True
        }

        result = mandrill_client.messages.send_template(
            template_name='Dashboard Updated',
            message=message, 
            async=False, 
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)


def send_password_reset_email(email, link, should_not_send=DEBUG):
    if should_not_send: return

    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': 'Change Your Password',
            'merge_language': 'mailchimp',
            'html': holding_processing.style,
            "merge_vars":[
                {
                    "rcpt": email,
                    "vars": [
                        {
                            "name": "MAGICLINK",
                            "content": link
                        }
                    ]
                }
            ],
            'merge_language': 'mailchimp',
            'merge' : True,
        }

        result = mandrill_client.messages.send_template(
            template_name='New Password',
            message=message,
            async=False,
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)


def send_magic_link_notification(email, magic_link, should_not_send=DEBUG):

    if should_not_send:
        return

    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': "You've Been Invited To Vestivise!",
            "merge_vars": [
                {
                    "rcpt": email,
                    "vars": [
                        {
                            "name": "MAGICLINK",
                            "content": magic_link
                        }
                    ]
                }
            ],
            'merge_language': 'mailchimp',
            'merge' : True,
        }

        result = mandrill_client.messages.send_template(
            template_name='Magic Link',
            message=message,
            async=False,
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)


def alert_identify_holdings(holding_name, should_not_send=DEBUG):

    if should_not_send: return

    repo_owner = 'Vestivise'
    repo_name = 'Vestivise'

    url = 'https://api.github.com/repos/{}/{}/issues'.format(repo_owner, repo_name)
    # Create an authenticated session to create the issue
    session = requests.Session()
    session.auth = (github_username, github_password)

    issue = {
        'title': "Missing Holding: %s - %s" % (holding_name, allowed_hosts),
        'body': "%s: alert from %s" % (holding_name, allowed_hosts),
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print 'Successfully created Issue "%s"' % "Missing Holding"
    else:
        print 'Could not create Issue "%s"' % "Missing Holding"
        print 'Response:', r.content


def alert_mislabeled_holding(holding_name, should_not_send=DEBUG):

    if should_not_send: return

    repo_owner = 'Vestivise'
    repo_name = 'Vestivise'

    url = 'https://api.github.com/repos/{}/{}/issues'.format(repo_owner, repo_name)
    # Create an authenticated session to create the issue
    session = requests.Session()
    session.auth = (github_username, github_password)

    issue = {
        'title': 'Mislabeled Holding: {} - {}'.format(holding_name, allowed_hosts),
        'body': "%s: allert from %s" % (holding_name, allowed_hosts),
    }
    # Add the issue to our repository
    r = session.post(url, json.dumps(issue))
    if r.status_code == 201:
        print 'Successfully created Issue "%s"' % "Missing Holding"
    else:
        print 'Could not create Issue "%s"' % "Missing Holding"
        print 'Response: ', r.content


def user_creation(email, should_not_send=DEBUG):
    if should_not_send:
        return

    send_mail(
        'new user',
        "%s: alert from %s" % (email, allowed_hosts),
        EMAIL_HOST_USER,
        OPERATIONS,
        fail_silently=False,
    )


def inactivity_reminder(email, should_not_send=DEBUG):

    if should_not_send:
        return

    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': "Number Monkey Alert",
            'merge_language': 'mailchimp',
            'merge' : True,
        }

        result = mandrill_client.messages.send_template(
            template_name='Dashboard View',
            message=message,
            async=False,
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)


def not_linked_account(email, should_not_send=DEBUG):

    if should_not_send: return

    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': "Number Monkey Alert",
            'merge_language': 'mailchimp',
            'merge' : True,
        }

        result = mandrill_client.messages.send_template(
            template_name='Account Link',
            message=message,
            async=False,
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)
