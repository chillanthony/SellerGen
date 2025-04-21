import requests

def download_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        response.raise_for_status()  # 如果请求失败会抛出异常

        with open(save_path, 'wb') as f:
            f.write(response.content)

        print(f"图片已成功保存到：{save_path}")
    except Exception as e:
        print(f"下载失败：{e}")

# 示例调用
url = "https://images.pexels.com/photos/2325447/pexels-photo-2325447.jpeg"
path = "downloaded_image.jpg"

download_image(url, path)