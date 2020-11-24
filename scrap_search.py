from scraper import *


def search_api(page_token, region_code):
    # get json file from search api
    url = f"https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=50{page_token}q={search_key}&regionCode={region_code}&type=video&key={api_key}"
    request = requests.get(url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()


def video_id_api(video_id):
    url = f"https://youtube.googleapis.com/youtube/v3/videos?part=id%2Csnippet%2Cstatistics&id={video_id}&key={api_key}"
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

    while next_page_token is not None and i < 60:
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
    # get id from search results and use the id search for the videos info
    res = []

    for item in items:
        video_id = item["id"].get("videoId","")
        if video_id != "":
            res.append(video_id_api(video_id).get('items', [])[0])

    return res


def init(api_path, region_path, search_path):
    with open(api_path, 'r') as file:
        api = file.readline()

    with open(region_path) as file:
        country = file.readline()

    with open(search_path, 'r') as file:
        search = file.readline()

    return api, country, search


def write_to_csv(country, search, data):
    print(f"Writing {search} data to file...")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/{time.strftime('%y.%d.%m')}_{country}_{search}_videos.csv", "w+", encoding='utf-8') as file:
        for row in data:
            file.write(f"{row}\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--key_path',
                        help='Path to the file containing the api key, by default will use api_key.txt in the same directory',
                        default='api_key.txt')
    parser.add_argument('--country_code_path',
                        help='Path to the file containing the list of country codes to scrape, by default will use country_codes.txt in the same directory',
                        default='country_codes.txt')
    parser.add_argument('--output_dir', help='Path to save the outputted files in', default='output/')
    parser.add_argument('--search_keyword', help='path to the file containing search keyword', default='search_key.txt')

    args = parser.parse_args()

    output_dir = args.output_dir
    api_key, country_code, search_key = init(args.key_path, args.country_code_path, args.search_keyword)

    search_data_result = [",".join(header)] + get_search_pages(country_code)
    write_to_csv(country_code, search_key, search_data_result)