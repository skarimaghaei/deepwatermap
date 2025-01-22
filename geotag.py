from osgeo import gdal
import os


def applyGeoData(source_tif, target_tif):
  """Apply georeferencing data from a source geoTIF to a target one.

  Inputs:
    source_tif : str
        Path to a georeferenced geoTIF

    target_tif : str
        Path to a non-georeferenced geoTIF we want to make georeferenced

  Outputs:
    Saves a file with the same name as the target tif but '_ref'
    appeneded as a suffix

  """
  # trim file extensions if they exist
  source_tif = os.path.splitext(source_tif)[0]
  target_tif = os.path.splitext(target_tif)[0]
  src = gdal.Open(source_tif + '.tif')  # open source tif
  # pull georef info from it
  projection = src.GetProjection()
  gt = src.GetGeoTransform()
  # close source
  src = None
  target = gdal.Open(target_tif + '.tif')  # open target tif
  # apply georef info to it
  img = target.ReadAsArray()
  DATA_TYPE = {
    "uint8": gdal.GDT_Byte,
    "int8": gdal.GDT_Byte,
    "uint16": gdal.GDT_UInt16,
    "int16": gdal.GDT_Int16,
    "uint32": gdal.GDT_UInt32,
    "int32": gdal.GDT_Int32,
    "float32": gdal.GDT_Float32,
    "float64": gdal.GDT_Float64
  }
  driver = gdal.GetDriverByName('GTiff')
  ds = driver.Create(target_tif + '_ref.tif',
                     img.shape[1], img.shape[0],
                     1, DATA_TYPE[img.dtype.name])

  ds.SetGeoTransform(gt)
  ds.SetProjection(projection)
  ds.GetRasterBand(1).WriteArray(img)
  ds.FlushCache()
  ds = None

# source_tif = r'C:\\Users\\sk35569\\Coding\\geotag\\Input\\LA_barataria_2020_11_01_2021_04_30_L8_geo'
# target_tif = r'C:\\Users\\sk35569\\Coding\\geotag\\Output\\LA_barataria_2020_11_01_2021_04_30_L8_geo_watermap'
# applyGeoData(source_tif, target_tif)
