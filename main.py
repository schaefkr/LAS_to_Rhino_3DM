import laspy
import numpy as np
import rhino3dm
import constants


def create_rhino3dm_point(x, y, z):
    pt = rhino3dm.Point3d(x, y, z)
    return pt


if __name__ == '__main__':
    # Get Data from Las File with Laspy
    las_filepath = 'filename.las'
    with laspy.open(las_filepath) as f:
        for points in f.chunk_iterator(1000000000):
            x, y, z, classification_codes = points.x.copy(), points.y.copy(), points.z.copy(), points.classification.copy()
    pts = zip(x.tolist(), y.tolist(), z.tolist(), classification_codes.tolist())
    classification_codes = np.unique(np.array(classification_codes.tolist()))

    # Create Rhino 3dm file
    model = rhino3dm.File3dm()
    model.Settings.ModelUnitSystem = rhino3dm.UnitSystem.Feet
    layers_by_classification_codes = {}

    for code in classification_codes:
        name = f'{code}-{constants.LAS_CLASSIFICATION_CODES[str(code)]}'
        point_cloud = rhino3dm.PointCloud()
        props = {
            'name': name,
            'idx': 0,
            'point_cloud': point_cloud,
        }
        layers_by_classification_codes[str(code)] = props

    for x, y, z, code in pts:
        pt = create_rhino3dm_point(x, y, z)
        layers_by_classification_codes[str(code)]['point_cloud'].Add(pt)

    for code, props in layers_by_classification_codes.items():
        layer = rhino3dm.Layer()
        layer.Name = props['name']
        layer_idx = model.Layers.Add(layer)
        attrs = rhino3dm.ObjectAttributes()
        attrs.LayerIndex = layer_idx
        model.Objects.Add(props['point_cloud'], attrs)

    model.Write(f'las_to_rhino_3dm_output.3dm', 7)
