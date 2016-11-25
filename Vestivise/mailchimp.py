from keys import mailchimp_api_key, mailchimp_list_id, mailchimp_referal_id, mandrill_api_key, mailchimp_sales_id
import requests
import json
import mandrill
from mailchimpStyles import holdingProcessing
import logging
from django.core.mail import send_mail
from settings import EMAIL_HOST_USER, ADMINS, DEBUG

mandrill_client = mandrill.Mandrill(mandrill_api_key)
MAILCHIMP_URL = "https://us13.api.mailchimp.com/3.0/"
SUBSCRIBE_LIST = MAILCHIMP_URL + "lists/" + mailchimp_list_id + "/members"
SALES_LIST = MAILCHIMP_URL + "lists/" + mailchimp_sales_id + "/members"


def subscribeToMailChimp(firstName, lastName, email, should_not_send=DEBUG):
    if should_not_send: return {"failure" : "In debug mode: skipping"}

    data = {
        "status": "pending",
        "email_address": email,
        "merge_fields": {
            "FNAME": firstName,
            "LNAME": lastName
        }
    }
    headers = {
        'Authorization': 'apikey ' + mailchimp_api_key
    }
    r = requests.post(SUBSCRIBE_LIST, data=json.dumps(data), headers=headers)
    return r.json()


def subscribeToSalesLead(fullName, company, email, should_not_send=DEBUG):
    if should_not_send: return {"failure": "In debug mode: skipping"}

    data = {
        "status": "pending",
        "email_address": email,
        "merge_fields": {
            "FNAME": fullName,
            "COMP": company
        }
    }
    headers = {
        'Authorization': 'apikey ' + mailchimp_api_key
    }
    r = requests.post(SALES_LIST, data=json.dumps(data), headers=headers)
    return r.json()


def sendProcessingHoldingNotification(email, should_not_send=DEBUG):

    if should_not_send: return

    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': 'Our Number Monkeys Are Processing Your Holdings',
            'merge_language' : 'mailchimp',
            'html' : holdingProcessing.style   
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


def sendHoldingProcessingCompleteNotification(email, should_not_send=DEBUG):

    if should_not_send: return
    
    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': 'Your Dashboard Is Ready!',
            'merge_language' : 'mailchimp',
            'html' : holdingProcessing.style,
            "merge": True
        }

        result = mandrill_client.messages.send_template(
            template_name='Dashboard Ready',
            message=message, 
            async=False, 
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)

def sendMagicLinkNotification(email, magic_link, should_not_send=DEBUG):

    if should_not_send: return


    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': "You've Been Invited To Vestivise!",
            "merge_vars":[
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


def alertIdentifyHoldings(holding_name, should_not_send=DEBUG):
    if should_not_send: return

    send_mail(
        'Missing Holding',
        holding_name,
        EMAIL_HOST_USER,
        ADMINS,
        fail_silently=False,
    )
