from google import genai

client = genai.Client(api_key="AIzaSyBR4MNnI1LLaiY7ulMPp1x92hzFeuAmwwU")

my_file = client.files.upload(file=r"D:\mini\pes_image_test.jpeg")

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[my_file, "Caption this image."],
)

print(response.text)