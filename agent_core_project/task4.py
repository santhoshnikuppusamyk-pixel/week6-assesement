import asyncio
import time
ORDERS = {
    "1042": {
        "order_id": "1042",
        "customer_id": "5",
        "amount": 2500,
        "status": "Delivered"
    },
    "1043": {
        "order_id": "1043",
        "customer_id": "6",
        "amount": 1500,
        "status": "Shipped"
    }
}
REFUND_POLICY = {
    "eligible": True,
    "period": "7 days"
}

def refund_agent(request):

    print("[REFUND AGENT] Processing request")

    if "1042" in request:
        order = ORDERS["1042"]

        return (
            f"Refund information: Order {order['order_id']} "
            f"amount Rs.{order['amount']}. "
            f"Eligibility: {REFUND_POLICY['eligible']}. "
            "Actual refund requires human approval."
        )

    return "Please provide a valid order ID for refund."
def order_status_agent(request):
    print("[ORDER STATUS AGENT] Processing request")
    for order_id, order in ORDERS.items():
        if order_id in request:
            return (
                f"Order {order_id} status is "
                f"{order['status']}."
            )

    return "Order not found."
def general_info_agent(request):

    print("[GENERAL INFO AGENT] Processing request")

    return (
        "Our customer support team is available "
        "Monday to Saturday, 9 AM to 6 PM. "
        "You can contact support for order, "
        "refund and product-related queries."
    )
def router(request):

    text = request.lower()

    refund_keywords = [
        "refund", "money back", "reimbursement",
        "return my money"
    ]

    order_keywords = [
        "order status", "track order",
        "where is my order", "delivery status",
        "shipment status"
    ]

    if any(word in text for word in refund_keywords):
        return "refund"

    elif any(word in text for word in order_keywords):
        return "order-status"

    else:
        return "general-info"

AGENTS = {
    "refund": refund_agent,
    "order-status": order_status_agent,
    "general-info": general_info_agent
}
def dispatch(request):

    selected_agent = router(request)
    print("\nCustomer:", request)
    print("Selected agent:", selected_agent)
    response = AGENTS[selected_agent](request)
    print("Agent response:", response)
    return selected_agent, response

def test_routing():

    test_cases = [
        ("I want a refund for order 1042", "refund"),
        ("Please return my money for my purchase", "refund"),
        ("I need reimbursement for my order", "refund"),
        ("What is the order status of 1042?", "order-status"),
        ("Track order 1043", "order-status"),
        ("Where is my order?", "order-status"),
        ("What are your customer support hours?", "general-info"),
        ("How can I contact customer support?", "general-info"),
        ("Tell me about your support services", "general-info")
    ]
    correct = 0
    total = len(test_cases)
    print("\n========== ROUTING TEST ==========")
    for index, (request, expected) in enumerate(
        test_cases, start=1
    ):
        actual = router(request)
        if actual == expected:
            correct += 1
            result = "PASS"
        else:
            result = "FAIL"
        print(f"\nTest {index}: {request}")
        print("Expected:", expected)
        print("Actual:", actual)
        print("Result:", result)
    accuracy = (correct / total) * 100
    print("\n========== ROUTING ACCURACY ==========")
    print(f"Correct: {correct}/{total}")
    print(f"Accuracy: {accuracy:.2f}%")
    return accuracy
async def order_research_agent():
    print("[SUB-AGENT 1] Researching order details")
    await asyncio.sleep(2)
    return {
        "order_status": "Delivered",
        "order_amount": 2500
    }
async def customer_research_agent():
    print("[SUB-AGENT 2] Researching customer details")
    await asyncio.sleep(2)
    return {
        "customer_name": "Santhosh",
        "customer_id": "5",
        "support_status": "Active"
    }
async def orchestrator():
    print("\n========== ORCHESTRATOR ==========")
    start = time.perf_counter()
    order_result, customer_result = await asyncio.gather(
        order_research_agent(),
        customer_research_agent()
    )
    elapsed = time.perf_counter() - start
    final_answer = {
        "customer": customer_result["customer_name"],
        "customer_id": customer_result["customer_id"],
        "order_status": order_result["order_status"],
        "order_amount": order_result["order_amount"],
        "support_status": customer_result["support_status"]
    }
    print("\n========== AGGREGATED ANSWER ==========")
    print(final_answer)
    print(f"\nParallel execution time: {elapsed:.2f} seconds")
    return final_answer
async def main():
    print("\n******** TASK 4: ROUTER ********")
    accuracy = test_routing()
    await orchestrator()
    print("\n========== FINAL SUMMARY ==========")
    print(f"Routing accuracy: {accuracy:.0f}%")
    print("Router testing completed.")
    print("Parallel sub-agents completed.")
    print("Results aggregated successfully.")
if __name__ == "__main__":
    asyncio.run(main())
