import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for,send_from_directory
import uuid
import squareAuth

app = Flask(__name__)
idempotency_key = str(uuid.uuid4())

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/charge', methods=['POST','GET'])
def charge():
    amount = int(request.form['amount'])
    email = request.form['email']
    givenName = request.form['givenName']
    familyName = request.form['familyName']
    billing = request.form['billing']
    locality = request.form['locality']
    country = request.form['country']
     
    # CREATE CUSTOMER
    result = squareAuth.client.customers.create_customer(
    body = {
        "idempotency_key": idempotency_key,
        "given_name": givenName,
        "family_name": familyName,
        "email_address": email
    }
    )


    if result.is_success():
        # print(result.body)
        customer_id = result.body['customer']['id']
        # print(customer_id)
    elif result.is_error():
        print(result.errors)
    
    # CREATE CARD    
    c_result = squareAuth.client.cards.create_card(
    body = {
    "idempotency_key": idempotency_key,
    "source_id": "cnon:card-nonce-ok",
    "card": {
        "cardholder_name": givenName + familyName,
        "billing_address": {
        "address_line_1": "500 Electric Ave",
        "address_line_2": billing,
        "locality": locality,
        "administrative_district_level_1": "NY",
        "postal_code": "94103",
        "country": country
        },
        "customer_id": customer_id,
        "reference_id": "alternate-id-1"
    }
    }
    )

    # Get Card Details
    if c_result.is_success():
        # print(c_result.body)
        card_id = c_result.body['card']['id']
        print("Card ID:", card_id)
    elif c_result.is_error():
        print(c_result.errors)
    
        
    #CREATE ORDER
    o_result = squareAuth.client.orders.create_order(
    body = {
        "order": {
        "location_id": "LJGHD7PBGN574",
        "customer_id": customer_id,
        "line_items": [
            {
            "name": "MpaMpe Donation",
            "quantity": "1",
            "base_price_money": {
                "amount": amount,
                "currency": "USD"
            }
            }
        ]
        },
        "idempotency_key": idempotency_key
    }
    )

    if o_result.is_success():
        # print(o_result.body)
        order_id = o_result.body['order']['id']
        print("Order ID:", order_id)
    elif o_result.is_error():
        print(o_result.errors)
        
    #CREATE INVOICE  
    i_result = squareAuth.client.invoices.create_invoice(
    body = {
        "invoice": {
        "order_id": order_id,
        "primary_recipient": {
            "customer_id": customer_id
        },
        "payment_requests": [
            {
            "request_type": "BALANCE",
            "due_date": "2023-11-30"
            }
        ],
        "delivery_method": "EMAIL",
        "accepted_payment_methods": {
            "card": True
        }
        },
        "idempotency_key": idempotency_key
    }
    )

    if i_result.is_success():
        # print(i_result.body)
        invoice_order_id = i_result.body['invoice']['id']
        print("Invoice Order ID:", invoice_order_id)
    elif i_result.is_error():
        print(i_result.errors)

    #PUBLISH INVOICE
    p_result = squareAuth.client.invoices.publish_invoice(
    invoice_id = invoice_order_id,
    body = {
        "version": 0,
        "idempotency_key": idempotency_key
    }
    )

    if p_result.is_success():
        # print(p_result.body)
        public_url = p_result.body['invoice']['public_url']
        print("Public URL:", public_url)
    elif p_result.is_error():
        print(p_result.errors)
        
    if public_url:
        return redirect(public_url)
    else:
        return "Payment initiation failed."

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory('images', filename)

@app.route('/success')
def success():
    return render_template('success.html')

if __name__ == '__main__':
    app.run()
