from prettytable import PrettyTable
from utils import inputter, _exit
from traceback import print_exception
from requests import get
from rezka import search, FilmsPage, SeriesPage, Episode
from tqdm import tqdm

import sys


def stderr(_, exception, traceback):
    print('Возникла какая-то непредвиденная ошибка, покажите это разработчику:\n')
    print_exception(_, exception, traceback)
    _exit()

sys.excepthook = stderr


search_query = input('Введите запрос для поиска фильма/сериала: ')

search_results = search(search_query)

print()

if not search_results:
    print('По вашему запросу ничего не найдено!')
    _exit()


table = PrettyTable(['ID', 'Title'])

for i, data in enumerate(search_results, start=1):
    table.add_row([i, '{} "{}"'.format('Сериал' if isinstance(data, SeriesPage) else 'Фильм', data.title)])

data_index = inputter(table.get_string(), 1, i)


data = search_results[data_index]


if isinstance(data, SeriesPage):
    data: SeriesPage

    translators = data.translators
    translator = translators

    if len(translators) > 1:
        table = PrettyTable(['ID', 'Озвучка'])

        for i, translator in enumerate(translators, start=1):
            table.add_row([i, translator[1]])

        translator = translators[inputter(table.get_string(), 1, i)]

    table = PrettyTable(['ID', 'Сезон', 'Эпизод'])

    data._init_data(translator[0])
    episodes = data._episodes

    for i, episode in enumerate(episodes, start=1):
        episode: Episode
        table.add_row([i, episode.season_id, episode.episode_id])

    episode_index = inputter(table.get_string(), 1, i)

    table = PrettyTable(['ID', 'Качество'])

    for i, episode_data in enumerate(episodes[episode_index].data, start=1):
        table.add_row([i, episode_data[0]])

    quality_index = inputter(table.get_string(), 1, i)

    episode = episodes[episode_index]
    episode_data = episode.data[quality_index]

    quality = episode_data[0]
    url = episode_data[1]

    print('{}-сезон, {}-серия сериала "{}" с качеством {}{}:\n{}'.format(
        episode.season_id, episode.episode_id, data.title, episode_data[0],
        ' в озвучке от {}'.format(translator[1]) if translator[0] != 56 else '', url)
    )

elif isinstance(data, FilmsPage):
    data: FilmsPage

    translators = data.translators
    translator = translators

    if len(translators) > 1:
        table = PrettyTable(['ID', 'Озвучка'])

        for i, translator in enumerate(translators, start=1):
            table.add_row([i, translator[1]])

        translator = translators[inputter(table.get_string(), 1, i)]

    data._init_data(translator[0])

    table = PrettyTable(['ID', 'Качество'])

    for i, _data in enumerate(data._data, start=1):
        table.add_row([i, _data[0]])

    quality_index = inputter(table.get_string(), 1, i)

    item = data._data[quality_index]

    quality = item[0]
    url = item[1]

    print(
        'Фильм "{}" с качеством {}{}:\n{}'\
            .format(
                data.title, quality, ' в озвучке от {}'.format(translator[1]) if translator[0] != 56 else '', url
            )
    )

else:
    print('Что-то пошло не-по плану')
    _exit()


print()


if inputter('Хотите открыть плеер и скачать {}? [Да/Нет]:'.format('эту серию' if isinstance(data, SeriesPage) else 'этот фильм'), yesno=True):
    print()

    filename = '{_type} {title} {quality}.mp4'.format(_type='Сериал' if isinstance(data, SeriesPage) else 'Фильм', title=data.title, quality='{} {} сезон {} эпизод'.format(quality, episode.season_id, episode.episode_id) if isinstance(data, SeriesPage) else quality)

    response = get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))

    with tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True) as progress_bar:
        with open(filename, 'wb') as file:
            for data in response.iter_content(1024):
                progress_bar.update(len(data))
                file.write(data)

    print('\nЗагрузка завершена!')
    print('Отркываю плеер...')

    from PyQt5 import QtWidgets
    from player import PlayerWindow

    app = QtWidgets.QApplication(sys.argv)
    player = PlayerWindow(filepath=filename)
    player.resize(640, 480)
    player.show()
    sys.exit(app.exec_())


_exit()
