def fallback_response(user_text: str) -> str:
    return "I am offline or unconfigured. I heard: " + (user_text[:200] if user_text else "nothing")
