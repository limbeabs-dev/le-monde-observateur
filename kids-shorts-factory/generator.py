import os
import random
import requests
import subprocess
from pathlib import Path

PEXELS_API_KEY = os.environ["PEXELS_API_KEY"].strip()

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

SEARCHES = [
    "cute cat",
    "cute dog",
    "cute rabbit",
    "funny animals",
    "kids animals"
]

def search_pexels(query, per_page=10):
    url = "https://api.pexels.com/videos/search"

    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": query,
        "per_page": per_page,
        "orientation": "portrait"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["videos"]


def choose_video(videos):
    usable = []

    for video in videos:
        files = video.get("video_files", [])

        for file in files:
            width = file.get("width")
            height = file.get("height")
            link = file.get("link")

            if not link or not width or not height:
                continue

            if height >= width:
                usable.append(file)

    if not usable:
        return None

    return random.choice(usable)


def download_video(url, destination):
    response = requests.get(url, stream=True, timeout=60)
    response.raise_for_status()

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)


def create_test_video():
    query = random.choice(SEARCHES)

    print(f"Recherche Pexels : {query}")

    videos = search_pexels(query)

    if not videos:
        raise RuntimeError("Aucune vidéo trouvée.")

    selected = choose_video(videos)

    if not selected:
        raise RuntimeError("Aucune vidéo verticale exploitable.")

    source = OUTPUT_DIR / "source.mp4"
    final = OUTPUT_DIR / "kids_short.mp4"

    print("Téléchargement de la vidéo...")

    download_video(
        selected["link"],
        source
    )

    print("Création du Short...")

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-t",
        "15",
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "23",
        "-an",
        str(final)
    ]

    subprocess.run(
        command,
        check=True
    )

    print(f"Short créé : {final}")


if __name__ == "__main__":
    create_test_video()
