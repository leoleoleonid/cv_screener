from google import genai
from google.genai import types

api_key = "AIzaSyDrLAE82k0vs-3FERH0NiBy5oy9Wuov6Zg"
client = genai.Client(api_key=api_key)

response = client.models.generate_images(
    model='imagen-4.0-fast-generate-001',
    prompt='Robot holding a red skateboard',
    config=types.GenerateImagesConfig(
        number_of_images= 1,
    )
)
for generated_image in response.generated_images:
  generated_image.image.show()

response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Расскажи короткую шутку про программистов."
)

print(response.text)