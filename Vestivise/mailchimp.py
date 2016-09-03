from keys import mailchimp_api_key, mailchimp_list_id, mailchimp_referal_id, mandrill_api_key
import requests
import json
import mandrill
from mailchimpStyles import holdingProcessing

mandrill_client = mandrill.Mandrill(mandrill_api_key)

MAILCHIMP_URL = "https://us13.api.mailchimp.com/3.0/"
SUBSCRIBE_LIST = MAILCHIMP_URL + "lists/" + mailchimp_list_id + "/members"


def subscribeToMailChimp(firstName, lastName, email):
    firstName = firstName
    lastName = lastName
    email = email
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
        print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
        raise

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
        print 'A mandrill error occurred: %s - %s' % (e.__class__, e)
        raise
