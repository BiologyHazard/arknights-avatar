import asyncio
from hashlib import md5
from pathlib import Path
from urllib.parse import quote

import httpx

from professions import PROFESSION_DICT


def get_prts_url(image_name: str):
    md5_str = md5(image_name.encode("utf-8")).hexdigest()
    url = f"https://media.prts.wiki/{md5_str[0]}/{md5_str[:2]}/{quote(image_name)}"
    return url


async def download_image(url: str, path: Path):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        with open(path, "wb") as f:
            f.write(response.content)


async def download_prts_images(image_names: list[str], output_folder: Path):
    tasks = []
    for image_name in image_names:
        url = get_prts_url(image_name)
        path = output_folder / image_name
        tasks.append(download_image(url, path))
    await asyncio.gather(*tasks)


async def main():
    output_folder = Path("resources")
    image_names = []
    image_names.extend(f"精英_{i}_大图.png" for i in range(3))
    image_names.extend(f"图标_职业_{profession}.png" for profession in PROFESSION_DICT.values())
    image_names.extend(f"稀有度_黄_{i}.png" for i in range(6))
    # image_names = [
    #     *(f"精英_{i}_大图.png" for i in range(3)),
    #     *(f"图标_职业_{profession}.png" for profession in PROFESSION_DICT.values()),
    #     *(f"稀有度_黄_{i}.png" for i in range(6)),
    # ]

    await download_prts_images(image_names, output_folder)


if __name__ == "__main__":
    asyncio.run(main())
