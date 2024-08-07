import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox, ttk, Listbox, Scrollbar
import vlc
from youtubesearchpython import VideosSearch
import os
import yt_dlp
import threading
import time
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from urllib.parse import urlparse, parse_qs
import json
from pytube import YouTube

# Set the VLC path
vlc_path = r'C:\Program Files\VideoLAN\VLC\libvlc.dll' or r'C:\Program Files (x86)\VideoLAN\VLC\libvlc.dll' # Update this path to your VLC installation path
os.add_dll_directory(os.path.dirname(vlc_path))
vlc_instance = vlc.Instance()

# Global variables
player = None
current_url = None
playlist = []
current_index = 0
progress_updating = False
current_genre = None
played_songs = set()
visualizer_running = False
search_cancel_event = threading.Event()
playlists = {}  # Dictionary to store playlists
playlist_file = "playlists.json"  # File to save playlists
next_player = None  # Player for pre-loading the next song
favorites = []  # List to store favorite songs
favorites_file = "favorites_playlist.txt"  # File to store favorite songs
preloaded_next_song = False  # Initialize the flag for preloading the next song
documents_path = os.path.expanduser("~/Documents")
full_path = os.path.join(documents_path, favorites_file)
full_playlist_path = os.path.join(documents_path, playlist_file)
shuffle_mode = False

root = tk.Tk()
root.title("SYMPLIFY Music Player")
root.geometry("700x1100")
root.configure(bg="black")

def set_volume(volume_level):
    """
    Set the volume of the VLC player.

    Args:
    - volume_level (int): The volume level to set (0 to 100).
    """
    global player
    if player:
        # Ensure volume level is within the valid range
        volume_level = max(0, min(volume_level, 100))
        player.audio_set_volume(volume_level)
        print(f"Volume set to {volume_level}%")
    else:
        print("Player is not initialized.")

def toggle_shuffle():
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    shuffle_button.config(bg="blue" if shuffle_mode else "black")
    print("Shuffle mode is now", "ON" if shuffle_mode else "OFF")
def update_volume(val):
    """
    Update the volume based on slider input.

    Args:
    - val (str): The value from the slider (as a string).
    """
    volume_level = int(val)
    set_volume(volume_level)

def load_playlists():
    global playlists
    if os.path.exists(full_playlist_path):
        with open(full_playlist_path, "r") as file:
            playlists = json.load(file)

def save_playlists():
    with open(full_playlist_path, "w") as file:
        json.dump(playlists, file)

# Custom input dialog to set font size
class CustomInputDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Enter the music genre:", font=("Helvetica", 25)).pack(pady=10)
        self.entry = tk.Entry(master, font=("Helvetica", 25))
        self.entry.pack(pady=10)
        return self.entry

    def apply(self):
        self.result = self.entry.get()

# Custom input dialog to name the playlist
class PlaylistNameDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.result = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text="Enter the playlist name:", font=("Helvetica", 25)).pack(pady=10)
        self.entry = tk.Entry(master, font=("Helvetica", 25))
        self.entry.pack(pady=10)
        return self.entry

    def apply(self):
        self.result = self.entry.get()

# Function to extract audio URL using yt-dlp
def get_audio_url(video_url):
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': 'in_playlist',
        'force_generic_extractor': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        audio_url = info_dict['url']
        return audio_url



def perform_search(genre):
    # Simulate a search function
    # Replace this with your actual search logic
    genre = genre.lower()
    if genre == "hip hop":
        return ["song1_url", "song2_url"]
    elif genre == "deep house":
        return ["song3_url", "song4_url"]
    else:
        return []  # Return an empty list if no results are found

def search_music_by_genre(genre):
    results = perform_search(genre)
    if results is None:
        print("perform_search returned None")
        return []
    return results

def find_and_play_similar_track(genre):
    # Simulate a search function for similar tracks
    # Replace this with your actual search logic
    genre = genre.lower()
    if genre == "hip hop":
        return ["similar_song1_url", "similar_song2_url"]
    elif genre == "deep house":
        return ["similar_song3_url", "similar_song4_url"]
    else:
        return []  # Return an empty list if no results are found

def search_similar_track_by_genre(genre):
    results = find_and_play_similar_track(genre)
    if results is None:
        print("find_and_play_similar_track returned None")
        return []
    return results

def find_another_playlist(genre):
    # Simulate a search function for another playlist
    # Replace this with your actual search logic
    genre = genre.lower()
    if genre == "hip hop":
        return ["playlist1_song1_url", "playlist1_song2_url"]
    elif genre == "deep house":
        return ["playlist2_song1_url", "playlist2_song2_url"]
    else:
        return []  # Return an empty list if no results are found


def save_as_favorite():
    global marquee_text, playlist, favorites, favorites_listbox

    try:
        # Extract the title from marquee_text
        if marquee_text.startswith("Playing: "):
            song_title = marquee_text[len("Playing: "):]

            # Find the URL for the current song based on title
            for url in playlist:
                if get_video_title(url) == song_title:
                    current_url = url
                    break
            else:
                # If no URL is found, use the current URL if available
                if current_url and current_url not in favorites:
                    current_url = current_url
                else:
                    print("Current song is not in the playlist or already a favorite.")
                    return

            if current_url not in favorites:
                favorites.append(current_url)
                favorites_listbox.insert(tk.END, song_title)
                save_favorites_to_file()
                print(f"Saved as favorite: {current_url}")
            else:
                print("Song is already saved as a favorite.")
        else:
            print("No song title available in marquee_text.")
    except Exception as e:
        print(f"Exception in save_as_favorite: {e}")


def is_music_video(video):
    # Define keywords that are typically found in music videos
    music_keywords = ['music', 'official', 'audio', 'lyrics', 'remix', 'cover']
    title = video.get('title', '').lower()
    description_snippets = video.get('descriptionSnippet', [])

    # Combine all description snippets into a single string
    description = ' '.join([snippet['text'] for snippet in description_snippets if 'text' in snippet]).lower()

    # Check if the video duration is less than 10 minutes (600 seconds) and contains music keywords
    if any(keyword in title for keyword in music_keywords) or any(keyword in description for keyword in music_keywords):
        return True
    return False


