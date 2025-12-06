from flask import Flask, request, Response
import stripe
from dotenv import load_dotenv
import logging
import os

load_dotenv(verbose=True)

PYTHON_LOG_LEVEL = os.environ.get("PYTHON_LOG_LEVEL", "WARNING")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_BUY_BUTTON_ID = os.environ.get("STRIPE_BUY_BUTTON_ID")
WEBHOOK_CLIENT_REFERENCE_ID_LOG_FILE_FULL_PATH = os.environ.get("WEBHOOK_CLIENT_REFERENCE_ID_LOG_FILE_FULL_PATH")

log = logging.getLogger(__name__)
log.setLevel(PYTHON_LOG_LEVEL)
log.addHandler(logging.StreamHandler())

STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

if STRIPE_WEBHOOK_SECRET is None:
    raise Exception("STRIPE_WEBHOOK_SECRET is not set")

if STRIPE_PUBLISHABLE_KEY is None:
    raise Exception("STRIPE_PUBLISHABLE_KEY is not set")

if STRIPE_BUY_BUTTON_ID is None:
    raise Exception("STRIPE_BUY_BUTTON_ID is not set")

if WEBHOOK_CLIENT_REFERENCE_ID_LOG_FILE_FULL_PATH is None:
    raise Exception("WEBHOOK_CLIENT_REFERENCE_ID_LOG_FILE_FULL_PATH is not set")

print(f"PYTHON_LOG_LEVEL is: {PYTHON_LOG_LEVEL}")
app = Flask(__name__)


@app.route("/")
def test_payment():

    return f"""
          <!-- Stripe Buy Button -->
          <script async src="https://js.stripe.com/v3/buy-button.js"></script>
          <div id="stripe-buy-button"></div>

          <script>
          // Create buy button
          elm = document.createElement("stripe-buy-button");
          elm.setAttribute("publishable-key", "{ STRIPE_PUBLISHABLE_KEY }")
          elm.setAttribute("buy-button-id", "{ STRIPE_BUY_BUTTON_ID}")
          elm.setAttribute("client-reference-id", document.location.host.split('.')[0])
          document.getElementById("stripe-buy-button").appendChild(elm)
          </script>
    """

@app.route("/", methods=["POST"])
def receive_stripe_webhook_event():
    """Receive stripe webhook event(s)"""
    # Verify stripe signature header
    sig_header = request.headers.get("Stripe-Signature", None)
    event = None
    try:
        event = stripe.Webhook.construct_event(
            request.data, sig_header, STRIPE_WEBHOOK_SECRET
        )
        log.debug(event)
        # Handle the event
        if event.type == 'checkout.session.completed':
            log.info('Processing Stripe event type {}'.format(event.type))
            client_reference_id = event.data.object.get("client_reference_id")
            if client_reference_id is None:
                log.error(f"No client_reference_id on Stripe event checkout.session.completed")
            # Write client_reference_id to file/database
            with open("webhook-client_reference_id.log", "a") as fp:
                fp.write(f"{client_reference_id}\n")        

        else:
            log.error('Unhandled Stripe event type {}'.format(event.type))

    except ValueError as e:
        msg = "ValueError when attempting to get Stripe-Signature header"  # noqa: E501
        log.error(msg)
        log.error(e)
        return e, 400
    except stripe.error.SignatureVerificationError as e:
        log.error("Stripe SignatureVerificationError")
        log.error(e)
        return "Stripe SignatureVerificationError", 400

    except Exception as e:
        log.error("Error processing stripe webhook request")
        log.error(e)
    return "Invalid request to route_stripe_connect_webhook", 400