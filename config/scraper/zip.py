from zipfile import ZipFile

from django.core.files.temp import NamedTemporaryFile
from django.http import FileResponse


def make_zip(tmp_files, **kwargs):
        with NamedTemporaryFile(
            prefix=kwargs['prefix'], 
            suffix=kwargs['suffix']
            ) as zf_file:

            with ZipFile(zf_file, 'w') as myzip:
                for tfile in tmp_files:
                    myzip.write(tfile.name)
                    # tfile.close()

            response = FileResponse(
                open(zf_file.name, 'rb'), 
                as_attachment=True
                )

            response['Content-Disposition'] = f"attachment; filename={zf_file.name}"
    
        return response

def get_zip(tmp_files, **kwargs):
    zip_response = make_zip(tmp_files, **kwargs)
    return zip_response