def find_and_play_similar_track_thread(genre):
    global current_url, playlist, current_index, played_songs

    exclude_keywords = [
        'jazz chizm', 'how to', 'reaction', 'review', 'tutorial', 'guide', 'lesson', 'tour',
        'explained', 'tips', 'beginners', 'introduction', 'unboxing', 'first impression',
        'thoughts', 'news', 'discussion', 'talk', 'debate', 'podcast', 'interview',
        'panel', 'live', 'performance', 'concert', 'cover', 'acoustic', 'vlog', 'diary',
        'story', 'journey', 'daily', 'weekend', 'vacation', 'holiday', 'recap', 'summary',
        'compilation', 'highlight', 'course', 'learning', 'practice', 'masterclass', 'opinion', 'critique',
        'analysis', 'commentary', 'forum', 'report', 'broadcast', 'rendition', 'version',
        'showcase', 'behind the scenes', 'making of', 'parody', 'skit', 'funny', 'humor',
        'meme', 'trailer', 'promo', 'teaser', 'announcement', 'sneak peek', 'featurette',
        'comparison', 'experiment', 'challenge', 'reaction', 'analysis', 'documentary',
        'webinar', 'stream', 'gameplay', 'walkthrough', 'playthrough', 'speedrun',
        'achievement', 'highlight reel', 'montage', 'game review', 'hardware review',
        'software review', 'unboxing', 'setup', 'installation', 'configuration',
        'calibration', 'tips and tricks', 'troubleshooting', 'fix', 'repair', 'maintenance',
        'vlogmas', 'haul', 'outfit of the day', 'get ready with me', 'routine', 'diet',
        'nutrition', 'fitness', 'exercise', 'workout', 'yoga', 'meditation', 'mindfulness',
        'self-help', 'motivational', 'inspirational', 'success', 'goal setting',
        'productivity', 'life hack', 'DIY', 'craft', 'homemade', 'home improvement',
        'garden', 'landscaping', 'cooking', 'recipe', 'baking', 'meal prep', 'food review',
        'mukbang', 'eating show', 'taste test', 'cuisine', 'travel', 'destination',
        'trip', 'tour', 'exploration', 'adventure', 'cruise', 'road trip', 'camping',
        'hiking', 'backpacking', 'gear review', 'tech review', 'app review', 'book review',
        'movie review', 'film critique', 'tv show review', 'reaction video', 'live reaction',
        'response video', 'analysis video', 'breakdown', 'deep dive', 'expose', 'scandal',
        'drama', 'controversy', 'rant', 'op-ed', 'editorial', 'commentary video', 'hot take',
        'trend', 'viral video', 'challenge video', 'prank', 'joke', 'comedy skit',
        'stand-up', 'improv', 'magic trick', 'illusion', 'behind the scenes', 'making of',
        'director’s cut', 'alternate ending', 'bloopers', 'outtakes', 'deleted scenes',
        'cast interview', 'crew interview', 'Q&A', 'fan theories', 'speculation', 'spoiler',
        'prediction', 'review roundup', 'discussion panel', 'live stream', 'gaming',
        'ESports', 'walkthrough', 'playthrough', 'lets play', 'speedrun', 'tournament', 'match', 'game highlight',
        'sports highlight', 'ESports commentary', 'game review',
        'patch notes', 'game update', 'developer interview', 'game announcement',
        'trailer analysis', 'cinematic', 'cutscene', 'gameplay', 'beta test', 'alpha test',
        'pre-order', 'collector’s edition', 'special edition', 'unboxing', 'merchandise',
        'swag', 'fan meetup', 'cosplay', 'fan art', 'fan fiction', 'shipping', 'ship',
        'fandom', 'community', 'event coverage', 'expo', 'convention', 'trade show',
        'behind the scenes', 'making of', 'director’s commentary', 'producer’s commentary',
        'casting', 'audition', 'rehearsal', 'script read', 'table read', 'script analysis',
        'character analysis', 'plot breakdown', 'world-building', 'lore', 'timeline',
        'easter egg', 'reference', 'in-joke', 'meme', 'gif', 'fan edit', 'compilation',
        'supercut', 'highlight reel', 'best moments', 'top 10', 'ranking', 'tier list',
        'reaction', 'commentary', 'first impression', 'early access', 'preview', 'spoiler',
        'speculation', 'rumor', 'leak', 'teaser', 'promo', 'announcement', 'sneak peek',
        'update', 'patch', 'dlc', 'expansion', 'mod', 'custom content', 'user-generated content',
        'tutorial', 'how to', 'guide', 'walkthrough', 'playthrough', 'tips', 'tricks',
        'cheats', 'hacks', 'glitch', 'exploit', 'speedrun', 'challenge', 'competition',
        'match', 'tournament', 'event', 'livestream', 'replay', 'vod', 'recap', 'highlight',
        'montage', 'satire', 'skit', 'comedy', 'funny', 'joke', 'prank', 'challenge',
        'reaction', 'review', 'unboxing', 'haul', 'vlog', 'daily vlog', 'weekly vlog',
        'travel vlog', 'diary', 'journal', 'story', 'life update', 'routine', 'morning routine',
        'night routine', 'day in the life', 'week in the life', 'monthly favorites',
        'yearly favorites', 'product review', 'book review', 'movie review', 'tv show review',
        'album review', 'song review', 'game review', 'app review', 'tech review', 'device review',
        'software review', 'hardware review', 'food review', 'restaurant review', 'taste test',
        'mukbang', 'eating show', 'recipe', 'cooking', 'baking', 'meal prep', 'what I eat in a day',
        'fitness', 'workout', 'exercise', 'gym', 'home workout', 'yoga', 'pilates', 'meditation',
        'mindfulness', 'self-care', 'self-help', 'motivation', 'inspiration', 'success', 'productivity',
        'study', 'work', 'organization', 'planner', 'bullet journal', 'stationery', 'school supplies',
        'office supplies', 'desk setup', 'workspace', 'home office', 'remote work', 'telecommute',
        'freelance', 'entrepreneur', 'business', 'startup', 'side hustle', 'money', 'finance',
        'investment', 'stock market', 'cryptocurrency', 'real estate', 'budget', 'saving', 'frugal',
        'minimalism', 'declutter', 'organization', 'cleaning', 'housekeeping', 'home improvement',
        'DIY', 'craft', 'project', 'renovation', 'decoration', 'home tour', 'room tour', 'apartment tour',
        'house tour', 'garden', 'backyard', 'outdoor', 'nature', 'travel', 'adventure', 'vacation',
        'trip', 'road trip', 'hiking', 'camping', 'backpacking', 'gear', 'equipment', 'review',
        'unboxing', 'first impression', 'setup', 'installation', 'configuration', 'calibration',
        'troubleshooting', 'fix', 'repair', 'maintenance', 'vlogmas', 'vlogtober', 'vlogember', 'vloguary',
        'vloguary', 'date idea'
    ]

    include_keywords = [
        'music', 'song', 'track', 'mix', 'remix', 'dj', 'instrumental', 'cover', 'live', 'concert',
        'performance', 'band', 'artist', 'singer', 'rapper', 'musician', 'album', 'playlist', 'single',
        'dance', 'beat', 'r&b', 'pop', 'rock', 'hip hop', 'jazz', 'blues', 'classical', 'country', 'folk',
        'electronic', 'techno', 'house', 'dubstep', 'reggae', 'ska', 'punk', 'metal', 'grunge', 'indie',
        'alternative', 'soul', 'funk', 'disco', 'gospel', 'orchestral', 'symphonic', 'acoustic', 'ambient'
    ]

    try:
        if genre:
            print(f"Finding similar track for genre: {genre}")

            # Initialize variables for pagination
            offset = 0
            limit = 50
            new_results_found = False
            max_attempts = 5
            attempts = 0

            while attempts < max_attempts:
                # Fetch results with pagination
                videos_search = VideosSearch(genre, limit=limit, offset=offset)
                result = videos_search.result()

                if result and 'result' in result and result['result']:
                    results = result['result']
                    print(f"Search results fetched: {len(results)}")

                    if not new_results_found:
                        new_results_found = True

                    # Shuffle results for randomness
                    random.shuffle(results)

                    # Filter out previously played songs and non-music videos
                    filtered_results = [video for video in results if video['link'] not in played_songs and is_music_video(video)]

                    if filtered_results:
                        for video in filtered_results:
                            if (video['link'] not in played_songs and
                                    get_artist_name(video['link']) != get_artist_name(current_url) and
                                    get_video_duration(
                                        video['link']) <= 600):  # Only add videos that are 10 minutes or shorter

                                video_url = video['link']
                                print("Next similar track URL:", video_url)

                                # Add the new song to the playlist and update current_index
                                current_index = len(playlist) - 1
                                current_url = video_url

                                # Update the marquee and song display
                                marquee_text = f"Playing: {get_video_title(video_url)}"
                                update_marquee()

                                play_music()
                                return

                    # Increase offset for pagination and try again
                    offset += limit
                    attempts += 1
                else:
                    # No more results available or an error occurred
                    if not new_results_found:
                        print("No new tracks found.")
                        song_label.config(text="No similar tracks found.", fg="red")
                    break
        else:
            print("No genre specified to find similar tracks from.")
            song_label.config(text="No genre specified to find similar tracks from.", fg="red")
    except Exception as e:
        print(f"Exception in find_and_play_similar_track_thread: {e}")

