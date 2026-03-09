
def route_intent(parsed):
    topic = parsed["topic"]
    # Simple routing based on topic
    if topic == "algebra":
        return "algebra_solver"
    elif topic == "probability":
        return "probability_solver"
    elif topic == "calculus":
        return "calculus_solver"
    elif topic == "linear_algebra":
        return "linear_solver"
    else:
        return "general_solver"