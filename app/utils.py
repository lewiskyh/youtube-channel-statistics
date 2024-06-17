import os
import googleapiclient.discovery
from urllib.error import HTTPError
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt
##Import Hiragino sans to display Japanese characters
import matplotlib

matplotlib.rcParams['font.family'] = 'Hiragino sans'

MAX_TITLE_LENGTH = 30
SPACE_FOR_DOTS = 3

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=API_KEY)

if not API_KEY:
    raise ValueError("No API key found. Please set the YOUTUBE_API_KEY environment variable in .env file.")


##function to retrieve all video IDs
def get_video_ids(channel_id):
    video_ids = []
    try:
        request = youtube.search().list(
            part="id",
            channelId=channel_id,
            maxResults=50,
            type="video",
        )
        response = request.execute()

        while response["items"]:
            for item in response["items"]:
                video_ids.append(item["id"]["videoId"])

            if 'nextPageToken' in response:
                request = youtube.search().list(
                    part="id",
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=response["nextPageToken"],
                    type="video",
                )
                response = request.execute()
            else:
                break

    except HTTPError as error:
        print(f"{error} has occurred")

    return video_ids


#Function to fetch channek details (e.g. channel name, subscribers and total view counts)
def get_channel_details(channel_id):
    channel_details = {
        "channel_name": "",
        "total_subscribers": "",
        "total_videos": "",
        "total_views": "",
        "channel_description": ""
    }
    try:
        request = youtube.channels().list(part="snippet,statistics", id=channel_id)
        response = request.execute()
        if response["items"]:
            channel_details["channel_name"] = response["items"][0]["snippet"]["title"]
            channel_details["total_subscribers"] = response["items"][0]["statistics"]["subscriberCount"]
            channel_details["total_videos"] = response["items"][0]["statistics"]["videoCount"]
            channel_details["total_views"] = response["items"][0]["statistics"]["viewCount"]
            channel_details["channel_description"] = response["items"][0]["snippet"]["description"]
    except HTTPError as error:
        print(f"{error} has occurred")
    return channel_details


#function to retrieve video statistics
def get_video_stats(video_id):
    try:
        request = youtube.videos().list(part="snippet,statistics", id=video_id)
        response = request.execute()

        if response["items"]:
            video = response["items"][0]
            title = video["snippet"]["title"]
            views = int(video["statistics"]["viewCount"])
            likes = int(video["statistics"]["likeCount"])
            upload_date = (datetime.strptime(video["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ").strftime
                           ("%d/%m/%Y"))
            return [title, views, likes, upload_date]
        else:
            return ["N/A", 0, 0, "N/A"]
    except HTTPError as error:
        print(f"An error occurred: {error}")
        return ["N/A", 0, 0, "N/A"]


##Create dataframe by combining the data and the columns
def create_dataframe(channel_id):
    video_ids = get_video_ids(channel_id)
    video_stats = [get_video_stats(id) for id in video_ids]
    df = pd.DataFrame(video_stats, columns=["Title", "Views", "Likes", "Release Date"])
    return df


def trim_title(track_name):
    if len(track_name) <= MAX_TITLE_LENGTH:
        return track_name
    else:
        return track_name[:(MAX_TITLE_LENGTH - SPACE_FOR_DOTS)] + "..."

def save_data_plot(df, plot_type="views"):
    if plot_type == "views":
        top10_df = df.sort_values(by=['Views'], ascending=False)[:10]
        top10_df["Title"] = top10_df["Title"].apply(trim_title)
        plt.figure(figsize=(12, 5))
        plt.barh(top10_df['Title'], top10_df["Views"], color="green")
        plt.xlabel("Views")
        plt.ylabel("Video Title")
        plt.title("Top10 most viewed videos")
        plt.tight_layout()
        plt.gca().invert_yaxis()
        plot_filename = os.path.join("app", "static", "views_plot.png")
    elif plot_type == "likes":
        top10_df = df.sort_values(by=['Likes'], ascending=False)[:10]
        top10_df["Title"] = top10_df["Title"].apply(trim_title)
        plt.figure(figsize=(12, 5))
        plt.barh(top10_df['Title'], top10_df["Likes"], color="blue")
        plt.xlabel("Likes")
        plt.ylabel("Video Title")
        plt.title("Top10 most liked videos")
        plt.tight_layout()
        plt.gca().invert_yaxis()
        plot_filename = os.path.join("app", "static", "likes_plot.png")

    plt.savefig(plot_filename)
    plt.close()