# Function to search and play music from YouTube based on genre


def search_and_play_music_thread(genre, max_retries=5, retry_delay=2):
    global player, current_url, playlist, current_index, current_genre, played_songs
    current_genre = genre
    played_songs.clear()
    print(f"Searching for genre: {genre}")

    exclude_keywords = [
        'jazz chizm', 'how to', 'reaction', 'review', 'tutorial', 'guide', 'lesson',
        'explained', 'tips', 'beginners', 'introduction', 'unboxing', 'first impression',
        'thoughts', 'news', 'discussion', 'talk', 'debate', 'podcast', 'interview',
        'panel', 'live', 'performance', 'concert', 'cover', 'acoustic', 'vlog', 'diary',
        'story', 'journey', 'daily', 'weekend', 'vacation', 'holiday', 'recap', 'summary',
        'compilation', 'highlight', 'course', 'learning', 'practice', 'masterclass', 'opinion', 'critique',
        'analysis', 'commentary', 'forum', 'report', 'broadcast', 'rendition', 'version',
        'showcase', 'behind the scenes', 'making of', 'parody', 'skit', 'funny', 'humor',
        'meme', 'trailer', 'promo', 'teaser', 'announcement', 'sneak peek', 'featurette',
        'comparison', 'experiment', 'challenge', 'reaction', 'analysis', 'documentary',
        'webinar', 'stream', 'gameplay', 'walkthrough', 'playthrough', 'speedrun',
        'achievement', 'highlight reel', 'montage', 'game review', 'hardware review',
        'software review', 'unboxing', 'setup', 'installation', 'configuration',
        'calibration', 'tips and tricks', 'troubleshooting', 'fix', 'repair', 'maintenance',
        'vlogmas', 'haul', 'outfit of the day', 'get ready with me', 'routine', 'diet',
        'nutrition', 'fitness', 'exercise', 'workout', 'yoga', 'meditation', 'mindfulness',
        'self-help', 'motivational', 'inspirational', 'success', 'goal setting',
        'productivity', 'life hack', 'DIY', 'craft', 'homemade', 'home improvement',
        'garden', 'landscaping', 'cooking', 'recipe', 'baking', 'meal prep', 'food review',
        'mukbang', 'eating show', 'taste test', 'cuisine', 'travel', 'destination',
        'trip', 'tour', 'exploration', 'adventure', 'cruise', 'road trip', 'camping',
        'hiking', 'backpacking', 'gear review', 'tech review', 'app review', 'book review',
        'movie review', 'film critique', 'tv show review', 'reaction video', 'live reaction',
        'response video', 'analysis video', 'breakdown', 'deep dive', 'expose', 'scandal',
        'drama', 'controversy', 'rant', 'op-ed', 'editorial', 'commentary video', 'hot take',
        'trend', 'viral video', 'challenge video', 'prank', 'joke', 'comedy skit',
        'stand-up', 'improv', 'magic trick', 'illusion', 'behind the scenes', 'making of',
        'director’s cut', 'alternate ending', 'bloopers', 'outtakes', 'deleted scenes',
        'cast interview', 'crew interview', 'Q&A', 'fan theories', 'speculation', 'spoiler',
        'prediction', 'review roundup', 'discussion panel', 'live stream', 'gaming',
        'ESports', 'walkthrough', 'playthrough', 'lets play', 'speedrun', 'tournament', 'match', 'game highlight',
        'sports highlight', 'ESports commentary', 'game review',
        'patch notes', 'game update', 'developer interview', 'game announcement',
        'trailer analysis', 'cinematic', 'cutscene', 'gameplay', 'beta test', 'alpha test',
        'pre-order', 'collector’s edition', 'special edition', 'unboxing', 'merchandise',
        'swag', 'fan meetup', 'cosplay', 'fan art', 'fan fiction', 'shipping', 'ship',
        'fandom', 'community', 'event coverage', 'expo', 'convention', 'trade show',
        'behind the scenes', 'making of', 'director’s commentary', 'producer’s commentary',
        'casting', 'audition', 'rehearsal', 'script read', 'table read', 'script analysis',
        'character analysis', 'plot breakdown', 'world-building', 'lore', 'timeline',
        'easter egg', 'reference', 'in-joke', 'meme', 'gif', 'fan edit', 'compilation',
        'supercut', 'highlight reel', 'best moments', 'top 10', 'ranking', 'tier list',
        'reaction', 'commentary', 'first impression', 'early access', 'preview', 'spoiler',
        'speculation', 'rumor', 'leak', 'teaser', 'promo', 'announcement', 'sneak peek',
        'update', 'patch', 'dlc', 'expansion', 'mod', 'custom content', 'user-generated content',
        'tutorial', 'how to', 'guide', 'walkthrough', 'playthrough', 'tips', 'tricks',
        'cheats', 'hacks', 'glitch', 'exploit', 'speedrun', 'challenge', 'competition',
        'match', 'tournament', 'event', 'livestream', 'replay', 'vod', 'recap', 'highlight',
        'montage', 'satire', 'skit', 'comedy', 'funny', 'joke', 'prank', 'challenge',
        'reaction', 'review', 'unboxing', 'haul', 'vlog', 'daily vlog', 'weekly vlog',
        'travel vlog', 'diary', 'journal', 'story', 'life update', 'routine', 'morning routine',
        'night routine', 'day in the life', 'week in the life', 'monthly favorites',
        'yearly favorites', 'product review', 'book review', 'movie review', 'tv show review',
        'album review', 'song review', 'game review', 'app review', 'tech review', 'device review',
        'software review', 'hardware review', 'food review', 'restaurant review', 'taste test',
        'mukbang', 'eating show', 'recipe', 'cooking', 'baking', 'meal prep', 'what I eat in a day',
        'fitness', 'workout', 'exercise', 'gym', 'home workout', 'yoga', 'pilates', 'meditation',
        'mindfulness', 'self-care', 'self-help', 'motivation', 'inspiration', 'success', 'productivity',
        'study', 'work', 'organization', 'planner', 'bullet journal', 'stationery', 'school supplies',
        'office supplies', 'desk setup', 'workspace', 'home office', 'remote work', 'telecommute',
        'freelance', 'entrepreneur', 'business', 'startup', 'side hustle', 'money', 'finance',
        'investment', 'stock market', 'cryptocurrency', 'real estate', 'budget', 'saving', 'frugal',
        'minimalism', 'declutter', 'organization', 'cleaning', 'housekeeping', 'home improvement',
        'DIY', 'craft', 'project', 'renovation', 'decoration', 'home tour', 'room tour', 'apartment tour',
        'house tour', 'garden', 'backyard', 'outdoor', 'nature', 'travel', 'adventure', 'vacation',
        'trip', 'road trip', 'hiking', 'camping', 'backpacking', 'gear', 'equipment', 'review',
        'unboxing', 'first impression', 'setup', 'installation', 'configuration', 'calibration',
        'troubleshooting', 'fix', 'repair', 'maintenance', 'vlogmas', 'vlogtober', 'vlogember', 'vloguary',
        'vloguary', 'date idea'
    ]


    include_keywords = [
        'music', 'song', 'track', 'mix', 'remix', 'dj', 'instrumental', 'cover', 'live', 'concert',
        'performance', 'band', 'artist', 'singer', 'rapper', 'musician', 'album', 'playlist', 'single',
        'dance', 'beat', 'r&b', 'pop', 'rock', 'hip hop', 'jazz', 'blues', 'classical', 'country', 'folk',
        'electronic', 'techno', 'house', 'dubstep', 'reggae', 'ska', 'punk', 'metal', 'grunge', 'indie',
        'alternative', 'soul', 'funk', 'disco', 'gospel', 'orchestral', 'symphonic', 'acoustic', 'ambient'
    ]

    retries = 0
    while retries < max_retries:
        try:
            if genre:
                query = f"{genre} music"
                print(f"Searching with query: {query}")
                videos_search = VideosSearch(query, limit=50)  # Fetch more results to ensure variety
                result = videos_search.result()
                print(f"Search results: {result}")

                if result and isinstance(result, dict) and 'result' in result:
                    results_list = result['result']
                    if isinstance(results_list, list):
                        random.shuffle(results_list)  # Shuffle the results to add randomness
                        playlist.clear()

                        for video in results_list:
                            title = video.get('title', '').lower()
                            description = video.get('description', '').lower()
                            link = video.get('link', '')

                            # Filter out videos based on keywords
                            if any(keyword in title for keyword in exclude_keywords):
                                continue

                            # Check if video is likely to be music-related
                            if (any(keyword in title for keyword in include_keywords) or
                                    any(keyword in description for keyword in include_keywords)):

                                if (link not in played_songs and
                                        get_video_duration(
                                            link) <= 600):  # Only add videos that are 10 minutes or shorter
                                    playlist.append(link)
                                    played_songs.add(link)  # Mark this song as played
                                    print(f"Added to playlist: {link}")

                        if playlist:
                            current_index = 0
                            play_music()
                            return
                        else:
                            print("No suitable tracks found in this batch, retrying...")

                else:
                    print("Invalid result format, retrying...")

            else:
                print("No genre specified to find similar tracks from.")
                return

        except Exception as e:
            print(f"Exception during search or processing: {e}")

        retries += 1
        print(f"Retrying in {retry_delay} seconds...")
        time.sleep(retry_delay)  # Wait before retrying

    print("Failed to find suitable tracks after multiple attempts.")
    song_label.config(text="No suitable tracks found after multiple attempts.", fg="red")
    cancel_button.pack_forget()

