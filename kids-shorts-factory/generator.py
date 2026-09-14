import os
import random
import requests
import subprocess
from pathlib import Path

PEXELS_API_KEY = "".join(os.environ["PEXELS_API_KEY"].split())

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

SEARCHES = [
    {
        "query": "cute cat",
        "titles": [
            "LE CHAT QUI CACHE UN SECRET 🐱",
            "TU AS VU CE QU'IL FAIT ? 😳",
            "LE CHAT LE PLUS CURIEUX DU MONDE"
        ]
    },
    {
        "query": "cute dog",
        "titles": [
            "CE CHIEN A UNE IDÉE 😂🐶",
            "IL A COMPRIS QUELQUE CHOSE...",
            "LE CHIEN LE PLUS MALIN ?"
        ]
    },
    {
        "query": "cute rabbit",
        "titles": [
            "CE PETIT LAPIN EST TROP CURIEUX 🐰",
            "REGARDE BIEN SES OREILLES 👀",
            "LE LAPIN QUI NE TIENT PAS EN PLACE"
        ]
    },
    {
        "query": "funny animals",
        "titles": [
            "ÇA NE S'EST PAS PASSÉ COMME PRÉVU 😂",
            "ATTENDS LA FIN 😳",
            "LE MOMENT LE PLUS DRÔLE"
        ]
    }
]


def search_pexels(query, per_page=15):
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

    return response.json().get("videos", [])


def choose_video(videos):
    usable = []

    for video in videos:
        for file in video.get("video_files", []):
            width = file.get("width")
            height = file.get("height")
            link = file.get("link")

            if not link or not width or not height:
                continue

            if height >= width and width >= 500:
                usable.append(file)

    if not usable:
        return None

    return random.choice(usable)


def download_video(url, destination):
    response = requests.get(
        url,
        stream=True,
        timeout=60
    )

    response.raise_for_status()

    with open(destination, "wb") as file:
        for chunk in response.iter_content(chunk_size=1024 * 1024):
            if chunk:
                file.write(chunk)


def create_short(source, final, title):
    safe_title = (
        title
        .replace("'", "")
        .replace(":", "")
        .replace("!", "")
        .replace("?", "")
        .replace("🐱", "")
        .replace("🐶", "")
        .replace("🐰", "")
        .replace("😂", "")
        .replace("😳", "")
        .replace("👀", "")
        .strip()
    )

    filter_text = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "drawbox=x=0:y=0:w=1080:h=260:color=black@0.45:t=fill,"
        "drawtext="
        "fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
        f"text='{safe_title}':"
        "fontcolor=white:"
        "fontsize=58:"
        "x=(w-text_w)/2:"
        "y=80:"
        "text_shaping=1"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(source),
        "-t",
        "15",
        "-vf",
        filter_text,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-an",
        str(final)
    ]

    subprocess.run(
        command,
        check=True
    )


def create_test_video():
    choice = random.choice(SEARCHES)

    query = choice["query"]
    title = random.choice(choice["titles"])

    print(f"Recherche Pexels : {query}")
    print(f"Titre choisi : {title}")

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

    create_short(
        source,
        final,
        title
    )

    print(f"Short créé : {final}")
    print("Génération terminée avec succès.")


if __name__ == "__main__":
    create_test_video()
