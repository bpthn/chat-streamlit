def check_status(response, url):
    if response.status_code == 200:
        print(f"The webpage {url} is accessible.")
        return True
    else:
        print("Failed to retrieve the webpage. Status code:", response.status_code)
        return False