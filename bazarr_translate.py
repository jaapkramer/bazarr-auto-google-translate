import json
import requests
from dotenv import load_dotenv
import os
from tqdm import tqdm
import logging
from typing import List, Dict, Optional, Any

load_dotenv()

API_KEY = os.getenv("BAZARR_API_KEY")
BASE_URL = os.getenv("BAZARR_BASE_URL")

if not API_KEY or not BASE_URL:
    raise ValueError("API_KEY and BASE_URL must be set in the environment variables")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

session = requests.Session()
session.headers.update({
    "X-API-KEY": API_KEY,
    "Content-Type": "application/json"
})


def make_request(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Makes a GET request to the specified URL with optional parameters.

    :param url: The URL to make the request to.
    :param params: Optional parameters to include in the request.
    :return: The JSON response as a dictionary, or None if an error occurs.
    """
    response = None
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        logging.error(f"HTTP Error occurred: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error occurred while making the request: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"JSON decode error: {e}")
        if response:
            logging.error(f"Response content: {response.content}")
    return None


def get_wanted_subtitles(series_id: Optional[int] = None, episode_id: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Retrieves the list of wanted subtitles.

    :param series_id: Optional series ID to filter the subtitles.
    :param episode_id: Optional episode ID to filter the subtitles.
    :return: A list of dictionaries containing subtitle information.
    """
    url = f"{BASE_URL}/api/episodes/wanted"
    subtitles = make_request(url)
    if subtitles and isinstance(subtitles, dict) and "data" in subtitles:
        return [
            {
                "sonarrSeriesId": subtitle['sonarrSeriesId'],
                "sonarrEpisodeId": subtitle['sonarrEpisodeId'],
                "missing_language": missing_subtitle['name']
            }
            for subtitle in subtitles["data"]
            if "missing_subtitles" in subtitle and
               (series_id is None or subtitle['sonarrSeriesId'] == series_id) and
               (episode_id is None or subtitle['sonarrEpisodeId'] == episode_id)
            for missing_subtitle in subtitle["missing_subtitles"]
        ]
    logging.warning("Unexpected response format: %s", subtitles)
    return []


def get_episode(series_id: int, episode_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves information about a specific episode.

    :param series_id: The series ID of the episode.
    :param episode_id: The episode ID.
    :return: A dictionary containing episode information, or None if an error occurs.
    """
    url = f"{BASE_URL}/api/episodes"
    params = {
        "seriesid[]": series_id,
        "episodeid[]": episode_id
    }
    return make_request(url, params)


def process_subtitles(wanted_subtitles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes the list of wanted subtitles to retrieve detailed information including the path of the existing English subtitle

    :param wanted_subtitles: A list of dictionaries containing wanted subtitle information.
    :return: A list of dictionaries containing detailed subtitle information.
    """
    result = []
    for subtitle in tqdm(wanted_subtitles, desc="Processing subtitles"):
        series_id = subtitle["sonarrSeriesId"]
        episode_id = subtitle["sonarrEpisodeId"]
        episode_data = get_episode(series_id, episode_id)
        if episode_data and "data" in episode_data and len(episode_data["data"]) > 0:
            episode_info = episode_data["data"][0]
            if "subtitles" in episode_info:
                result.extend(
                    {
                        "seriesid": series_id,
                        "episodeid": episode_id,
                        "title": episode_info["title"],
                        "episode": episode_info["episode"],
                        "path": sub.get('path')
                    }
                    for sub in episode_info["subtitles"]
                    if sub.get("name") == "English"
                )
    return result


def translate_subtitles(subtitles_info: List[Dict[str, Any]], target_language: str = "nl") -> None:
    """
    Translates the subtitles to the target language.

    :param subtitles_info: A list of dictionaries containing subtitle information.
    :param target_language: The target language for translation.
    """
    response = None
    for subtitle in tqdm(subtitles_info, desc="Translating subtitles"):
        subs_path = subtitle["path"]
        sonarrepisodeid = subtitle["episodeid"]
        sonarrepisode = subtitle["episode"]
        url = f"{BASE_URL}/api/subtitles?action=translate&language={target_language}&path={subs_path}&type=episode&id={sonarrepisodeid}&forced=false&hi=false&original_format=true"
        try:
            response = session.patch(url)
            response.raise_for_status()
            if response.status_code == 204:
                logging.info(f"Translated subtitle for episode: {sonarrepisode} with id: {sonarrepisodeid}")
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTP Error occurred: {e}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while making the request: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"JSON decode error: {e}")
            if response:
                logging.error(f"Response content: {response.content}")


def main() -> None:
    """
    Main function to execute the subtitle translation process.
    """
    target_language = 'nl'  # The target language to translate the subtitles to
    series_id = None  # The series id of the show you want to translate, or set to None to translate all shows
    episode_id = None  # The episode id of the show you want to translate, or set to None to translate all episodes

    wanted_subtitles = get_wanted_subtitles(series_id, episode_id)
    subtitles_info = process_subtitles(wanted_subtitles)
    translate_subtitles(subtitles_info, target_language)


if __name__ == "__main__":
    main()
