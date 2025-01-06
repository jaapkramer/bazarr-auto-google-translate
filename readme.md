# Bazarr Auto Google Translate

## Description
Bazarr Auto Google Translate is a Python script that automates the process of translating subtitles for TV shows using the Google Translate feature of Bazarr.

It's a small script that I've used to automatically translate subtitles for my TV shows from English to Dutch where no Dutch subtitles were available. This script does not use any LLM model or any other advanced translation method, but simply uses the Google Translate feature of Bazarr. 

## Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/bazarr-auto-google-translate.git
    cd bazarr-auto-google-translate
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your Bazarr API key and base URL:
    ```plaintext
    BAZARR_API_KEY=your_api_key
    BAZARR_BASE_URL=http://your-bazarr-url-including-port
    ```

## Usage
Run the script to translate subtitles:
```sh
python bazarr_translate.py
```

## Variables

You can modify the following variables in the main function of `bazarr_translate.py` to customize the translation:  
* `target_language`: The target language to translate the subtitles to (default is 'nl' for Dutch).
* `series_id`: The series ID of the show you want to translate, or set to None to translate all shows.
* `episode_id`: The episode ID of the show you want to translate, or set to None to translate all episodes.

Example: Translating a specific episode of a show:
```python
target_language = 'nl' 
series_id = 1 
episode_id = 456 
```
Example: Translating all episodes of a show:
```python
target_language = 'nl' 
series_id = 1 
episode_id = None 
```
Example: Translating all episodes of all shows:
```python
target_language = 'nl' 
series_id = None
episode_id = None 
```
