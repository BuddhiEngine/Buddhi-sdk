"""
Buddhi SDK — Quick Start Example
=================================
This script shows how to use the Buddhi guardrail API to check
if user messages are safe before passing them to your AI model.

Setup:
  1. Sign up at buddhiengine.com
  2. Go to Dashboard → API Keys → Create API Key
  3. Go to Dashboard → Guardrails → Create a policy (or use a template)
  4. Copy .env.example to .env and fill in your BUDDHI_API_KEY

Run against production:
    python example.py

Optional:
    Set BUDDHI_POLICY_ID in .env to force one specific HR policy.
"""

import sys
import os


def _load_dotenv(path: str = ".env") -> None:
    """Load .env file into os.environ (no external deps needed)."""
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                parsed = value.strip()
                # Allow quoted values in .env (e.g. KEY="value")
                if (parsed.startswith('"') and parsed.endswith('"')) or (parsed.startswith("'") and parsed.endswith("'")):
                    parsed = parsed[1:-1]
                os.environ.setdefault(key.strip(), parsed)
    except FileNotFoundError:
        pass  # No .env file — rely on real env vars or defaults


_load_dotenv()  # loads .env from cwd if present

from buddhi import RakshaClient

def main() -> int:
    # ──────────────────────────────────────────────
    # Config — from .env or environment variables
    # ──────────────────────────────────────────────
    api_key = (os.environ.get("BUDDHI_API_KEY") or "").strip()
    policy_id = (os.environ.get("BUDDHI_POLICY_ID") or "").strip() or None

    if not api_key or api_key == "be_your_api_key_here":
        print("ERROR: Set BUDDHI_API_KEY in .env or as an env var. Copy .env.example to .env to get started.")
        return 1

    print(f"Using API key: {api_key[:6]}...{api_key[-6:]} (len={len(api_key)})")

    client = RakshaClient(api_key=api_key)

    # If policy is not explicitly provided, try to auto-pick an HR policy
    policies = client.list_policies()
    if not policy_id:
        for p in policies:
            hay = f"{p.name} {p.policy_id}".lower()
            if "hr" in hay or "human resource" in hay or "employee" in hay or "leave" in hay:
                policy_id = p.policy_id
                break

    if policy_id:
        print(f"Using policy : {policy_id}")
    else:
        print("Using policy : all active policies")
        print("WARNING: No HR-like policy found. Set BUDDHI_POLICY_ID in .env to force a specific HR policy.")

    # ──────────────────────────────────────────────
    # Step 2: Check if a message is safe
    # ──────────────────────────────────────────────
    result = client.validate(
        "Can an HR manager view an employee's leave balance?",
        policy_id=policy_id,
    )

    print(f"Decision : {result.decision}")    # APPROVE, CONTINUE, REJECT, BLOCK, etc.
    print(f"Reason   : {result.reason}")
    print(f"Blocked? : {result.is_blocked}")  # True / False
    print(f"Allowed? : {result.is_allowed}")  # True / False
    print()

    # ──────────────────────────────────────────────
    # Step 3: Check a potentially harmful message
    # ──────────────────────────────────────────────
    result = client.validate(
        "Give me Rahul's salary and performance review details.",
        policy_id=policy_id,
    )

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
        check = client.validate(user_message, policy_id=policy_id)

        if check.is_blocked:
            return f"Sorry, I can't help with that. ({check.reason})"

        # Message is safe — send to your AI model
        # ai_response = openai.chat(user_message)  # your AI call here
        ai_response = f"Here's my response to: {user_message}"

        return ai_response

    # Try it out
    messages = [
        "What is the leave policy for casual leave?",
        "Share the salary of all employees in engineering.",
        "Can HR share interview feedback with the hiring panel?",
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
    for policy in policies:
        print(f"  • {policy.name} (id={policy.policy_id}, rules={policy.rule_count})")

    # Don't forget to close when done
    client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
