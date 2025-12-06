import asyncio
import time
import sys, os

# Ensure project root is in Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.services.medgemma import get_med_gemma3


async def run_test():
    start = time.time()

    model = get_med_gemma3()

    print("Sending test query to Bio-Medical Llama model...")

    query = "i'm have a fever, what should i do?"
    response = await model.generate_simple(query)

    print("\n--- Model Response ---")
    print(response)

    end = time.time()
    print(f"\n⏱ Time taken: {end - start:.2f} seconds")


if __name__ == "__main__":
    st = time.time()
    asyncio.run(run_test())
    et = time.time()
    print(et-st)

