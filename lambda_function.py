# Adapted from https://github.com/aws-samples/aws-news-feed-chime-webhook

import os
import pytz
import requests
import re
from datetime import datetime
from datetime import timedelta
import xml.etree.ElementTree as ET
import time


def lambda_handler(event, context):
    RSS_PAGE = "https://aws.amazon.com/about-aws/whats-new/recent/feed"
    POST_HEADERS = {"Content-Type": "application/json"}
    GET_HEADERS = {"Accept": "application/xml", "Content-Type": "application/xml"}
    ADDRESS = "<Slack/MS Teams/Amazon Chime Incoming Webook URL>"
    AWS_SERVICES = [
        "SageMaker",
        "Glue",
        "Athena",
    ]

    xml = requests.get(RSS_PAGE, headers=GET_HEADERS)
    root = ET.fromstring(xml.text)

    for entry in root.iter("item"):
        published_datetime = datetime.strptime(
            entry.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z"
        )
        yesterday_datetime = datetime.now(pytz.utc) - timedelta(days=1)

        # Skip the item if the post was published more than 1 day ago
        if published_datetime < yesterday_datetime:
            continue

        publish = False
        for service in AWS_SERVICES:
            if entry.find("title").text.__contains__(service):
                publish = True
                break

        if publish:

            # `#x1F680` = Rocket Emoji 
            # Payload represents format required by MS Teams Incoming Webhooks
            payload = (
                "{"
                + f'"title":"&#x1F680 &#x1F680 &#x1F680 {entry.find("title").text}  &#x1F680 &#x1F680 &#x1F680 " , '
                + '"text":"'
                + f'[{entry.find("link").text}]({entry.find("link").text})'
                + '"}'
            )

            print("Payload:", payload)

            response = requests.post(
                ADDRESS, data=payload.encode("utf-8"), headers=POST_HEADERS
            )

            print("HTTP Response Code", response.status_code)
            time.sleep(1)

    return "Done"