def get_video_duration(url):
    # This function should return the duration of the video in seconds
    # Implement this according to your specific requirements
    return 0  # Placeholder

def play_music():
    # This function should handle playing music from the playlist
    # Implement this according to your specific requirements
    pass
def search_and_play_music():
    dialog = CustomInputDialog(root, title="Input")
    genre = dialog.result
    if genre:
        song_label.config(text="Searching...", fg="yellow")
        cancel_button.pack(pady=10)  # Show the cancel button
        search_cancel_event.clear()
        threading.Thread(target=search_and_play_music_thread, args=(genre,)).start()


# Function to cancel the search
def cancel_search():
    search_cancel_event.set()

# Function to search and play music from YouTube based on track name
def search_and_play_track():
    track_name = search_entry.get()
    if track_name:
        song_label.config(text="Searching...", fg="yellow")
        cancel_button.pack(pady=10)  # Show the cancel button
        search_cancel_event.clear()
        threading.Thread(target=search_and_play_track_thread, args=(track_name,)).start()

def search_and_play_track_thread(track_name):
    try:
        global player, current_url, playlist, current_index, current_genre, played_songs
        print(f"Searching for track: {track_name}")
        videos_search = VideosSearch(track_name, limit=50)
        result = videos_search.result()
        print(f"Search results: {result}")
        if result and 'result' in result and result['result']:
            video_url = result['result'][0]['link']
            current_genre = track_name  # Assume the track name represents the genre
            played_songs.clear()
            if get_video_duration(video_url) <= 600:  # Only add videos that are 10 minutes or shorter
                playlist.append(video_url)
                current_index = len(playlist) - 1
                play_music()
        else:
            song_label.config(text="No results found for the track.", fg="red")
    except Exception as e:
        print(f"Exception in search_and_play_track_thread: {e}")
    finally:
        cancel_button.pack_forget()  # Hide the cancel button


# Function to play music
def on_song_finished(event):
    global current_index, playlist, next_player, player, preloaded_next_song

    print("Song finished. Processing next song.")

    if next_player:
        # Switch to the preloaded player
        player = next_player
        next_player = None
        preloaded_next_song = None  # Clear preloaded flag
        player.play()


        # Update index and UI
        current_index += 1
        if current_index < len(playlist):
            video_url = playlist[current_index]
            marquee_text = f"Playing: {get_video_title(video_url)}"
            update_marquee()
            update_up_next_label()

        # Preload the next song
        pre_load_next_song()

    else:
        # No preloaded song, move to the next song in the playlist
        if current_index < len(playlist) - 1:
            current_index += 1
            play_music()
        else:
            # No more tracks in the playlist, find a similar track
            if playlist == favorites:
                print("No more tracks in the favorites playlist.")
            else:
                print("No more tracks in the playlist. Finding a similar track.")
                genre = search_entry.get()
                threading.Thread(target=find_and_play_similar_track_thread, args=(genre,)).start()

    # Ensure the UI is updated regardless of player state
    update_up_next_label()


