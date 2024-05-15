import io
import zipfile


def sane_repr(*attrs):
    """
    Borrowed from sentry
    """
    if 'id' not in attrs and 'pk' not in attrs:
        attrs = ('id',) + attrs

    def _repr(self):
        cls = type(self).__name__

        pairs = (
            '{}={}'.format(x, repr(getattr(self, x, None)))
            for x in attrs
        )

        return '<{} at 0x{}: {}>'.format(cls, id(self), ', '.join(pairs))

    return _repr


def make_zip(data, compression=zipfile.ZIP_STORED):
    """ Создает .zip в памяти из переданных файлов

    Принимает массив [
        ('file_name', 'file_content')
    ].

    Возвращает b'zipfile_content'
    """
    # убираем пустые файлы
    data = [item for item in data if item[1]]
    if not data:
        return
    zf = io.BytesIO()
    with zipfile.ZipFile(zf, mode='w',
                         compression=compression,
                         allowZip64=False) as zipper:
        for filename, content in data:
            zipper.writestr(filename, content)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for f in zipper.filelist:
            f.create_system = 0

    return zf.getvalue()
