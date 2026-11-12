import asyncio
import json
import random
import time
import uuid
from datetime import datetime, timezone
MAX_ITERATIONS = 8
MAX_RETRIES = 2
AUDIT_FILE = "audit_log.jsonl"
run_id = str(uuid.uuid4())
ORDERS = {
    "1042": {
        "order_id": "1042",
        "customer_id": "5",
        "amount": 2500,
        "status": "Delivered"
    }
}
CUSTOMERS = {
    "5": {
        "customer_id": "5",
        "name": "Santhosh",
        "email": "santhosh@example.com"
    }
}
POLICIES = {
    "1042": {
        "eligible": True,
        "reason": "Order is eligible for refund"
    }
}
async def get_order(order_id):
    await asyncio.sleep(1)
    if str(order_id) not in ORDERS:
        raise ValueError("Order not found")
    return ORDERS[str(order_id)]
async def get_customer(customer_id):
    await asyncio.sleep(1)
    if str(customer_id) not in CUSTOMERS:
        raise ValueError("Customer not found")
    return CUSTOMERS[str(customer_id)]
async def check_policy(order_id):
    await asyncio.sleep(1)
    if str(order_id) not in POLICIES:
        raise ValueError("Policy not found")
    return POLICIES[str(order_id)]
async def draft_email(customer_id, text):
    customer = await get_customer(customer_id)
    return {
        "status": "DRAFT_CREATED",
        "to": customer["email"],
        "message": text
    }
async def issue_refund(order_id, amount):
    return {
        "status": "PENDING APPROVAL",
        "order_id": order_id,
        "amount": amount
    }
TOOL_REGISTRY = {
    "get_order": {
        "function": get_order,
        "risk": "READ",
        "schema": {
            "order_id": "string"
        }
    },

    "get_customer": {
        "function": get_customer,
        "risk": "READ",
        "schema": {
            "customer_id": "string"
        }
    },

    "check_policy": {
        "function": check_policy,
        "risk": "READ",
        "schema": {
            "order_id": "string"
        }
    },

    "draft_email": {
        "function": draft_email,
        "risk": "WRITE",
        "schema": {
            "customer_id": "string",
            "text": "string"
        }
    },

    "issue_refund": {
        "function": issue_refund,
        "risk": "DELETE_SEND",
        "schema": {
            "order_id": "string",
            "amount": "number"
        }
    }
}
def log_step(step, action, action_input,
             observation, thought="Executing tool"):

    record = {
        "run_id": run_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "step": step,
        "thought": thought,
        "action": action,
        "action_input": action_input,
        "observation": observation,
        "tokens": 0
    }

    with open(AUDIT_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")
failure_state = {}
async def execute_with_retry(tool_name, arguments):
    tool = TOOL_REGISTRY[tool_name]
    for attempt in range(MAX_RETRIES + 1):
        try:
            if (
                tool_name == failure_state.get("fail_tool")
                and failure_state.get("failed") is False
            ):
                failure_state["failed"] = True
                raise TimeoutError("timeout")
            result = await tool["function"](**arguments)
            if attempt > 0:
                print(
                    f"Tool {tool_name}: retry {attempt} succeeded"
                )
            return {
                "status": "success",
                "result": result
            }
        except Exception as error:
            observation = {
                "error": str(error),
                "tool": tool_name,
                "attempt": attempt + 1
            }
            print(
                f"Tool failed: {error} -> retry {attempt + 1}"
            )
            log_step(
                attempt + 1,
                tool_name,
                arguments,
                observation,
                "Tool execution failed; passing error as observation"
            )
            if attempt == MAX_RETRIES:
                return {
                    "status": "failed",
                    "error": str(error)
                }
    return {
        "status": "failed",
        "error": "Unknown error"
    }
async def sequential_execution():
    print("\n--- SEQUENTIAL EXECUTION ---")
    start = time.perf_counter()
    await get_order("1042")
    await get_customer("5")
    await check_policy("1042")
    elapsed = time.perf_counter() - start
    print(f"Sequential time: {elapsed:.2f} seconds")
    return elapsed
async def parallel_execution():
    print("\n--- PARALLEL EXECUTION ---")
    start = time.perf_counter()
    results = await asyncio.gather(
        execute_with_retry(
            "get_order",
            {"order_id": "1042"}
        ),
        execute_with_retry(
            "get_customer",
            {"customer_id": "5"}
        ),
        execute_with_retry(
            "check_policy",
            {"order_id": "1042"}
        )

    )
    elapsed = time.perf_counter() - start
    print(f"Parallel time: {elapsed:.2f} seconds")
    return results, elapsed
async def run_agent(run_number):
    global run_id, failure_state
    run_id = str(uuid.uuid4())
    print("\n================================")
    print(f"AGENT RUN {run_number}")
    print("================================")
    failure_state = {
        "fail_tool": random.choice([
            "get_order",
            "get_customer",
            "check_policy"
        ]),
        "failed": False
    }
    print("Selected temporary failure:",
          failure_state["fail_tool"])
    print(
        "\nUser: Customer 5 asks for a refund "
        "for order 1042"
    )
    try:
        results, elapsed = await parallel_execution()
        for index, result in enumerate(results, start=1):
            tool_name = [
                "get_order",
                "get_customer",
                "check_policy"
            ][index - 1]

            log_step(
                index,
                tool_name,
                {},
                result,
                "Received tool observation"
            )

        order = results[0]
        customer = results[1]
        policy = results[2]

        if all(
            item["status"] == "success"
            for item in results
        ):
            if policy["result"]["eligible"]:
                refund = await issue_refund(
                    "1042",
                    order["result"]["amount"]
                )
                print("\nRefund result:", refund)
            else:
                print("\nRefund rejected: Policy not eligible.")
        else:
            print(
                "\nAgent could not complete the refund "
                "because a lookup failed."
            )
        print("\nAgent run completed safely.")
    except Exception as error:
        print("Unexpected error handled:", error)
    print(f"Run {run_number} finished.")
async def main():
    open(AUDIT_FILE, "w", encoding="utf-8").close()
    sequential_time = await sequential_execution()
    results, parallel_time = await parallel_execution()
    print("\n--- TIME COMPARISON ---")
    print(
        f"Sequential {sequential_time:.2f} s | "
        f"Parallel {parallel_time:.2f} s"
    )
    for i in range(1, 4):
        await run_agent(i)
    print("\n========== AUDIT TRAIL ==========")
    with open(AUDIT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            print(json.dumps(
                json.loads(line),
                indent=4
            ))
if __name__ == "__main__":
    asyncio.run(main())