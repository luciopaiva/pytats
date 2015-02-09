
import os
import datetime
import re
import collections


def iter_files(root: str, wanted_extensions: tuple=None) -> collections.Iterable:
    for path, dirs, files in os.walk(root):
        for fname in files:
            yield_it = (not wanted_extensions) or \
                       (wanted_extensions and (len(wanted_extensions) > 0) and
                        fname.lower().endswith(wanted_extensions))

            if yield_it:
                yield (path, fname)


def stat_files(root: str, wanted_extensions: tuple=None) -> collections.Iterable:
    """ Vai listar todos os arquivos da pasta atual e de suas subpastas, trazendo para cada arquivo uma tupla
        (path, file_name, file_stats)
    """
    for path, file in iter_files(root, wanted_extensions):
        info = os.stat(os.path.join(path, file))
        yield (path, file, info)


def generate_csv_file():
    """ Gera um arquivo CSV com o conteúdo trazido pela função stat_files().
    """
    wanted_extensions = '.flv',

    for t in stat_files('.', wanted_extensions):
        d = datetime.datetime.utcfromtimestamp(t[2].st_birthtime).strftime('%Y-%m-%d')
        print('"{}","{}","{}","{}"'.format(t[0], t[1], t[2].st_size // (1024 * 1024), d))
        # print('{} ({} MB)'.format(t[0], t[2].st_size // (1024 * 1024)))


def rename_suspected_files(root):
    """ Identifiquei que, da lista de vídeos que estou analisando, os vídeos que baixei no ano passado devem ser
        renomeados para um nome temporário, para que meu script de download possa identificar que os vídeos originais
        estão faltando e baixe-os novamente.
    """
    suspect_year = 2014
    wanted_extensions = '.flv',
    new_extension_to_append = '.quarantine'

    suspect_count = 0
    suspect_total_size = 0

    # sorted_videos = sorted(stat_files(root), key=lambda _t: _t[2].st_birthtime, reverse=True)

    for path, file, stat in stat_files(root, wanted_extensions):
        year = datetime.datetime.utcfromtimestamp(stat.st_birthtime).year
        if year == suspect_year:
            print('Renaming "{}"... '.format(file), end='')
            full_name = os.path.join(path, file)
            os.rename(full_name, full_name + new_extension_to_append)
            print('OK')

            suspect_count += 1
            suspect_total_size += stat.st_size

    suspect_total_size //= 1024 * 1024
    print('{} suspect videos with a total size of {} MB.'.format(suspect_count, suspect_total_size))


def group_files_by_extension(root):
    pat = re.compile(r'[^.]*$')

    sizes_by_extension = {}
    for path, file, info in stat_files(root):
        mo = pat.search(file)
        extension = mo.group().lower() if mo else ''
        sizes_by_extension[extension] = sizes_by_extension.get(extension, 0) + info.st_size

    results = sorted(sizes_by_extension.items(), key=lambda t: t[1], reverse=True)
    for key, value in results:
        print('{}: {} MB'.format(key, value // (1024 * 1024)))


def remove_files_by_extension(root: str, extensions: tuple):
    for path, file in iter_files(root, extensions):
        print('Deleting "{}"... '.format(file), end='')
        os.remove(os.path.join(path, file))
        print('OK')

if __name__ == '__main__':
    rename_suspected_files('.')
    # group_files_by_extension('.')
    # remove_files_by_extension('.', ('.avi', '.mp4', '.mkv'))