def find_and_preload_similar_track_thread(genre, max_retries=5, retry_delay=2):
    global playlist, current_url, played_songs, next_player
    current_genre = genre
    played_songs = set()

    exclude_keywords = [
        'jazz chizm', 'how to', 'reaction', 'review', 'tutorial', 'guide', 'lesson',
        'explained', 'tips', 'beginners', 'introduction', 'unboxing', 'first impression',
        'thoughts', 'news', 'discussion', 'talk', 'debate', 'podcast', 'interview',
        'panel', 'live', 'performance', 'concert', 'cover', 'acoustic', 'vlog', 'diary',
        'story', 'journey', 'daily', 'weekend', 'vacation', 'holiday', 'recap', 'summary',
        'compilation', 'highlight', 'course', 'learning', 'practice', 'masterclass', 'opinion', 'critique',
        'analysis', 'commentary', 'forum', 'report', 'broadcast', 'rendition', 'version',
        'showcase', 'behind the scenes', 'making of', 'parody', 'skit', 'funny', 'humor',
        'meme', 'trailer', 'promo', 'teaser', 'announcement', 'sneak peek', 'featurette',
        'comparison', 'experiment', 'challenge', 'reaction', 'analysis', 'documentary',
        'webinar', 'stream', 'gameplay', 'walkthrough', 'playthrough', 'speedrun',
        'achievement', 'highlight reel', 'montage', 'game review', 'hardware review',
        'software review', 'unboxing', 'setup', 'installation', 'configuration',
        'calibration', 'tips and tricks', 'troubleshooting', 'fix', 'repair', 'maintenance',
        'vlogmas', 'haul', 'outfit of the day', 'get ready with me', 'routine', 'diet',
        'nutrition', 'fitness', 'exercise', 'workout', 'yoga', 'meditation', 'mindfulness',
        'self-help', 'motivational', 'inspirational', 'success', 'goal setting',
        'productivity', 'life hack', 'DIY', 'craft', 'homemade', 'home improvement',
        'garden', 'landscaping', 'cooking', 'recipe', 'baking', 'meal prep', 'food review',
        'mukbang', 'eating show', 'taste test', 'cuisine', 'travel', 'destination',
        'trip', 'tour', 'exploration', 'adventure', 'cruise', 'road trip', 'camping',
        'hiking', 'backpacking', 'gear review', 'tech review', 'app review', 'book review',
        'movie review', 'film critique', 'tv show review', 'reaction video', 'live reaction',
        'response video', 'analysis video', 'breakdown', 'deep dive', 'expose', 'scandal',
        'drama', 'controversy', 'rant', 'op-ed', 'editorial', 'commentary video', 'hot take',
        'trend', 'viral video', 'challenge video', 'prank', 'joke', 'comedy skit',
        'stand-up', 'improv', 'magic trick', 'illusion', 'behind the scenes', 'making of',
        'director’s cut', 'alternate ending', 'bloopers', 'outtakes', 'deleted scenes',
        'cast interview', 'crew interview', 'Q&A', 'fan theories', 'speculation', 'spoiler',
        'prediction', 'review roundup', 'discussion panel', 'live stream', 'gaming',
        'ESports', 'walkthrough', 'playthrough', 'lets play', 'speedrun', 'tournament', 'match', 'game highlight',
        'sports highlight', 'ESports commentary', 'game review',
        'patch notes', 'game update', 'developer interview', 'game announcement',
        'trailer analysis', 'cinematic', 'cutscene', 'gameplay', 'beta test', 'alpha test',
        'pre-order', 'collector’s edition', 'special edition', 'unboxing', 'merchandise',
        'swag', 'fan meetup', 'cosplay', 'fan art', 'fan fiction', 'shipping', 'ship',
        'fandom', 'community', 'event coverage', 'expo', 'convention', 'trade show',
        'behind the scenes', 'making of', 'director’s commentary', 'producer’s commentary',
        'casting', 'audition', 'rehearsal', 'script read', 'table read', 'script analysis',
        'character analysis', 'plot breakdown', 'world-building', 'lore', 'timeline',
        'easter egg', 'reference', 'in-joke', 'meme', 'gif', 'fan edit', 'compilation',
        'supercut', 'highlight reel', 'best moments', 'top 10', 'ranking', 'tier list',
        'reaction', 'commentary', 'first impression', 'early access', 'preview', 'spoiler',
        'speculation', 'rumor', 'leak', 'teaser', 'promo', 'announcement', 'sneak peek',
        'update', 'patch', 'dlc', 'expansion', 'mod', 'custom content', 'user-generated content',
        'tutorial', 'how to', 'guide', 'walkthrough', 'playthrough', 'tips', 'tricks',
        'cheats', 'hacks', 'glitch', 'exploit', 'speedrun', 'challenge', 'competition',
        'match', 'tournament', 'event', 'livestream', 'replay', 'vod', 'recap', 'highlight',
        'montage', 'satire', 'skit', 'comedy', 'funny', 'joke', 'prank', 'challenge',
        'reaction', 'review', 'unboxing', 'haul', 'vlog', 'daily vlog', 'weekly vlog',
        'travel vlog', 'diary', 'journal', 'story', 'life update', 'routine', 'morning routine',
        'night routine', 'day in the life', 'week in the life', 'monthly favorites',
        'yearly favorites', 'product review', 'book review', 'movie review', 'tv show review',
        'album review', 'song review', 'game review', 'app review', 'tech review', 'device review',
        'software review', 'hardware review', 'food review', 'restaurant review', 'taste test',
        'mukbang', 'eating show', 'recipe', 'cooking', 'baking', 'meal prep', 'what I eat in a day',
        'fitness', 'workout', 'exercise', 'gym', 'home workout', 'yoga', 'pilates', 'meditation',
        'mindfulness', 'self-care', 'self-help', 'motivation', 'inspiration', 'success', 'productivity',
        'study', 'work', 'organization', 'planner', 'bullet journal', 'stationery', 'school supplies',
        'office supplies', 'desk setup', 'workspace', 'home office', 'remote work', 'telecommute',
        'freelance', 'entrepreneur', 'business', 'startup', 'side hustle', 'money', 'finance',
        'investment', 'stock market', 'cryptocurrency', 'real estate', 'budget', 'saving', 'frugal',
        'minimalism', 'declutter', 'organization', 'cleaning', 'housekeeping', 'home improvement',
        'DIY', 'craft', 'project', 'renovation', 'decoration', 'home tour', 'room tour', 'apartment tour',
        'house tour', 'garden', 'backyard', 'outdoor', 'nature', 'travel', 'adventure', 'vacation',
        'trip', 'road trip', 'hiking', 'camping', 'backpacking', 'gear', 'equipment', 'review',
        'unboxing', 'first impression', 'setup', 'installation', 'configuration', 'calibration',
        'troubleshooting', 'fix', 'repair', 'maintenance', 'vlogmas', 'vlogtober', 'vlogember', 'vloguary',
        'vloguary', 'date idea'
    ]


    retries = 0
    while retries < max_retries:
        try:
            if genre:
                print(f"Finding similar track for genre: {genre}")

                try:
                    videos_search = VideosSearch(genre, limit=50)  # Fetch more results to ensure variety
                    result = videos_search.result()
                    print(f"Search results: {result}")

                    if result and isinstance(result, dict) and 'result' in result and result['result']:
                        results_list = result['result']
                        random.shuffle(results_list)  # Shuffle the results to add randomness

                        # Track the current batch of results to avoid re-selecting the same song
                        seen_tracks = set()

                        for video in results_list:
                            video_url = video.get('link', '')
                            if video_url in seen_tracks or video_url in played_songs:
                                continue

                            if (get_artist_name(video_url) != get_artist_name(current_url) and
                                    get_video_duration(video_url) <= 600):  # Only consider videos 10 minutes or shorter
                                seen_tracks.add(video_url)  # Track this URL in this batch

                                print("Pre-loading similar track URL:", video_url)

                                # Preload this track
                                parsed_url = urlparse(video_url)
                                if parsed_url.scheme in ('http', 'https'):
                                    try:
                                        next_audio_url = get_audio_url(video_url)
                                    except Exception as e:
                                        print(f"Error getting audio URL: {e}")
                                        next_audio_url = video_url  # Fallback to the original URL
                                else:
                                    next_audio_url = video_url  # Assume it's a local file path

                                try:
                                    next_player = vlc.Instance().media_player_new()
                                    next_media = vlc.Instance().media_new(next_audio_url)
                                    next_player.set_media(next_media)
                                    print(f"Pre-loaded similar track URL: {video_url}")

                                    playlist.append(video_url)  # Add the new song to the playlist
                                    played_songs.add(video_url)  # Mark this song as played

                                    # Update the "Up Next" label
                                    update_up_next_label()
                                    return  # Exit after successfully preloading

                                except Exception as e:
                                    print(f"Error preloading track: {e}")
                                    # Continue to the next video if there's an error preloading

                        print("No suitable similar tracks found in this batch, retrying...")

                    else:
                        print("No results found or invalid result format, retrying...")

                except Exception as e:
                    print(f"Error during search: {e}")

            else:
                print("No genre specified to find similar tracks from.")
                return

            retries += 1
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)  # Wait before retrying

        except Exception as e:
            print(f"Exception in find_and_preload_similar_track: {e}")

    print("Failed to find suitable similar tracks after multiple attempts.")

         # Use a set to track played songs



