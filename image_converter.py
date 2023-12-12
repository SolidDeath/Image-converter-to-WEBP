import os
from PIL import Image
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def convert_to_webp(image_path, output_path, quality):
    try:
        with Image.open(image_path) as img:
            output_file = os.path.join(output_path, os.path.basename(image_path) + '.webp')
            img.convert('RGB').save(output_file, 'webp', quality=quality)
            print(f"Successfully converted '{os.path.basename(image_path)}' to WEBP at '{output_path}' with quality {quality}.")
    except Exception as e:
        print(f"Error converting '{image_path}': {e}")

def read_config(file_path):
    config = {}
    base_path = os.path.dirname(os.path.abspath(file_path))
    with open(file_path, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            abs_path = os.path.abspath(os.path.join(base_path, value))  # Convert to absolute path
            config[key] = abs_path
    return config


class WatchDirectory(FileSystemEventHandler):
    def __init__(self, quality, output_folder):
        self.quality = quality
        self.output_folder = output_folder

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            print(f"Received task for '{event.src_path}'. Quality: {self.quality}")
            convert_to_webp(event.src_path, self.output_folder, self.quality)

if __name__ == "__main__":
    config = read_config('config.txt')
    output_folder = config['OUTPUT_FOLDER']
    observers = []

    for key, value in config.items():
        if key.startswith('FOLDER_'):
            quality = int(key.split('_')[1])
            folder_to_watch = value
            event_handler = WatchDirectory(quality, output_folder)
            observer = Observer()
            observer.schedule(event_handler, folder_to_watch, recursive=False)
            observer.start()
            observers.append(observer)
            print(f"Monitoring '{folder_to_watch}' for quality {quality}")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        for observer in observers:
            observer.stop()
        for observer in observers:
            observer.join()
        print("Stopped all observers")