# Badminton Bot

Automates badminton court booking via third-party APIs and LINE notifications.

---

## How it Works

1. Use the court API to log in, and explicitly set the User-Agent header to help prevent the website from
   detecting the script as a bot.
2. Fetch available slots and attempt to reserve them by adding to the cart.
3. Continuously retry the reservation process to secure the slots as early as possible.
4. Send the notification to LINE group
5. Monitor the cart after adding items — if any items are removed by the admin, attempt to re-add them automatically.

---

### Booking Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant Scheduler
    participant App
    participant SSM as SSM Parameter Store
    participant Court as Court API
    participant LINE as LINE API

    Scheduler->>App: Trigger court booking request

    App->>SSM: Get court account credentials
    SSM-->>App: Return court account

    App->>SSM: Get LINE secret
    SSM-->>App: Return LINE secret

    App->>Court: Login with credentials
    App->>Court: Book courts
    App->>Court: Check cart
    Court-->>App: Return cart data

    App->>LINE: Send notification (message, group_id)

    alt Cart contains items
        App->>Court: Reserve items in cart
    end

```

---

## Architecture

![image](diagram.png)

---

### Event Bridge

Define scheduled events to automatically trigger the lambda function when the reservation is available

Sample event:

```
{
     "accountId": "1",
     "location": "queensbridge-sports-community-centre",
     "activity": "badminton-40min",
     "keyword": "Court 1,Court 3",
     "day_offset": 7,
     "slots": [
         {
             "start_time": "11:00",
             "end_time": "11:40"
         },
         {
             "start_time": "11:40",
             "end_time": "12:20"
         }
     ]
 }
```

---

### SSM Parameter Store

Store the account details (username, password) and LINE secrets as SecureStrings in AWS Systems Manager Parameter Store to save costs. The lambda function fetches them by path (e.g., `account_1`, `line_secret`).

---

## Local Development & Testing

You can run the application locally to test the booking flow with a sample request.

### Setup
```bash
make setup
```

### Run Local Test
By default, running the app locally uses the `dev` environment (loads `line_secret_dev`).
```bash
make run-dev
```

### Run Tests
```bash
make test
```

---

## UI - LINE Notifications

Integrated LINE API to send the flex message to target group

<img src="./flex-message-ui.png" width=240 alt="">