def play_music():
    global player, current_url, playlist, current_index, progress_updating, played_songs, visualizer_running, marquee_text, marquee_index, preloaded_next_song


    try:
        if player and player.get_state() == vlc.State.Paused:
            player.play()

        else:
            if playlist:
                video_url = playlist[current_index]
                print(f"Playing video URL: {video_url}")
                parsed_url = urlparse(video_url)
                if parsed_url.scheme in ('http', 'https'):
                    audio_url = get_audio_url(video_url)
                else:
                    audio_url = video_url  # Assume it's a local file path

                if player:
                    player.stop()

                player = vlc_instance.media_player_new()
                media = vlc_instance.media_new(audio_url)
                player.set_media(media)
                player.audio_set_volume(80)  # Ensure volume is set correctly
                player.play()
                player.event_manager().event_attach(vlc.EventType.MediaPlayerEndReached, on_song_finished)

                current_url = video_url
                played_songs.add(video_url)  # Ensure the current song is added to played_songs

                # Update the marquee and song display
                marquee_text = f"Playing: {get_video_title(video_url)}"
                marquee_index = 0
                update_marquee()
                progress_updating = True
                visualizer_running = True
                update_progress_meter()
                update_visualizer()
                update_up_next_label()

                pre_load_next_song()
                # If there is a preloaded track, handle it

            else:
                print("No more tracks in the playlist.")
                genre = current_genre
                threading.Thread(target=find_and_play_similar_track_thread,
                                 args=(genre,)).start()  # Attempt to find and play a similar track
    except Exception as e:
        print(f"Exception in play_music: {e}")

def pre_load_next_song():
    global next_player, playlist, current_index, preloaded_next_song, current_genre

    exclude_keywords = [
        'jazz chizm', 'how to', 'reaction', 'review', 'tutorial', 'guide', 'lesson',
        'explained', 'tips', 'beginners', 'introduction', 'unboxing', 'first impression',
        'thoughts', 'news', 'discussion', 'talk', 'debate', 'podcast', 'interview',
        'panel', 'live', 'performance', 'concert', 'cover', 'acoustic', 'vlog', 'diary',
        'story', 'journey', 'daily', 'weekend', 'vacation', 'holiday', 'recap', 'summary',
        'compilation', 'highlight', 'course', 'learning', 'practice', 'masterclass', 'opinion', 'critique',
        'analysis', 'commentary', 'forum', 'report', 'broadcast', 'rendition', 'version',
        'showcase', 'behind the scenes', 'making of', 'parody', 'skit', 'funny', 'humor',
        'meme', 'trailer', 'promo', 'teaser', 'announcement', 'sneak peek', 'featurette',
        'comparison', 'experiment', 'challenge', 'reaction', 'analysis', 'documentary',
        'webinar', 'stream', 'gameplay', 'walkthrough', 'playthrough', 'speedrun',
        'achievement', 'highlight reel', 'montage', 'game review', 'hardware review',
        'software review', 'unboxing', 'setup', 'installation', 'configuration',
        'calibration', 'tips and tricks', 'troubleshooting', 'fix', 'repair', 'maintenance',
        'vlogmas', 'haul', 'outfit of the day', 'get ready with me', 'routine', 'diet',
        'nutrition', 'fitness', 'exercise', 'workout', 'yoga', 'meditation', 'mindfulness',
        'self-help', 'motivational', 'inspirational', 'success', 'goal setting',
        'productivity', 'life hack', 'DIY', 'craft', 'homemade', 'home improvement',
        'garden', 'landscaping', 'cooking', 'recipe', 'baking', 'meal prep', 'food review',
        'mukbang', 'eating show', 'taste test', 'cuisine', 'travel', 'destination',
        'trip', 'tour', 'exploration', 'adventure', 'cruise', 'road trip', 'camping',
        'hiking', 'backpacking', 'gear review', 'tech review', 'app review', 'book review',
        'movie review', 'film critique', 'tv show review', 'reaction video', 'live reaction',
        'response video', 'analysis video', 'breakdown', 'deep dive', 'expose', 'scandal',
        'drama', 'controversy', 'rant', 'op-ed', 'editorial', 'commentary video', 'hot take',
        'trend', 'viral video', 'challenge video', 'prank', 'joke', 'comedy skit',
        'stand-up', 'improv', 'magic trick', 'illusion', 'behind the scenes', 'making of',
        'director’s cut', 'alternate ending', 'bloopers', 'outtakes', 'deleted scenes',
        'cast interview', 'crew interview', 'Q&A', 'fan theories', 'speculation', 'spoiler',
        'prediction', 'review roundup', 'discussion panel', 'live stream', 'gaming',
        'ESports', 'walkthrough', 'playthrough', 'lets play', 'speedrun', 'tournament', 'match', 'game highlight',
        'sports highlight', 'ESports commentary', 'game review',
        'patch notes', 'game update', 'developer interview', 'game announcement',
        'trailer analysis', 'cinematic', 'cutscene', 'gameplay', 'beta test', 'alpha test',
        'pre-order', 'collector’s edition', 'special edition', 'unboxing', 'merchandise',
        'swag', 'fan meetup', 'cosplay', 'fan art', 'fan fiction', 'shipping', 'ship',
        'fandom', 'community', 'event coverage', 'expo', 'convention', 'trade show',
        'behind the scenes', 'making of', 'director’s commentary', 'producer’s commentary',
        'casting', 'audition', 'rehearsal', 'script read', 'table read', 'script analysis',
        'character analysis', 'plot breakdown', 'world-building', 'lore', 'timeline',
        'easter egg', 'reference', 'in-joke', 'meme', 'gif', 'fan edit', 'compilation',
        'supercut', 'highlight reel', 'best moments', 'top 10', 'ranking', 'tier list',
        'reaction', 'commentary', 'first impression', 'early access', 'preview', 'spoiler',
        'speculation', 'rumor', 'leak', 'teaser', 'promo', 'announcement', 'sneak peek',
        'update', 'patch', 'dlc', 'expansion', 'mod', 'custom content', 'user-generated content',
        'tutorial', 'how to', 'guide', 'walkthrough', 'playthrough', 'tips', 'tricks',
        'cheats', 'hacks', 'glitch', 'exploit', 'speedrun', 'challenge', 'competition',
        'match', 'tournament', 'event', 'livestream', 'replay', 'vod', 'recap', 'highlight',
        'montage', 'satire', 'skit', 'comedy', 'funny', 'joke', 'prank', 'challenge',
        'reaction', 'review', 'unboxing', 'haul', 'vlog', 'daily vlog', 'weekly vlog',
        'travel vlog', 'diary', 'journal', 'story', 'life update', 'routine', 'morning routine',
        'night routine', 'day in the life', 'week in the life', 'monthly favorites',
        'yearly favorites', 'product review', 'book review', 'movie review', 'tv show review',
        'album review', 'song review', 'game review', 'app review', 'tech review', 'device review',
        'software review', 'hardware review', 'food review', 'restaurant review', 'taste test',
        'mukbang', 'eating show', 'recipe', 'cooking', 'baking', 'meal prep', 'what I eat in a day',
        'fitness', 'workout', 'exercise', 'gym', 'home workout', 'yoga', 'pilates', 'meditation',
        'mindfulness', 'self-care', 'self-help', 'motivation', 'inspiration', 'success', 'productivity',
        'study', 'work', 'organization', 'planner', 'bullet journal', 'stationery', 'school supplies',
        'office supplies', 'desk setup', 'workspace', 'home office', 'remote work', 'telecommute',
        'freelance', 'entrepreneur', 'business', 'startup', 'side hustle', 'money', 'finance',
        'investment', 'stock market', 'cryptocurrency', 'real estate', 'budget', 'saving', 'frugal',
        'minimalism', 'declutter', 'organization', 'cleaning', 'housekeeping', 'home improvement',
        'DIY', 'craft', 'project', 'renovation', 'decoration', 'home tour', 'room tour', 'apartment tour',
        'house tour', 'garden', 'backyard', 'outdoor', 'nature', 'travel', 'adventure', 'vacation',
        'trip', 'road trip', 'hiking', 'camping', 'backpacking', 'gear', 'equipment', 'review',
        'unboxing', 'first impression', 'setup', 'installation', 'configuration', 'calibration',
        'troubleshooting', 'fix', 'repair', 'maintenance', 'vlogmas', 'vlogtober', 'vlogember', 'vloguary',
        'vloguary', 'date idea'
    ]


    if current_index < len(playlist) - 1:
        next_index = current_index + 1
        next_video_url = playlist[next_index]
        parsed_url = urlparse(next_video_url)
        if parsed_url.scheme in ('http', 'https'):
            next_audio_url = get_audio_url(next_video_url)
        else:
            next_audio_url = next_video_url  # Assume it's a local file path

        next_player = vlc_instance.media_player_new()
        next_media = vlc_instance.media_new(next_audio_url)
        next_player.set_media(next_media)
        print(f"Pre-loaded next video URL: {next_video_url}")

        preloaded_next_song = True  # Set flag to indicate next song is preloaded

        # Update the "Up Next" label
        update_up_next_label()

    else:
        # No more tracks to pre-load, find a similar track
        print("No more songs to pre-load. Finding a similar track.")
        threading.Thread(target=find_and_preload_similar_track_thread, args=(current_genre,)).start()

