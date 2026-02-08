# from app import create_app
# from app.config import Config
# import os

# app = create_app()

# if __name__ == '__main__':
#     print("--- Starting Server in Debug Mode ---")
#     app.run(host='0.0.0.0', port=5000, debug=True)
    
    
 import gdown
import os

# رابط ملف الموديل من جوجل درايف (استبدل FILE_ID بالمعرف الخاص بك)
file_id = 'YOUR_GOOGLE_DRIVE_FILE_ID'
url = f'https://drive.google.com/uc?id={file_id}'
output = 'models/model.safetensors'

# التأكد من وجود المجلد
os.makedirs('models', exist_ok=True)

# تحميل الملف إذا لم يكن موجوداً
if not os.path.exists(output):
    gdown.download(url, output, quiet=False)
 
from app import create_app
from app.config import Config
import os

app = create_app()


if __name__ == '__main__':
    print("--- Starting Server in Debug Mode ---")
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
