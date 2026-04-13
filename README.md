# buddhi-client

**Python SDK for the Buddhi Engine — AI Guardrail Validation**

Validate AI inputs and outputs against safety policies in 3 lines of code.
Built for the [Buddhi Engine](https://buddhiengine.com) guardrail platform (Raksha M).

---

## Installation

```bash
pip install buddhi-client
```

Requires Python 3.8+.

## Quick Start

```python
from buddhi import RakshaClient

client = RakshaClient(api_key="be_YOUR_KEY")

result = client.validate("Can you share patient lab results?")
print(result.decision)   # "APPROVE" or "BLOCK"
print(result.is_blocked)  # True / False
```

## Setup

1. Sign up at [buddhiengine.com](https://buddhiengine.com)
2. Create an API key in **Dashboard → API Keys**
3. Create a guardrail policy in **Dashboard → Guardrails** (or use a template)
4. Install: `pip install buddhi-client`

## Usage

### Basic Validation

```python
from buddhi import RakshaClient

client = RakshaClient(api_key="be_abc123...")

# Check a user message
result = client.validate("What's the weather like?")
print(result.decision)      # APPROVE, BLOCK, REJECT, CONTINUE, WARN
print(result.is_allowed)    # True
print(result.is_blocked)    # False
```

### Validate Against a Specific Policy

```python
result = client.validate(
    "Delete all user data",
    policy_id="data-protection-policy-a1b2c3d4",
)
print(result.reason)
print(result.rule_triggered)
print(result.severity)
```

### Use in a Chatbot / AI Pipeline

```python
def chatbot(user_message: str) -> str:
    check = client.validate(user_message)

    if check.is_blocked:
        return f"I can't help with that. ({check.reason})"

    # Safe — call your AI model
    return my_llm.generate(user_message)
```

### Rich Context (Dict Input)

Pass structured context when your policy rules need extra fields:

```python
result = client.validate({
    "user_message": "Book a meeting at 3am",
    "user_role": "intern",
    "department": "finance",
})
```

### Batch Evaluation (Professional+)

```python
results = client.validate_batch([
    {"input_context": "message 1"},
    {"input_context": "message 2", "policy_id": "my-policy"},
])
for r in results.results:
    print(r.decision)
```

### Check Usage

```python
usage = client.get_usage()
print(f"{usage.monthly_usage}/{usage.monthly_limit} calls used")
print(f"{usage.remaining} remaining")
```

### List Policies

```python
for policy in client.list_policies():
    print(f"{policy.name} (rules={policy.rule_count})")
```

### Async Client

```python
import asyncio
from buddhi import AsyncRakshaClient

async def main():
    async with AsyncRakshaClient(api_key="be_abc123...") as client:
        result = await client.validate("Check this message")
        print(result.decision)

asyncio.run(main())
```

### Self-Hosted / Custom Base URL

```python
client = RakshaClient(
    api_key="be_abc123...",
    base_url="https://guardrails.yourcompany.internal/api/v1",
)
```

### Specific Instance

```python
client = RakshaClient(
    api_key="be_abc123...",
    instance_id="aerm_005_prod",
)
```

## Response Object

```python
result = client.validate("some text")

result.decision          # str: APPROVE, BLOCK, REJECT, CONTINUE, WARN
result.reason            # str or None
result.severity          # str or None
result.rule_triggered    # str or None
result.policy_id         # str or None
result.evaluated_rules   # int
result.execution_time_ms # float
result.trace             # dict or None (if include_trace=True)
result.usage             # dict: {monthly_limit, monthly_usage, remaining}

result.is_allowed        # True if APPROVE or CONTINUE
result.is_blocked        # True if BLOCK, BLOCKED, or REJECT
```

## Error Handling

```python
from buddhi import (
    RakshaClient,
    AuthenticationError,
    QuotaExceededError,
    PolicyNotFoundError,
    InstanceUnavailableError,
)

client = RakshaClient(api_key="be_abc123...")

try:
    result = client.validate("test")
except AuthenticationError:
    print("Bad API key")
except QuotaExceededError:
    print("Monthly limit reached — upgrade your plan")
except PolicyNotFoundError:
    print("Policy doesn't exist")
except InstanceUnavailableError:
    print("No running AERM instance — start one in the dashboard")
```

## Pricing Tiers

| Plan         | Monthly Calls | Overage       | Batch |
|--------------|--------------|---------------|-------|
| Starter/Free | 500          | Blocked (429) | No    |
| Professional | 10,000       | $0.012/call   | Yes   |
| Business     | 100,000      | $0.006/call   | Yes   |
| Enterprise   | Unlimited    | Negotiated    | Yes   |

## Requirements

- Python >= 3.8
- [httpx](https://www.python-httpx.org/) >= 0.24.0
- [pydantic](https://docs.pydantic.dev/) >= 2.0.0

## License

MIT