def update_up_next_label():
    global playlist, current_index

    if current_index < len(playlist) - 1:
        next_index = current_index + 1
        next_video_url = playlist[next_index]
        next_video_title = get_video_title(next_video_url)
        # Assuming you have a label or similar UI element to show the up next information
        up_next_label.config(text=f"Up Next: {next_video_title}")
    else:
        up_next_label.config(text="Searching for next track...")


def search_next_song():
    global current_index, playlist
    if current_index < len(playlist) - 1:
        next_index = current_index + 1
        next_title = get_video_title(playlist[next_index])
        up_next_label.config(text=f"Up Next: {next_title}")
    else:
        up_next_label.config(text="Up Next: None")

# Function to get video title
def get_video_title(url):
    # Use pytube to get the video title from the URL
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme in ('http', 'https'):
            # Extract the video ID from the URL
            video_id = None
            if 'youtube.com' in parsed_url.netloc:
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get('v', [None])[0]
            elif 'youtu.be' in parsed_url.netloc:
                video_id = parsed_url.path.lstrip('/')

            if video_id:
                yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
                return yt.title
            else:
                return "Unknown Title"
        else:
            return os.path.splitext(os.path.basename(url))[0]  # Return the filename without extension for local files
    except Exception as e:
        print(f"Error fetching title for {url}: {e}")
        return os.path.splitext(os.path.basename(url))[0]  # Fallback to filename without extension if title fetch fails
