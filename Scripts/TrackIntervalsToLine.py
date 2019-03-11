#Importar modulos

import arcpy, sys
import pandas as pd
arcpy.env.overwriteOutput = True

try:

    ##Parametros
    fcInPut = arcpy.GetParameterAsText(0)
    dateField= arcpy.GetParameterAsText(1)
    fcOutPut = arcpy.GetParameter(2)
    spatialReference = arcpy.GetParameter(3)
    fcOutDesc = arcpy.Describe(fcOutPut)

    ##Crear Dataframe desde coordenadas conocidas

    data = arcpy.da.FeatureClassToNumPyArray(fcInPut, [dateField, "SHAPE@X", "SHAPE@Y"])
    df = pd.DataFrame(data)
    df = df.sort_values([dateField])

    ##Crear Festureclass en blanco
    fc = arcpy.CreateFeatureclass_management(fcOutDesc.path,fcOutDesc.name,"POLYLINE",spatial_reference=arcpy.SpatialReference(4326))
    camposNuevos = {"FECHA_INICIO":"DATE",
                    "FECHA_FINAL":"DATE"}

    for campo in camposNuevos:
        arcpy.AddField_management(fc,campo,camposNuevos[campo])

    cur = arcpy.da.InsertCursor(fc,["FECHA_INICIO","FECHA_FINAL","SHAPE@"])

    ##ingresar campos
    for i in range(1, df.shape[0]):
        coordInicio = [df["SHAPE@X"].iloc[i - 1], df["SHAPE@Y"].iloc[i - 1]]
        coordFinal = [df["SHAPE@X"].iloc[i], df["SHAPE@Y"].iloc[i]]
        array = arcpy.Array([arcpy.Point(coordInicio[0], coordInicio[1]),
                             arcpy.Point(coordFinal[0], coordFinal[1])])
        polyline = arcpy.Polyline(array, spatialReference)
        fechaInicio = df[dateField].iloc[i - 1]
        fechaFinal = df[dateField].iloc[i]
        cur.insertRow([fechaInicio, fechaFinal, polyline])
        array.removeAll()

    del cur
except arcpy.ExecuteError:
    arcpy.AddMessage(arcpy.AddError(arcpy.GetMessages(2)))

except Exception:
    e = sys.exc_info()[1]
    arcpy.AddMessage(e.args[0])