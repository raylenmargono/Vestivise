from keys import mailchimp_api_key, mailchimp_list_id, mailchimp_referal_id, mandrill_api_key, mailchimp_sales_id
import requests
import json
import mandrill
from mailchimpStyles import holdingProcessing
import logging
from django.core.mail import send_mail

mandrill_client = mandrill.Mandrill(mandrill_api_key)
MAILCHIMP_URL = "https://us13.api.mailchimp.com/3.0/"
SUBSCRIBE_LIST = MAILCHIMP_URL + "lists/" + mailchimp_list_id + "/members"
SALES_LIST = MAILCHIMP_URL + "lists/" + mailchimp_sales_id + "/members"


def subscribeToMailChimp(firstName, lastName, email):
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


def subscribeToSalesLead(fullName, company, email):
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


def sendProcessingHoldingNotification(email):

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


def sendHoldingProcessingCompleteNotification(email):
    
    try:
        message = {
            'from_email': 'hello@vestivise.com',
            'from_name': 'Vestivise',
            'to': [{'email': email}],
            'subject': 'Your Dashboard Is Ready!',
            'merge_language' : 'mailchimp',
            'html' : holdingProcessing.style   
        }

        result = mandrill_client.messages.send_template(
            template_name='Report Ready', 
            message=message, 
            async=False, 
            ip_pool='Main Pool',
            template_content=None
        )
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        logger = logging.getLogger('vestivise_exception')
        logger.exception(e.message, exc_info=True)


def alertIdentifyHoldings(holding_name):
    send_mail(
        'Missing Holding',
        holding_name,
        'danger@vestivise.com',
        ['raylen@vestivise.com', 'alex@vestivise.com', 'josh@vestivise.com'],
        fail_silently=False,
    )
