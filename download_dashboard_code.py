import urllib.request
import os

# URLs for the generated HTML code from Google Stitch
urls = {
    "Overview_Dashboard.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzQ4MjJiNzEzMmM0YjRkNDNiNTZjNTVkOWMxNmM5YjRlEgsSBxDXzPqgxQYYAZIBIwoKcHJvamVjdF9pZBIVQhM3MTc2OTMwNjU2NTY3NjUzNzM1&filename=&opi=96797242",
    "Model_Performance.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzcwNjQyOTA0NjAzMDQ2NjJhMzM3NTdjYTgxMWZjNDA2EgsSBxDXzPqgxQYYAZIBIwoKcHJvamVjdF9pZBIVQhM3MTc2OTMwNjU2NTY3NjUzNzM1&filename=&opi=96797242",
    "Email_Database.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sX2Y0NGM1NTc1NTNiZDRiYWJhZTdkNmI4MTY3NTE1NmQ1EgsSBxDXzPqgxQYYAZIBIwoKcHJvamVjdF9pZBIVQhM3MTc2OTMwNjU2NTY3NjUzNzM1&filename=&opi=96797242"
}

# The directory where the files will be saved
output_dir = r"d:\play\Email\Dashboard_UI"

def download_screens():
    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    print("Downloading EmailGuard Dashboard screens...")
    
    # Download each file
    for filename, url in urls.items():
        filepath = os.path.join(output_dir, filename)
        try:
            print(f"Downloading {filename}...")
            urllib.request.urlretrieve(url, filepath)
            print(f"✅ Saved to {filepath}")
        except Exception as e:
            print(f"❌ Failed to download {filename}: {e}")
            
    print("\nAll downloads completed!")

if __name__ == "__main__":
    download_screens()
