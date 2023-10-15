import squareAuth
import uuid
 
idempotency_key = str(uuid.uuid4())

# CREATE CUSTOMER
result = squareAuth.client.customers.create_customer(
body = {
    "idempotency_key": idempotency_key,
    "given_name": "John",
    "family_name": "Doe",
    "email_address": "johndoe@company.com"
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
    "cardholder_name": "John Doe",
    "billing_address": {
    "address_line_1": "500 Electric Ave",
    "address_line_2": "Suite 600",
    "locality": "New York",
    "administrative_district_level_1": "NY",
    "postal_code": "94103",
    "country": "US"
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
            "amount": 100,
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






# if result.is_success():
#     response_data = result.body
#     # print(result.body)
# elif result.is_error():
#     print(result.errors)
        
# # Assuming 'response' contains the JSON response you provided
# payment_link = response_data.get('payment_link', {})

# # Extract the payment URL
# payment_url = payment_link.get('url')

# if payment_url:
#     print(f'Payment URL for redirection: {payment_url}')
# else:
#     print('Payment URL not found in the response.')