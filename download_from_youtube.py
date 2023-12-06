from pytube import YouTube

def download_video(url, output_path='.', filename=None):
    try:
        # Создаем объект YouTube
        yt = YouTube(url)

        # Получаем информацию о видео
        video_title = yt.title

        # Выбираем поток с максимальным разрешением
        video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        # Составляем название файла
        if filename:
            file_name = filename
        else:
            file_name = video_title

        # Если вы хотите указать путь для сохранения файла, укажите output_path
        video_stream.download(output_path, filename=file_name)

        print("Видео успешно скачано")
    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")

# Пример использования
video_url = "https://www.youtube.com/watch?v=6gS1Bp4LZLc"  #. "https://www.youtube.com/watch?v=ваш_идентификатор_видео"
custom_filename = "пользовательское_название.mp4"
download_video(video_url, output_path='Youtube_videos', filename=custom_filename)
