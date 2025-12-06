# Generic Stripe Webhook listener

As title.

## Local development

```shell
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

Run

```shell
FLASK_APP=main flask run --debug
```

Visit http://127.0.0.1

Send Stripe webhook events locally

```shell
stripe listen --events customer.subscription.created --forward-to localhost:5000
```
