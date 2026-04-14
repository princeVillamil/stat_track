import asyncio
import json
from services.deadlock_client import get_leaderboard, get_player_mmr_history


async def test():
    # 1. Test Leaderboard
    print("\n[TEST] get_leaderboard('Asia')...")
    lb = await get_leaderboard("Asia")

    if lb:
        # Print just the first entry to avoid flooding the terminal
        first_entry = lb.get("entries", [])[:10]
        # print()
        print(f"Total Players: {len(lb.get('entries', []))}")
        print("First 5 Entry Structure:")
        print(json.dumps(first_entry, indent=2))
    else:
        print("Leaderboard returned None or empty.")

    # 2. Test Player History (Use a real account ID if possible)
    # test_id = 12345
    # print(f"\n[TEST] get_player_mmr_history({test_id})...")
    # history = await get_player_mmr_history(test_id)

    # if history:
    #     print(json.dumps(history, indent=2))
    # else:
    #     print(f"No history found for ID {test_id} (404 expected if ID is fake).")


if __name__ == "__main__":
    asyncio.run(test())