"""On-demand image requests for the common study extent."""
from urllib.parse import urlencode
from urllib.request import urlopen
from audit import ROI

BASE = 'https://raster.geosampa.prefeitura.sp.gov.br/geoserver/geoportal/wms'
LAYERS = {2017: 'Orto_PMD_RGB_2017', 2020: 'ORTO_RGB_2020'}


def image_url(year):
    query = dict(service='WMS', version='1.1.1', request='GetMap',
                 layers=LAYERS[year], styles='', srs='EPSG:31983',
                 bbox=','.join(map(str, ROI)), width=512, height=512,
                 format='image/png')
    return BASE + '?' + urlencode(query)


def fetch_image(year):
    with urlopen(image_url(year), timeout=15) as response:
        data = response.read(5_000_001)
    if len(data) > 5_000_000 or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('GeoSampa did not return a valid PNG image.')
    return data
