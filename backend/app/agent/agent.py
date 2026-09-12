class Agent:
    """Minimal agent interface; provider execution is added in the next milestone."""

    async def run(self, message: str) -> str:
        return f"Agent received: {message}"
