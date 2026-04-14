import os
import httpx

URL = "https://assets.deadlock-api.com/v2/ranks"
SAVE_DIR = "ranks_assets"

os.makedirs(SAVE_DIR, exist_ok=True)


def get_filename(url: str) -> str:
    return url.split("/")[-1]


async def main():
    async with httpx.AsyncClient(timeout=30) as client:
        # 1. fetch rank metadata
        res = await client.get(URL)
        res.raise_for_status()
        ranks = res.json()

        downloaded = set()

        # 2. extract all image URLs
        for rank in ranks:
            images = rank.get("images", {})

            for url in images.values():
                if not isinstance(url, str):
                    continue

                if url in downloaded:
                    continue  # avoid duplicates

                downloaded.add(url)

                filename = get_filename(url)
                path = os.path.join(SAVE_DIR, filename)

                # 3. download image
                img = await client.get(url)
                img.raise_for_status()

                with open(path, "wb") as f:
                    f.write(img.content)

                print(f"Downloaded: {filename}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())