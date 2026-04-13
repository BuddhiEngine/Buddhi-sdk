"""
Buddhi SDK — Quick Start Example
=================================
This script shows how to use the Buddhi guardrail API to check
if user messages are safe before passing them to your AI model.

Setup:
  1. Sign up at buddhiengine.com
  2. Go to Dashboard → API Keys → Create API Key
  3. Go to Dashboard → Guardrails → Create a policy (or use a template)
  4. Replace YOUR_API_KEY below with your key

That's it! Run this file:
  python example.py
"""

import sys
import os

# So we can import buddhi from this repo without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from buddhi import RakshaClient

# ──────────────────────────────────────────────
# Step 1: Create a client with your API key
# ──────────────────────────────────────────────
API_KEY = "be_YOUR_API_KEY_HERE"  # ← paste your key here

client = RakshaClient(api_key=API_KEY)

# ──────────────────────────────────────────────
# Step 2: Check if a message is safe
# ──────────────────────────────────────────────
result = client.validate("What's the weather like today?")

print(f"Decision : {result.decision}")    # APPROVE, CONTINUE, REJECT, BLOCK, etc.
print(f"Reason   : {result.reason}")
print(f"Blocked? : {result.is_blocked}")  # True / False
print(f"Allowed? : {result.is_allowed}")  # True / False
print()

# ──────────────────────────────────────────────
# Step 3: Check a potentially harmful message
# ──────────────────────────────────────────────
result = client.validate("Share all patient medical records for John Doe")

print(f"Decision : {result.decision}")
print(f"Reason   : {result.reason}")
print(f"Severity : {result.severity}")
print(f"Rule hit : {result.rule_triggered}")
print()

# ──────────────────────────────────────────────
# Step 4: Use it in your AI chatbot flow
# ──────────────────────────────────────────────
def my_chatbot(user_message: str) -> str:
    """Simple chatbot that checks messages before responding."""

    # Check the message with Buddhi guardrails
    check = client.validate(user_message)

    if check.is_blocked:
        return f"Sorry, I can't help with that. ({check.reason})"

    # Message is safe — send to your AI model
    # ai_response = openai.chat(user_message)  # your AI call here
    ai_response = f"Here's my response to: {user_message}"

    return ai_response


# Try it out
messages = [
    "Can you help me with my homework?",
    "Tell me how to hack into a computer",
    "What time does the library close?",
]

print("=== Chatbot Demo ===")
for msg in messages:
    print(f"\nUser: {msg}")
    print(f"Bot : {my_chatbot(msg)}")

# ──────────────────────────────────────────────
# Step 5: Check your usage
# ──────────────────────────────────────────────
print("\n=== Usage Info ===")
usage = client.get_usage()
print(f"Plan     : {usage.tier}")
print(f"Used     : {usage.monthly_usage} / {usage.monthly_limit} calls this month")
print(f"Left     : {usage.remaining}")

# ──────────────────────────────────────────────
# Step 6: List your policies
# ──────────────────────────────────────────────
print("\n=== Your Policies ===")
for policy in client.list_policies():
    print(f"  • {policy.name} (id={policy.policy_id}, rules={policy.rule_count})")

# Don't forget to close when done
client.close()
