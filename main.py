import argparse
import asyncio

from app.agent.manus import Manus
from app.config import config
from app.logger import logger


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Manus agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    parser.add_argument(
        "--model", type=str, default="reasoning", help="Model to use: 'reasoning' (Phi-3) or 'lightweight' (TinyLlama)"
    )
    args = parser.parse_args()

    # Create and initialize Manus agent
    agent = await Manus.create()
    try:
        # Use command line prompt if provided, otherwise ask for input
        prompt = args.prompt if args.prompt else input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        # Use local models if available
        if config.is_local_mode and config.local_model_handler:
            if args.model == "lightweight":
                response = await agent.quick_task(prompt)
            else:
                response = await agent.run_with_local_models(prompt)
            print(f"🤖 Response: {response}")
        else:
            await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())