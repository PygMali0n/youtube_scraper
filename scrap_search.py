from scraper import *


def search_api(page_token, region_code):
    # get json file from search api
    url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=50{page_token}q={search_text}&regionCode={region_code}&type=video&key={api_key}"
    request = requests.get(url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()

def videoId_api(id):
    url = f"https://youtube.googleapis.com/youtube/v3/videos?part=id%2Csnippet%2Cstatistics&id={id}&key={api_key}"
    request = requests.get(url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()


def get_search_pages(region_code, next_page_token="&"):
    # get list of video items from search result
    search_data = []
    # limit number of pages due to daily quota
    i = 0

    while next_page_token is not None and i < 65:
        # A page of data i.e. a list of videos and all needed data
        video_data_page = search_api(next_page_token, region_code)

        next_page_token = video_data_page.get("nextPageToken", None)
        next_page_token = f"&pageToken={next_page_token}&" if next_page_token is not None else next_page_token

        # Get all of the items as a list and let get_videos return the needed features
        items = video_data_page.get('items', [])
        search_data += get_videos(id_to_videos(items))
        i += 1

    return search_data


def id_to_videos(items):




if __name__ == "__main__":