# Function to get artist name
def get_artist_name(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        return info_dict['uploader']

# Function to get video duration in seconds
def get_video_duration(video_url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        return info_dict.get('duration', 0)  # Return 0 if 'duration' key is not present

# Function to pause music
def pause_music():
    global player, progress_updating, visualizer_running
    if player:
        player.pause()
        progress_updating = False
        visualizer_running = False


# Function to stop music
def stop_music():
    global player, progress_updating, visualizer_running
    if player:
        player.stop()
        song_label.config(text="Stopped", fg="green")
        progress_updating = False
        visualizer_running = False
        progress_meter.set(0)

# Function to skip to the next song in the playlist or find a similar track

def skip_music():
    global current_index, playlist, next_player, player, marquee_text, preloaded_next_song

    if next_player:
        player.stop()
        player = next_player
        player.play()
        next_player = None
        current_index += 1

        # Update the marquee and song display
        video_url = playlist[current_index]
        marquee_text = f"Playing: {get_video_title(video_url)}"
        marquee_index = 0
        update_marquee()
        update_up_next_label()

        # Preload the next song
        pre_load_next_song()
    else:
        if current_index < len(playlist) - 1:
            current_index += 1
            play_music()
        else:
            if playlist == favorites:
                print("No more tracks in the favorites playlist.")
            else:
                print("No more tracks in the playlist. Finding a similar track.")
                threading.Thread(target=find_and_preload_similar_track_thread, args=(current_genre,)).start()
# Function to find and play a similar track by a different artist
def find_and_play_similar_track():
    threading.Thread(target=find_and_play_similar_track_thread).start()



# Function to play local files
def play_local_file():
    global player, current_url, playlist, current_index
    file_path = filedialog.askopenfilename()
    if file_path:
        playlist.append(file_path)
        current_index = len(playlist) - 1
        play_music()

def delete_selected_track():
    global playlist, favorites, current_index
    selected_playlist_index = song_listbox.curselection()
    selected_favorites_index = favorites_listbox.curselection()

    if selected_playlist_index:
        selected_playlist_index = selected_playlist_index[0]
        del playlist[selected_playlist_index]
        song_listbox.delete(selected_playlist_index)
        if selected_playlist_index == current_index:
            stop_music()
            current_index = 0
            if playlist:
                play_music()
        elif selected_playlist_index < current_index:
            current_index -= 1

    if selected_favorites_index:
        selected_favorites_index = selected_favorites_index[0]
        del favorites[selected_favorites_index]
        favorites_listbox.delete(selected_favorites_index)
        save_favorites_to_file()

# Function to import playlist
def import_playlist():
    global playlists
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        dialog = PlaylistNameDialog(root, title="Name Playlist")
        playlist_name = dialog.result
        if playlist_name:
            playlists[playlist_name] = list(file_paths)
            save_playlists()
            update_playlist_dropdown()
            messagebox.showinfo("Success", f"Playlist '{playlist_name}' imported successfully!")

# Function to update the playlist dropdown menu
def update_playlist_dropdown():
    menu = playlist_dropdown["menu"]
    menu.delete(0, "end")
    for playlist_name in playlists:
        menu.add_command(label=playlist_name, command=lambda name=playlist_name: load_playlist(name))

# Function to load a selected playlist
def load_playlist(playlist_name):
    global playlist, current_index
    playlist = playlists[playlist_name]
    current_index = 0
    update_song_listbox()
    play_music()




# Function to update the song listbox
def update_song_listbox():
    song_listbox.delete(0, tk.END)
    for song in playlist:
        song_listbox.insert(tk.END, get_video_title(song))

# Function to update the progress meter
def update_progress_meter():
    global player, progress_updating
    if player and progress_updating:
        length = player.get_length() // 1000  # Length in seconds
        current_time = player.get_time() // 1000  # Current time in seconds
        if length > 0:
            progress_meter.config(to=length)
            progress_meter.set(current_time)
        root.after(1000, update_progress_meter)

# Function to seek to a specific time in the song
def seek(event):
    global player
    if player:
        seek_time = progress_meter.get() * 1000  # Convert to milliseconds
        player.set_time(seek_time)

# Function to update the visualizer
def update_visualizer():
    global visualizer_running
    if visualizer_running:
        data = np.random.rand(10)  # Replace with actual audio data if available
        for bar, height in zip(bars, data):
            bar.set_height(height)
        canvas.draw()
        root.after(100, update_visualizer)
# Function to update the marquee text
def update_marquee():
    global marquee_text, marquee_index

    if marquee_text:
        marquee_index += 1
        if marquee_index >= len(marquee_text):
            marquee_index = 0
        song_label.config(text=marquee_text[marquee_index:] + marquee_text[:marquee_index])
        song_label.after(200, update_marquee)  # Adjust the scrolling speed here



# Define font settings
font_settings = ("Helvetica", 15)

# Initialize the selected playlist variable after the root window is created
selected_playlist = tk.StringVar(root)
selected_playlist.set("Select a Playlist")  # Set a default value

# Add title label
title_label = tk.Label(root, text="SYMPLIFY MUSIC PLAYER", bg="black", fg="green", font=("Helvetica", 30, "bold"))
title_label.pack(pady=10)

input_frame_settings = ("Helvetica", 15)
input_frame = tk.Frame(root, bg="black")
input_frame.pack(pady=10)
# Add label above the input box
input_label = tk.Label(input_frame, text="TYPE SONG HERE:", bg="black", fg="green", font=font_settings)
input_label.pack(side="left", padx=5)

search_frame_settings = ("Helvetica", 15)
search_frame = tk.Frame(root, bg="black")
search_frame.pack(pady=10)

# Create and place buttons with padding and color
search_entry = tk.Entry(search_frame, bg="black", fg="green", font=font_settings)
search_entry.pack(pady=10)
button_font_settings = ("Helvetica", 15)
search_track_button = tk.Button(search_frame, text="Search and Play Track", command=search_and_play_track, bg="black", fg="blue", font=search_frame_settings)
search_track_button.pack(side="left", padx=5)

search_button = tk.Button(search_frame, text="Search and Play by Genre", command=search_and_play_music, bg="black", fg="blue", font=search_frame_settings)
search_button.pack(side="left", padx=5)

# Create a frame to hold the control buttons

import_frame_settings = ("Helvetica", 15)
import_frame = tk.Frame(root, bg="black")
import_frame.pack(pady=10)
import_playlist_button = tk.Button(import_frame, text="Import Playlist", command=import_playlist, bg="black", fg="blue", font=button_font_settings)
import_playlist_button.pack(side="left", padx=5)

playlist_font_settings = ("Helvetica", 15)
# Dropdown menu for previously imported playlists
playlist_dropdown = tk.OptionMenu(import_frame, selected_playlist, "Select a Playlist")
playlist_dropdown.config(bg="black", fg="green", font=playlist_font_settings)
playlist_dropdown["menu"].config(font=playlist_font_settings)  # Set the font for the dropdown options
playlist_dropdown.pack(side="left", padx=5)

# Define a smaller font for the playlist songs


# Listbox to show songs in the selected playlist with smaller size and text
song_listbox = tk.Listbox(root, bg="black", fg="green", font=playlist_font_settings, selectbackground="green", selectforeground="black", height=5, width=50)
song_listbox.pack(pady=10)

# Label to show the loaded song
song_label = tk.Label(root, text="No song loaded", bg="black", fg="green", font=font_settings)
song_label.pack(pady=10)

up_next_label = tk.Label(root, text="NEXT: None", bg="black", fg="green", font=font_settings)
up_next_label.pack(pady=10)
# Cancel button to cancel the search
cancel_button = tk.Button(root, text="Cancel Search", command=cancel_search, bg="black", fg="red", font=font_settings)
cancel_button.pack_forget()  # Hide the cancel button initially

# Progress meter
progress_meter = tk.Scale(root, from_=0, to=100, orient="horizontal", length=300, bg="black", fg="green", sliderrelief="flat", font=font_settings)
progress_meter.pack(pady=10)
progress_meter.bind("<ButtonRelease-1>", seek)

control_font_settings = ("Helvetica", 15)
control_frame = tk.Frame(root, bg="black")
control_frame.pack(pady=10)




play_button = tk.Button(control_frame, text="Play", command=play_music, bg="black", fg="green", font=control_font_settings)
play_button.pack(side="left", padx=5)

pause_button = tk.Button(control_frame, text="Pause", command=pause_music, bg="black", fg="green", font=control_font_settings)
pause_button.pack(side="left", padx=5)

stop_button = tk.Button(control_frame, text="Stop", command=stop_music, bg="black", fg="green", font=control_font_settings)
stop_button.pack(side="left", padx=5)

skip_button = tk.Button(control_frame, text="Skip", command=skip_music, bg="black", fg="green", font=control_font_settings)
skip_button.pack(side="left", padx=5)

favorite_button = tk.Button(control_frame, text="Save as Favorite", command=save_as_favorite, bg="black", fg="green", font=control_font_settings)
favorite_button.pack(side="left", padx=5)

delete_button = tk.Button(control_frame, text="Delete", command=delete_selected_track, bg="black", fg="red", font=control_font_settings)
delete_button.pack(side="left", padx=5)
shuffle_button = tk.Button(control_frame, text="Shuffle", command=toggle_shuffle, bg="black", fg="green", font="Helvetica 12 bold")
shuffle_button.pack(side="left", padx=5)

# Create the visualizer
fig, ax = plt.subplots(figsize=(4, 1), facecolor='black')
data = np.random.rand(10)
bars = ax.bar(range(len(data)), data, color='green')
ax.set_facecolor('black')
ax.tick_params(axis='x', colors='green')
ax.tick_params(axis='y', colors='green')
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(pady=10)

volume_slider = tk.Scale(root, from_=0, to=100, orient="horizontal", length=250, bg="black", fg="green", sliderrelief="flat", command=update_volume)
volume_slider.set(80)  # Set default volume level
volume_slider.pack()

favorites_label = tk.Label(root, text="FAVOURITES", bg="black", fg="green", font=font_settings)
favorites_label.pack(pady=10)

favorites_listbox = tk.Listbox(root, bg="black", fg="green", font=playlist_font_settings, selectbackground="green", selectforeground="black", height=5, width=50)
favorites_listbox.pack(pady=10)


def on_song_double_click(event):
    global current_index
    selection = event.widget.curselection()
    if selection:
        current_index = selection[0]
        play_music()


def save_favorites_to_file():
    # Construct the full file path
    full_path = os.path.join(documents_path, favorites_file)

    with open(full_path, "w") as f:
        for song in favorites:
            f.write(song + "\n")

def load_favorites_from_file():
    global favorites
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            favorites = [line.strip() for line in f.readlines()]
        for song in favorites:
            favorites_listbox.insert(tk.END, get_video_title(song))

def play_favorites():
    global playlist, current_index, played_songs
    if favorites:
        playlist = favorites.copy()
        current_index = 0
        played_songs = set()
        play_music()
        update_up_next_label()  # Update the "Up Next" label when playing favorites
    else:
        print("No favorite songs to play.")

def play_selected_favorite(event):
    global playlist, current_index, played_songs
    selected_index = favorites_listbox.curselection()
    if selected_index:
        selected_index = selected_index[0]
        selected_url = favorites[selected_index]
        playlist = favorites.copy()
        current_index = selected_index
        played_songs = set()
        play_music()
        update_up_next_label()  # Update the "Up Next" label when playing a selected favorite

def on_closing():
    save_playlists()  # Optionally save playlists or other state
    root.destroy()
    os._exit(0)


song_listbox.bind("<Double-Button-1>", on_song_double_click)
favorites_listbox.bind("<Double-Button-1>", play_selected_favorite)
# Load playlists on startup
load_playlists()
update_playlist_dropdown()
load_favorites_from_file()

buy_me_coffee_font_settings = ("Helvetica", 12)
def open_buy_me_coffee():
    import webbrowser
    webbrowser.open("https://www.buymeacoffee.com/pyninja")

buy_me_coffee_button = tk.Button(root, text="Made by PyNinja. Click here to buy me a coffee", command=open_buy_me_coffee, bg="black", fg="green", font=buy_me_coffee_font_settings)
buy_me_coffee_button.pack(pady=10)

root.protocol("WM_DELETE_WINDOW", on_closing)
# Run the application
root.mainloop()