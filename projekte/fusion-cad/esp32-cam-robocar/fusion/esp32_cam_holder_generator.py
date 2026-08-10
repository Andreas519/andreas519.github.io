"""Erster parametrischer ESP32-CAM-Halter für das RoboCar.

Das Skript erzeugt in Autodesk Fusion drei Komponenten:

- einen offenen Kamerarahmen mit Pin-Freiräumen,
- einen einteiligen U-Bügel mit M4-Anbindung,
- ein vereinfachtes Referenzmodell des realen Kameramoduls.

``parameter.json`` muss im selben Ordner liegen.
"""

import json
import math
import os
import traceback

import adsk.core
import adsk.fusion


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMETER_FILE = os.path.join(SCRIPT_DIR, "parameter.json")


def mm(value):
    """Fusion verwendet intern Zentimeter."""
    return float(value) / 10.0


def load_parameters():
    with open(PARAMETER_FILE, "r", encoding="utf-8") as stream:
        data = json.load(stream)

    module = {name: float(value) for name, value in data["module"].items()
              if name != "mounting_holes"}
    design = {name: float(value) for name, value in data["parameters"].items()}
    generation = {
        "target": str(data.get("generation", {}).get("target", "ask")),
        "create_holder": bool(data.get("generation", {}).get(
            "create_holder", False
        )),
        "create_faceplate": bool(data.get("generation", {}).get(
            "create_faceplate", True
        )),
        "create_camera_clip": bool(data.get("generation", {}).get(
            "create_camera_clip", False
        )),
        "adapter_version": str(data.get("generation", {}).get(
            "adapter_version", "V3"
        )),
        "faceplate_version": str(data.get("generation", {}).get(
            "faceplate_version", "V2"
        )),
    }
    mbot_mount = {
        name: float(value) for name, value in data.get("mbot_mount", {}).items()
    }
    validate_parameters(module, design, mbot_mount, generation)
    return module, design, generation, mbot_mount


def validate_parameters(m, p, mbot, generation):
    for collection in (m, p, mbot):
        for name, value in collection.items():
            if value <= 0:
                raise ValueError(f"{name} muss größer als 0 sein.")

    if m["camera_center_from_top"] >= m["board_length"]:
        raise ValueError("Die Kameramitte muss innerhalb der Platinenlänge liegen.")
    if m["pin_row_spacing"] >= m["board_width"]:
        raise ValueError("Der Pinreihenabstand muss kleiner als die Platinenbreite sein.")
    if m["board_corner_radius"] * 2 >= min(
        m["board_width"], m["board_length"]
    ):
        raise ValueError("Der Platinen-Eckradius ist zu groß.")
    if int(m["pin_count_per_row"]) != m["pin_count_per_row"]:
        raise ValueError("pin_count_per_row muss eine ganze Zahl sein.")
    if m["pin_count_per_row"] < 2:
        raise ValueError("Jede Pinreihe benötigt mindestens zwei Stifte.")
    pin_span = (m["pin_count_per_row"] - 1) * m["pin_pitch"]
    if pin_span >= m["board_length"]:
        raise ValueError("Das Pinraster ist länger als die Platine.")
    header_length = pin_span + m["pin_pitch"]
    if m["pin_header_from_bottom"] + header_length > m["board_length"]:
        raise ValueError("Die Stiftleiste ragt über die Platine hinaus.")
    if p["board_clearance"] >= p["wall_thickness"]:
        raise ValueError("board_clearance muss kleiner als wall_thickness sein.")
    if p["pin_slot_width"] <= 1.0:
        raise ValueError("pin_slot_width ist für die Stiftleiste zu klein.")
    if p["wall_thickness"] < p["pivot_hole_diameter"] + 0.8:
        raise ValueError("wall_thickness benötigt mindestens 0,4 mm Rand um die Drehbohrung.")
    lens_stack = (
        p["camera_base_depth"]
        + p["lens_base_depth"]
        + p["lens_middle_depth"]
        + p["lens_top_depth"]
    )
    if lens_stack >= m["camera_height_above_board"]:
        if lens_stack != m["camera_height_above_board"]:
            raise ValueError("Objektivstapel ist höher als der gemessene Kamerabauraum.")
    lens_center_from_top = (
        p["lens_base_from_top"] + p["lens_base_height"] / 2
    )
    if lens_center_from_top != m["camera_center_from_top"]:
        raise ValueError(
            "camera_center_from_top passt nicht zur Lage des Objektivsockels."
        )
    if mbot:
        minimum_width = (
            mbot["mount_hole_spacing"] + mbot["screw_head_diameter"]
        )
        if mbot["adapter_width"] < minimum_width:
            raise ValueError(
                "adapter_width ist für Lochabstand und Schraubenköpfe zu klein."
            )
        if mbot["mount_hole_diameter"] <= 3.2:
            raise ValueError("Die M3-Bohrung benötigt Fertigungsspiel.")
        if mbot["neck_width"] >= mbot["sensor_cylinder_gap"]:
            raise ValueError(
                "neck_width muss kleiner als der freie Zylinderabstand sein."
            )
        if mbot["lower_lip_height"] > mbot["side_rail_height"]:
            raise ValueError(
                "lower_lip_height darf nicht höher als die Seitenführung sein."
            )
        if (
            mbot["upper_lip_from_bottom"] + mbot["upper_lip_height"]
            > mbot["side_rail_height"]
        ):
            raise ValueError(
                "Die obere Sicherungslippe muss innerhalb der Seitenführung liegen."
            )
        if mbot["rail_gusset_height"] > mbot["side_rail_height"]:
            raise ValueError(
                "rail_gusset_height darf nicht höher als die Seitenführung sein."
            )
        if mbot["rail_gusset_width"] * 2 >= m["board_width"]:
            raise ValueError("Die Verstärkungsrippen sind für die Platine zu breit.")
        nose_lower = (
            m["board_length"] - mbot["rail_nose_lower_from_board_top"]
        )
        nose_upper = nose_lower + mbot["rail_nose_height"]
        if nose_upper >= mbot["side_rail_height"]:
            raise ValueError(
                "Oberhalb der Rastnase muss eine Einführungsschräge bleiben."
            )
        if mbot["faceplate_window_top"] >= m["board_length"]:
            raise ValueError("Das Blendenfenster muss unter der Kamera enden.")
        if not (
            0 <= mbot["faceplate_bottom_from_board_bottom"]
            < mbot["faceplate_window_bottom_margin"]
            < mbot["faceplate_window_top"]
        ):
            raise ValueError(
                "Unterkante, unterer Quersteg und Fensterende der Frontblende "
                "liegen nicht in der richtigen Reihenfolge."
            )
        if mbot["faceplate_flange_height"] > mbot["side_rail_height"]:
            raise ValueError(
                "Die Blendenflügel dürfen nicht höher als die Führungen sein."
            )
        if generation["create_camera_clip"]:
            if mbot["camera_clip_bottom"] <= (
                m["pin_header_from_bottom"]
                + m["pin_count_per_row"] * m["pin_pitch"]
            ):
                raise ValueError(
                    "Der Kamera-Clip benötigt Abstand zu den oberen Pins."
                )
            if mbot["camera_clip_opening_width"] >= m["board_width"]:
                raise ValueError("Die U-Öffnung ist breiter als die Platine.")
        sensor_diameter = (
            mbot["sensor_cylinder_center_spacing"]
            - mbot["sensor_cylinder_gap"]
        )
        if sensor_diameter <= 0:
            raise ValueError("Die Sonic-Zylindermaße sind widersprüchlich.")


def get_or_create_design(app):
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design:
        return design
    document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    return adsk.fusion.Design.cast(
        document.products.itemByProductType("DesignProductType")
    )


def add_component(design, name):
    occurrence = design.rootComponent.occurrences.addNewComponent(
        adsk.core.Matrix3D.create()
    )
    occurrence.component.name = name
    return occurrence.component


def add_rectangle(sketch, x_min, z_min, x_max, z_max):
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(x_min), mm(z_min), 0),
        adsk.core.Point3D.create(mm(x_max), mm(z_max), 0),
    )


def add_rounded_rectangle(sketch, x_min, z_min, x_max, z_max, radius):
    """Zeichnet ein geschlossenes Rechteck mit vier gleichen Eckradien."""
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    def point(x, z):
        return adsk.core.Point3D.create(mm(x), mm(z), 0)

    lines.addByTwoPoints(point(x_min + radius, z_min),
                         point(x_max - radius, z_min))
    arcs.addByCenterStartSweep(
        point(x_max - radius, z_min + radius),
        point(x_max - radius, z_min),
        math.pi / 2,
    )
    lines.addByTwoPoints(point(x_max, z_min + radius),
                         point(x_max, z_max - radius))
    arcs.addByCenterStartSweep(
        point(x_max - radius, z_max - radius),
        point(x_max, z_max - radius),
        math.pi / 2,
    )
    lines.addByTwoPoints(point(x_max - radius, z_max),
                         point(x_min + radius, z_max))
    arcs.addByCenterStartSweep(
        point(x_min + radius, z_max - radius),
        point(x_min + radius, z_max),
        math.pi / 2,
    )
    lines.addByTwoPoints(point(x_min, z_max - radius),
                         point(x_min, z_min + radius))
    arcs.addByCenterStartSweep(
        point(x_min + radius, z_min + radius),
        point(x_min, z_min + radius),
        math.pi / 2,
    )


def extrude_profiles(component, sketch, distance_mm, operation, start_mm=0.0,
                     name=None):
    profiles = adsk.core.ObjectCollection.create()
    for index in range(sketch.profiles.count):
        profiles.add(sketch.profiles.item(index))

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(profiles, operation)
    if start_mm:
        extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(mm(start_mm))
        )
    distance = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(mm(distance_mm))
    )
    extrude_input.setOneSideExtent(
        distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    if name:
        feature.name = name
    return feature


def create_embossed_text(component, plane, text, bounds, height, depth,
                         start, name, horizontal_flip=False):
    """Prägt eine kurze Versionskennung erhaben auf einen Körper."""
    sketch = component.sketches.add(plane)
    sketch.name = name
    texts = sketch.sketchTexts
    expression = "'" + text.replace("'", "") + "'"
    try:
        text_input = texts.createInput3(
            expression,
            adsk.core.ValueInput.createByString(f"{height:g} mm"),
        )
    except (AttributeError, TypeError):
        # Kompatibilität mit Fusion-Versionen vor createInput3.
        text_input = texts.createInput2(text, mm(height))
    x0, z0, x1, z1 = bounds
    text_input.setAsMultiLine(
        adsk.core.Point3D.create(mm(x0), mm(z0), 0),
        adsk.core.Point3D.create(mm(x1), mm(z1), 0),
        adsk.core.HorizontalAlignments.CenterHorizontalAlignment,
        adsk.core.VerticalAlignments.TopVerticalAlignment,
        0,
    )
    text_input.isHorizontalFlip = horizontal_flip
    sketch_text = texts.add(text_input)

    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        sketch_text, adsk.fusion.FeatureOperations.JoinFeatureOperation
    )
    extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
        adsk.core.ValueInput.createByReal(mm(start))
    )
    distance = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(mm(depth))
    )
    extrude_input.setOneSideExtent(
        distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = name
    return feature


def create_rectangle_feature(component, plane, bounds, depth, operation,
                             start=0.0, name=None, sketch_name=None):
    sketch = component.sketches.add(plane)
    if sketch_name:
        sketch.name = sketch_name
    add_rectangle(sketch, *bounds)
    return extrude_profiles(component, sketch, depth, operation, start, name)


def create_rounded_rectangle_feature(component, plane, bounds, radius, depth,
                                     operation, start=0.0, name=None,
                                     sketch_name=None):
    sketch = component.sketches.add(plane)
    if sketch_name:
        sketch.name = sketch_name
    add_rounded_rectangle(sketch, *bounds, radius)
    return extrude_profiles(component, sketch, depth, operation, start, name)


def create_polygon_feature(component, plane, points, depth, operation,
                           start=0.0, name=None, sketch_name=None):
    sketch = component.sketches.add(plane)
    if sketch_name:
        sketch.name = sketch_name
    lines = sketch.sketchCurves.sketchLines
    fusion_points = [
        adsk.core.Point3D.create(mm(x), mm(z), 0) for x, z in points
    ]
    for index, point in enumerate(fusion_points):
        lines.addByTwoPoints(point, fusion_points[(index + 1) % len(points)])
    return extrude_profiles(component, sketch, depth, operation, start, name)


def create_polygon_with_holes(component, plane, points, hole_centers,
                              hole_diameter, depth, start=0.0, name=None,
                              sketch_name=None):
    sketch = component.sketches.add(plane)
    if sketch_name:
        sketch.name = sketch_name
    lines = sketch.sketchCurves.sketchLines
    fusion_points = [
        adsk.core.Point3D.create(mm(x), mm(z), 0) for x, z in points
    ]
    for index, point in enumerate(fusion_points):
        lines.addByTwoPoints(point, fusion_points[(index + 1) % len(points)])

    circles = sketch.sketchCurves.sketchCircles
    for x, z in hole_centers:
        circles.addByCenterRadius(
            adsk.core.Point3D.create(mm(x), mm(z), 0), mm(hole_diameter / 2)
        )

    outer_profile = max(
        (sketch.profiles.item(index) for index in range(sketch.profiles.count)),
        key=lambda profile: profile.areaProperties().area,
    )
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        outer_profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    if start:
        extrude_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(mm(start))
        )
    distance = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(mm(depth))
    )
    extrude_input.setOneSideExtent(
        distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    if name:
        feature.name = name
    return feature


def create_circle_cut(component, plane, centers, diameter, depth, start, name):
    sketch = component.sketches.add(plane)
    sketch.name = name
    circles = sketch.sketchCurves.sketchCircles
    for x, z in centers:
        circles.addByCenterRadius(
            adsk.core.Point3D.create(mm(x), mm(z), 0), mm(diameter / 2)
        )
    return extrude_profiles(
        component,
        sketch,
        depth,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        start,
        name,
    )


def add_reference_distance(sketch, point_one, point_two, orientation,
                           text_x, text_z):
    """Ergänzt ein nicht treibendes Kontrollmaß in einer Master-Skizze."""
    dimension = sketch.sketchDimensions.addDistanceDimension(
        point_one,
        point_two,
        orientation,
        adsk.core.Point3D.create(mm(text_x), mm(text_z), 0),
        False,
    )
    return dimension


def create_mbot_master_sketch(component, m, mbot, geometry):
    """Zeichnet die entscheidenden Adaptermaße als prüfbare 2D-Übersicht."""
    sketch = component.sketches.add(component.xZConstructionPlane)
    sketch.name = "mBot Master-Skizze"
    lines = sketch.sketchCurves.sketchLines

    outline_points = [
        adsk.core.Point3D.create(mm(x), mm(z), 0)
        for x, z in geometry["outline"]
    ]
    outline_lines = []
    for index, point in enumerate(outline_points):
        outline_lines.append(lines.addByTwoPoints(
            point, outline_points[(index + 1) % len(outline_points)]
        ))

    rail_inner_left = -mbot["board_side_clearance"]
    rail_inner_right = m["board_width"] + mbot["board_side_clearance"]
    nose_lower_z = (
        m["board_length"] - mbot["rail_nose_lower_from_board_top"]
    )
    nose_upper_z = nose_lower_z + mbot["rail_nose_height"]
    rail_profiles = (
        (
            (geometry["adapter_x0"], 0),
            (rail_inner_left, 0),
            (rail_inner_left, nose_lower_z),
            (rail_inner_left + mbot["rail_nose_overlap"], m["board_length"]),
            (rail_inner_left + mbot["rail_nose_overlap"], nose_upper_z),
            (
                rail_inner_left - mbot["rail_entry_flare"],
                mbot["side_rail_height"],
            ),
            (geometry["adapter_x0"], mbot["side_rail_height"]),
        ),
        (
            (rail_inner_right, 0),
            (geometry["adapter_x1"], 0),
            (geometry["adapter_x1"], mbot["side_rail_height"]),
            (
                rail_inner_right + mbot["rail_entry_flare"],
                mbot["side_rail_height"],
            ),
            (rail_inner_right - mbot["rail_nose_overlap"], nose_upper_z),
            (rail_inner_right - mbot["rail_nose_overlap"], m["board_length"]),
            (rail_inner_right, nose_lower_z),
        ),
    )
    for profile in rail_profiles:
        points = [
            adsk.core.Point3D.create(mm(x), mm(z), 0) for x, z in profile
        ]
        for index, point in enumerate(points):
            lines.addByTwoPoints(point, points[(index + 1) % len(points)])

    gusset_points = (
        (
            (rail_inner_left - mbot["rail_gusset_overlap"],
             -mbot["rail_gusset_overlap"]),
            (rail_inner_left - mbot["rail_gusset_overlap"],
             mbot["rail_gusset_height"]),
            (rail_inner_left + mbot["rail_gusset_width"],
             -mbot["rail_gusset_overlap"]),
        ),
        (
            (rail_inner_right + mbot["rail_gusset_overlap"],
             -mbot["rail_gusset_overlap"]),
            (rail_inner_right + mbot["rail_gusset_overlap"],
             mbot["rail_gusset_height"]),
            (rail_inner_right - mbot["rail_gusset_width"],
             -mbot["rail_gusset_overlap"]),
        ),
    )
    for triangle in gusset_points:
        points = [
            adsk.core.Point3D.create(mm(x), mm(z), 0) for x, z in triangle
        ]
        for index, point in enumerate(points):
            lines.addByTwoPoints(point, points[(index + 1) % len(points)])

    lip_zones = (
        (0, mbot["lower_lip_height"]),
        (
            mbot["upper_lip_from_bottom"],
            mbot["upper_lip_from_bottom"] + mbot["upper_lip_height"],
        ),
    )
    for z0, z1 in lip_zones:
        add_rectangle(
            sketch,
            geometry["adapter_x0"],
            z0,
            mbot["front_lip_overlap"],
            z1,
        )
        add_rectangle(
            sketch,
            m["board_width"] - mbot["front_lip_overlap"],
            z0,
            geometry["adapter_x1"],
            z1,
        )

    circles = sketch.sketchCurves.sketchCircles
    hole_circles = []
    for x, z in geometry["hole_centers"]:
        hole_circles.append(circles.addByCenterRadius(
            adsk.core.Point3D.create(mm(x), mm(z), 0),
            mm(mbot["mount_hole_diameter"] / 2),
        ))

    centerline = lines.addByTwoPoints(
        adsk.core.Point3D.create(
            mm(geometry["board_center_x"]), mm(geometry["plate_bottom"]), 0
        ),
        adsk.core.Point3D.create(
            mm(geometry["board_center_x"]),
            mm(mbot["side_rail_height"]),
            0,
        ),
    )
    centerline.isConstruction = True

    horizontal = (
        adsk.fusion.DimensionOrientations
        .HorizontalDimensionOrientation
    )
    vertical = (
        adsk.fusion.DimensionOrientations
        .VerticalDimensionOrientation
    )
    add_reference_distance(
        sketch,
        outline_lines[4].startSketchPoint,
        outline_lines[6].endSketchPoint,
        horizontal,
        geometry["board_center_x"],
        geometry["sensor_top"] + 3,
    )
    add_reference_distance(
        sketch,
        hole_circles[0].centerSketchPoint,
        hole_circles[1].centerSketchPoint,
        horizontal,
        geometry["board_center_x"],
        geometry["hole_z"] - 6,
    )
    add_reference_distance(
        sketch,
        outline_lines[5].endSketchPoint,
        centerline.endSketchPoint,
        vertical,
        geometry["adapter_x1"] + 5,
        mbot["side_rail_height"] / 2,
    )
    diameter = sketch.sketchDimensions.addDiameterDimension(
        hole_circles[0],
        adsk.core.Point3D.create(
            mm(geometry["hole_centers"][0][0] - 5),
            mm(geometry["hole_z"]),
            0,
        ),
        False,
    )
    return sketch


def register_parameters(design, m, p):
    entries = {
        "cam_board_length": m["board_length"],
        "cam_board_width": m["board_width"],
        "cam_board_thickness": m["board_thickness"],
        "cam_pin_projection": m["pin_projection_below_board"],
        "cam_pin_row_spacing": m["pin_row_spacing"],
        "cam_pin_pitch": m["pin_pitch"],
        "cam_pin_square_size": m["pin_square_size"],
        "cam_camera_height": m["camera_height_above_board"],
        "cam_camera_from_top": m["camera_center_from_top"],
        "holder_clearance": p["board_clearance"],
        "holder_wall": p["wall_thickness"],
        "holder_pivot_diameter": p["pivot_hole_diameter"],
        "holder_beam_hole_diameter": p["beam_mount_hole_diameter"],
    }
    for name, value in entries.items():
        existing = design.userParameters.itemByName(name)
        expression = f"{value:g} mm"
        if existing:
            existing.expression = expression
        else:
            design.userParameters.add(
                name,
                adsk.core.ValueInput.createByString(expression),
                "mm",
                "ESP32-CAM-Halter",
            )


def register_mbot_parameters(design, mbot):
    hole_center_below_board = (
        mbot["screw_head_diameter"] / 2
        + mbot["screw_edge_to_sensor_top"]
        + mbot["board_gap_above_sensor"]
    )
    entries = {
        "mbot_hole_spacing": mbot["mount_hole_spacing"],
        "mbot_hole_diameter": mbot["mount_hole_diameter"],
        "mbot_hole_below_board": hole_center_below_board,
        "mbot_sensor_gap": mbot["sensor_cylinder_gap"],
        "mbot_neck_width": mbot["neck_width"],
        "mbot_plane_offset": mbot["plane_offset"],
        "mbot_adapter_width": mbot["adapter_width"],
        "mbot_adapter_thickness": mbot["adapter_thickness"],
    }
    for name, value in entries.items():
        existing = design.userParameters.itemByName(name)
        expression = f"{value:g} mm"
        if existing:
            existing.expression = expression
        else:
            design.userParameters.add(
                name,
                adsk.core.ValueInput.createByString(expression),
                "mm",
                "mBot-Adapter für ESP32-CAM",
            )


def derived_dimensions(m, p):
    board_gap = p["board_clearance"]
    wall = p["wall_thickness"]
    inner_width = m["board_width"] + board_gap
    inner_length = m["board_length"] + board_gap
    outer_width = inner_width + 2 * wall
    outer_length = inner_length + 2 * wall
    board_x = wall + board_gap / 2
    board_z = p["yoke_bridge_height"] + p["yoke_clearance"] + wall + board_gap / 2
    frame_z = p["yoke_bridge_height"] + p["yoke_clearance"]
    pivot_z = board_z + m["board_length"] - m["camera_center_from_top"]
    return {
        "inner_width": inner_width,
        "inner_length": inner_length,
        "outer_width": outer_width,
        "outer_length": outer_length,
        "board_x": board_x,
        "board_z": board_z,
        "frame_z": frame_z,
        "pivot_z": pivot_z,
    }


def create_cradle(design, m, p, d):
    component = add_component(design, "ESP32-CAM Kamerarahmen")
    plane = component.xZConstructionPlane
    yoke_depth = p["yoke_thickness"]
    cradle_start = yoke_depth + p["yoke_clearance"]
    rear = p["rear_frame_thickness"]
    total_depth = rear + m["board_thickness"] + p["retaining_lip_height"]

    create_rectangle_feature(
        component,
        plane,
        (0, d["frame_z"], d["outer_width"], d["frame_z"] + d["outer_length"]),
        total_depth,
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        cradle_start,
        "Rahmen außen",
        "Rahmenkontur",
    )

    cavity_start = cradle_start + rear
    create_rectangle_feature(
        component,
        plane,
        (
            p["wall_thickness"],
            d["frame_z"] + p["wall_thickness"],
            p["wall_thickness"] + d["inner_width"],
            d["frame_z"] + p["wall_thickness"] + d["inner_length"],
        ),
        total_depth - rear,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        cavity_start,
        "Platinenaufnahme",
        "Platinenaufnahme",
    )

    margin = p["electronics_opening_margin"]
    create_rectangle_feature(
        component,
        plane,
        (
            d["board_x"] + margin,
            d["board_z"] + margin,
            d["board_x"] + m["board_width"] - margin,
            d["board_z"] + m["board_length"] - margin,
        ),
        rear,
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        cradle_start,
        "Elektronikfreiraum",
        "Elektronikfreiraum",
    )

    row_offset = (m["board_width"] - m["pin_row_spacing"]) / 2
    slot_half = p["pin_slot_width"] / 2
    z0 = d["board_z"] + p["pin_slot_end_margin"]
    z1 = d["board_z"] + m["board_length"] - p["pin_slot_end_margin"]
    for index, x in enumerate((d["board_x"] + row_offset,
                               d["board_x"] + m["board_width"] - row_offset), 1):
        create_rectangle_feature(
            component,
            plane,
            (x - slot_half, z0, x + slot_half, z1),
            rear,
            adsk.fusion.FeatureOperations.CutFeatureOperation,
            cradle_start,
            f"Pinfreiraum {index}",
            f"Pinfreiraum {index}",
        )

    create_circle_cut(
        component,
        plane,
        [
            (p["yoke_arm_width"] / 2, d["pivot_z"]),
            (d["outer_width"] - p["yoke_arm_width"] / 2, d["pivot_z"]),
        ],
        p["pivot_hole_diameter"],
        total_depth,
        cradle_start,
        "Drehbohrungen Kamerarahmen",
    )
    return component


def create_yoke(design, p, d):
    component = add_component(design, "ESP32-CAM U-Bügel")
    plane = component.xZConstructionPlane
    top = d["pivot_z"] + p["yoke_arm_width"]

    create_rectangle_feature(
        component,
        plane,
        (0, 0, d["outer_width"], top),
        p["yoke_thickness"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        0,
        "U-Bügel außen",
        "U-Bügel Kontur",
    )
    create_rectangle_feature(
        component,
        plane,
        (
            p["yoke_arm_width"],
            p["yoke_bridge_height"],
            d["outer_width"] - p["yoke_arm_width"],
            top,
        ),
        p["yoke_thickness"],
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        0,
        "U-Bügel Öffnung",
        "U-Bügel Öffnung",
    )
    create_circle_cut(
        component,
        plane,
        [
            (p["yoke_arm_width"] / 2, d["pivot_z"]),
            (d["outer_width"] - p["yoke_arm_width"] / 2, d["pivot_z"]),
        ],
        p["pivot_hole_diameter"],
        p["yoke_thickness"],
        0,
        "Drehbohrungen U-Bügel",
    )
    create_circle_cut(
        component,
        plane,
        [(d["outer_width"] / 2, p["yoke_bridge_height"] / 2)],
        p["beam_mount_hole_diameter"],
        p["yoke_thickness"],
        0,
        "M4 Beam-Befestigung",
    )
    return component


def create_mbot_adapter(design, m, mbot, part_version):
    component = add_component(design, "mBot ESP32-CAM Adapter")
    plane = component.xZConstructionPlane
    board_center_x = m["board_width"] / 2
    adapter_x0 = board_center_x - mbot["adapter_width"] / 2
    adapter_x1 = board_center_x + mbot["adapter_width"] / 2
    hole_center_below_board = (
        mbot["screw_head_diameter"] / 2
        + mbot["screw_edge_to_sensor_top"]
        + mbot["board_gap_above_sensor"]
    )
    hole_z = -hole_center_below_board
    plate_bottom = hole_z - (
        mbot["screw_head_diameter"] / 2
        + mbot["edge_margin_below_screw_head"]
    )
    flange_top = hole_z + (
        mbot["screw_head_diameter"] / 2
        + mbot["edge_margin_below_screw_head"]
    )
    sensor_diameter = (
        mbot["sensor_cylinder_center_spacing"]
        - mbot["sensor_cylinder_gap"]
    )
    sensor_top = -mbot["board_gap_above_sensor"]
    sensor_bottom = sensor_top - sensor_diameter
    neck_x0 = board_center_x - mbot["neck_width"] / 2
    neck_x1 = board_center_x + mbot["neck_width"] / 2
    adapter_start = (
        m["pin_projection_below_board"] - mbot["plane_offset"]
    )

    outline = (
        (adapter_x0, plate_bottom),
        (adapter_x1, plate_bottom),
        (adapter_x1, flange_top),
        (neck_x1, sensor_bottom),
        (neck_x1, sensor_top),
        (adapter_x1, 0),
        (adapter_x0, 0),
        (neck_x0, sensor_top),
        (neck_x0, sensor_bottom),
        (adapter_x0, flange_top),
    )
    hole_x_offset = mbot["mount_hole_spacing"] / 2
    hole_centers = (
        (board_center_x - hole_x_offset, hole_z),
        (board_center_x + hole_x_offset, hole_z),
    )
    create_mbot_master_sketch(
        component,
        m,
        mbot,
        {
            "outline": outline,
            "adapter_x0": adapter_x0,
            "adapter_x1": adapter_x1,
            "board_center_x": board_center_x,
            "plate_bottom": plate_bottom,
            "sensor_top": sensor_top,
            "hole_z": hole_z,
            "hole_centers": hole_centers,
        },
    )
    bridge = create_polygon_with_holes(
        component,
        plane,
        outline,
        hole_centers,
        mbot["mount_hole_diameter"],
        mbot["adapter_thickness"],
        adapter_start,
        "mBot Konturadapter",
        "Schraubflansch, Hals und Aufweitung",
    )
    bridge.bodies.item(0).name = "mBot Montagebrücke"

    rail_inner_left = -mbot["board_side_clearance"]
    rail_inner_right = m["board_width"] + mbot["board_side_clearance"]
    nose_lower_z = (
        m["board_length"] - mbot["rail_nose_lower_from_board_top"]
    )
    nose_upper_z = nose_lower_z + mbot["rail_nose_height"]
    rail_points = (
        (
            (adapter_x0, 0),
            (rail_inner_left, 0),
            (rail_inner_left, nose_lower_z),
            (rail_inner_left + mbot["rail_nose_overlap"], m["board_length"]),
            (rail_inner_left + mbot["rail_nose_overlap"], nose_upper_z),
            (rail_inner_left - mbot["rail_entry_flare"], mbot["side_rail_height"]),
            (adapter_x0, mbot["side_rail_height"]),
        ),
        (
            (rail_inner_right, 0),
            (adapter_x1, 0),
            (adapter_x1, mbot["side_rail_height"]),
            (rail_inner_right + mbot["rail_entry_flare"], mbot["side_rail_height"]),
            (rail_inner_right - mbot["rail_nose_overlap"], nose_upper_z),
            (rail_inner_right - mbot["rail_nose_overlap"], m["board_length"]),
            (rail_inner_right, nose_lower_z),
        ),
    )
    rail_width = (
        mbot["adapter_width"] - m["board_width"]
    ) / 2 - mbot["board_side_clearance"]
    for index, points in enumerate(rail_points, 1):
        rail = create_polygon_feature(
            component,
            plane,
            points,
            mbot["adapter_thickness"],
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            adapter_start,
            f"Seitenführung {index}",
            f"Seitenführung {index}",
        )
        rail.bodies.item(0).name = f"Seitenführung {index} ({rail_width:g} mm)"

    # Die Dreiecksrippen liegen hinter der Platine. Dadurch versteifen sie den
    # im Probedruck auffälligen 90-Grad-Übergang, ohne die Einschubbreite oder
    # die seitlichen Pinleisten zu verdecken.
    gusset_depth = mbot["rail_gusset_depth"]
    gusset_start = adapter_start - gusset_depth + mbot["plane_offset"]
    gusset_points = (
        (
            (rail_inner_left - mbot["rail_gusset_overlap"],
             -mbot["rail_gusset_overlap"]),
            (rail_inner_left - mbot["rail_gusset_overlap"],
             mbot["rail_gusset_height"]),
            (rail_inner_left + mbot["rail_gusset_width"],
             -mbot["rail_gusset_overlap"]),
        ),
        (
            (rail_inner_right + mbot["rail_gusset_overlap"],
             -mbot["rail_gusset_overlap"]),
            (rail_inner_right + mbot["rail_gusset_overlap"],
             mbot["rail_gusset_height"]),
            (rail_inner_right - mbot["rail_gusset_width"],
             -mbot["rail_gusset_overlap"]),
        ),
    )
    for index, points in enumerate(gusset_points, 1):
        create_polygon_feature(
            component,
            plane,
            points,
            gusset_depth,
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
            gusset_start,
            f"Rückseitige Übergangsrippe {index}",
            f"Rückseitige Übergangsrippe {index}",
        )

    front_start = (
        m["pin_projection_below_board"]
        + m["board_thickness"]
        + mbot["board_depth_clearance"]
    )
    lip_zones = (
        ("unten", 0, mbot["lower_lip_height"]),
        (
            "oben",
            mbot["upper_lip_from_bottom"],
            mbot["upper_lip_from_bottom"] + mbot["upper_lip_height"],
        ),
    )
    lip_x_ranges = (
        (adapter_x0, mbot["front_lip_overlap"]),
        (m["board_width"] - mbot["front_lip_overlap"], adapter_x1),
    )
    for zone_name, z0, z1 in lip_zones:
        for index, (x0, x1) in enumerate(lip_x_ranges, 1):
            lip = create_rectangle_feature(
                component,
                plane,
                (x0, z0, x1, z1),
                mbot["front_lip_depth"],
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                front_start,
                f"Vorderlippe {zone_name} {index}",
                f"Vorderlippe {zone_name} {index}",
            )
            lip.bodies.item(0).name = f"Vorderlippe {zone_name} {index}"

    create_embossed_text(
        component,
        plane,
        part_version,
        (
            board_center_x - 4.0,
            plate_bottom + 0.5,
            board_center_x + 4.0,
            plate_bottom + 3.8,
        ),
        2.4,
        0.5,
        adapter_start - 0.4,
        "Versionsprägung Adapter",
        True,
    )

    return component


def create_mbot_faceplate(design, m, p, mbot, part_version):
    """Erzeugt eine von oben aufschiebbare Blende zur Kamerafixierung."""
    component = add_component(design, "ESP32-CAM Frontblende")
    plane = component.xZConstructionPlane
    board_center_x = m["board_width"] / 2
    adapter_x0 = board_center_x - mbot["adapter_width"] / 2
    adapter_x1 = board_center_x + mbot["adapter_width"] / 2
    # Die Seitenflügel stehen je Seite 0,1 mm in das Nennmaß der
    # Adapterführungen hinein und erzeugen dadurch eine leichte Klemmung.
    inner_x0 = adapter_x0 + mbot["faceplate_side_interference"]
    inner_x1 = adapter_x1 - mbot["faceplate_side_interference"]
    panel_x0 = inner_x0 - mbot["faceplate_wall"]
    panel_x1 = inner_x1 + mbot["faceplate_wall"]
    # V3 endet auf Höhe der weißen Kamerasteckerleiste. Der untere Teil der
    # Platine bleibt sichtbar und die kürzere Blende kann weniger kippeln.
    panel_z0 = mbot["faceplate_bottom_from_board_bottom"]
    panel_z1 = m["board_length"] + mbot["faceplate_top_margin"]

    board_front = (
        m["pin_projection_below_board"] + m["board_thickness"]
    )
    # Die Rückseite der Blende liegt an der Vorderseite des quadratischen
    # Objektivsockels an und drückt damit das Kamerapaket gegen die Platine.
    panel_start = (
        board_front + p["camera_base_depth"] + p["lens_base_depth"]
    )
    panel = create_rectangle_feature(
        component,
        plane,
        (panel_x0, panel_z0, panel_x1, panel_z1),
        mbot["faceplate_thickness"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        panel_start,
        "Blendenrahmen",
        "Blendenkontur",
    )
    panel.bodies.item(0).name = "Frontblende"

    window_x0 = mbot["faceplate_window_side_margin"]
    window_x1 = m["board_width"] - mbot["faceplate_window_side_margin"]
    create_rectangle_feature(
        component,
        plane,
        (
            window_x0,
            mbot["faceplate_window_bottom_margin"],
            window_x1,
            mbot["faceplate_window_top"],
        ),
        mbot["faceplate_thickness"],
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        panel_start,
        "Elektronik- und Blitzfenster",
        "Elektronik- und Blitzfenster",
    )

    camera_z = m["board_length"] - m["camera_center_from_top"]
    lens_opening = mbot["faceplate_lens_opening_diameter"]
    create_circle_cut(
        component,
        plane,
        [(board_center_x, camera_z)],
        lens_opening,
        mbot["faceplate_thickness"],
        panel_start,
        "Objektivöffnung Frontblende",
    )

    flange_start = (
        m["pin_projection_below_board"]
        - mbot["plane_offset"]
        - mbot["faceplate_back_clearance"]
    )
    flange_depth = (
        panel_start + mbot["faceplate_thickness"] - flange_start
    )
    flange_ranges = (
        (panel_x0, inner_x0),
        (inner_x1, panel_x1),
    )
    for index, (x0, x1) in enumerate(flange_ranges, 1):
        create_rectangle_feature(
            component,
            plane,
            (x0, panel_z0, x1, mbot["faceplate_flange_height"]),
            flange_depth,
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
            flange_start,
            f"Aufschiebeflügel {index}",
            f"Aufschiebeflügel {index}",
        )

    # Da V3 keinen durchgehenden unteren Quersteg mehr besitzt, liegt die
    # Versionskennung rechts oberhalb des Objektivs.
    create_embossed_text(
        component,
        plane,
        part_version,
        (
            board_center_x + lens_opening / 2 + 0.8,
            camera_z + lens_opening / 2 + 0.3,
            panel_x1 - 0.5,
            panel_z1 - 0.5,
        ),
        2.0,
        0.5,
        panel_start - 0.4,
        "Versionsprägung Frontblende",
        True,
    )

    return component


def create_camera_u_clip(design, m, p, mbot):
    """Erzeugt einen kompakten U-Clip, der direkt an der Platine klemmt."""
    component = add_component(design, "ESP32-CAM U-Kamera-Clip")
    plane = component.xZConstructionPlane
    board_center_x = m["board_width"] / 2
    camera_z = m["board_length"] - m["camera_center_from_top"]
    interference = mbot["camera_clip_side_interference"]
    wall = mbot["camera_clip_wall"]
    clip_x0 = -wall + interference
    clip_x1 = m["board_width"] + wall - interference
    clip_z0 = mbot["camera_clip_bottom"]
    clip_z1 = m["board_length"] + mbot["camera_clip_top_margin"]

    board_front = (
        m["pin_projection_below_board"] + m["board_thickness"]
    )
    clip_front_start = (
        board_front + p["camera_base_depth"] + p["lens_base_depth"]
    )
    clip = create_rectangle_feature(
        component,
        plane,
        (clip_x0, clip_z0, clip_x1, clip_z1),
        mbot["camera_clip_thickness"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        clip_front_start,
        "U-Clip Grundplatte",
        "U-Clip Kontur",
    )
    clip.bodies.item(0).name = "U-Kamera-Clip"

    opening_half = mbot["camera_clip_opening_width"] / 2
    # Die Aussparung wird bewusst unter die Unterkante verlängert. Dadurch
    # entsteht ein echtes U statt eines geschlossenen Rahmens.
    create_rectangle_feature(
        component,
        plane,
        (
            board_center_x - opening_half,
            clip_z0 - 1.0,
            board_center_x + opening_half,
            camera_z + mbot["camera_clip_opening_above_center"],
        ),
        mbot["camera_clip_thickness"],
        adsk.fusion.FeatureOperations.CutFeatureOperation,
        clip_front_start,
        "U-Öffnung Objektiv",
        "U-Öffnung Objektiv",
    )

    lip_start = (
        m["pin_projection_below_board"]
        - mbot["camera_clip_back_clearance"]
    )
    lip_depth = (
        clip_front_start + mbot["camera_clip_thickness"] - lip_start
    )
    lip_ranges = (
        (clip_x0, interference),
        (m["board_width"] - interference, clip_x1),
    )
    for index, (x0, x1) in enumerate(lip_ranges, 1):
        create_rectangle_feature(
            component,
            plane,
            (x0, clip_z0, x1, clip_z1),
            lip_depth,
            adsk.fusion.FeatureOperations.JoinFeatureOperation,
            lip_start,
            f"Federnde Platinenlippe {index}",
            f"Federnde Platinenlippe {index}",
        )

    return component


def create_module_reference(design, m, p, d, standalone=False):
    component = add_component(design, "ESP32-CAM Referenz")
    plane = component.xZConstructionPlane
    if standalone:
        board_x = 0.0
        board_z = 0.0
        board_start = m["pin_projection_below_board"]
    else:
        board_x = d["board_x"]
        board_z = d["board_z"]
        board_start = (
            p["yoke_thickness"]
            + p["yoke_clearance"]
            + p["rear_frame_thickness"]
        )

    feature = create_rounded_rectangle_feature(
        component,
        plane,
        (
            board_x,
            board_z,
            board_x + m["board_width"],
            board_z + m["board_length"],
        ),
        m["board_corner_radius"],
        m["board_thickness"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        board_start,
        "Platine Referenz",
        "Platine 27 × 40",
    )
    feature.bodies.item(0).name = "ESP32-CAM Platine 27x40x2"

    board_front = board_start + m["board_thickness"]
    create_embossed_text(
        component,
        plane,
        "ESP32-CAM",
        (
            board_x + 2.0,
            board_z + 1.0,
            board_x + m["board_width"] - 2.0,
            board_z + 5.0,
        ),
        3.0,
        0.2,
        board_front,
        "Platinenbeschriftung ESP32-CAM",
    )

    connector_x0 = (
        board_x + (m["board_width"] - m["ffc_connector_width"]) / 2
    )
    connector_z0 = (
        board_z + m["ffc_connector_center_from_bottom"]
        - m["ffc_connector_height"] / 2
    )
    connector = create_rectangle_feature(
        component,
        plane,
        (
            connector_x0,
            connector_z0,
            connector_x0 + m["ffc_connector_width"],
            connector_z0 + m["ffc_connector_height"],
        ),
        m["ffc_connector_depth"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        board_front,
        "Weiße Kamerasteckerleiste",
        "Kamerasteckerleiste 19x4",
    )
    connector.bodies.item(0).name = "Weiße Kamerasteckerleiste"

    led_half = m["flash_led_size"] / 2
    led_x = board_x + m["flash_led_center_from_left"]
    led_z = board_z + m["flash_led_center_from_bottom"]
    led = create_rectangle_feature(
        component,
        plane,
        (
            led_x - led_half,
            led_z - led_half,
            led_x + led_half,
            led_z + led_half,
        ),
        m["flash_led_depth"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        board_front,
        "Gelbe Blitz-LED",
        "Blitz-LED 3.5x3.5",
    )
    led.bodies.item(0).name = "Gelbe Blitz-LED"

    row_offset = (m["board_width"] - m["pin_row_spacing"]) / 2
    pin_count = int(m["pin_count_per_row"])
    pin_span = (pin_count - 1) * m["pin_pitch"]
    header_length = pin_span + m["pin_pitch"]
    header_z0 = board_z + m["pin_header_from_bottom"]
    header_z1 = header_z0 + header_length
    first_pin_z = header_z0 + m["pin_pitch"] / 2
    for index, pin_x in enumerate((
        board_x + row_offset,
        board_x + m["board_width"] - row_offset,
    ), 1):
        header = create_rectangle_feature(
            component,
            plane,
            (
                pin_x - m["header_body_width"] / 2,
                header_z0,
                pin_x + m["header_body_width"] / 2,
                header_z1,
            ),
            m["header_body_height"],
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
            board_start - m["header_body_height"],
            f"Kunststoffträger Pinreihe {index}",
            f"Kunststoffträger Pinreihe {index}",
        )
        header.bodies.item(0).name = f"Pinreihe {index} Kunststoffträger"

        pin_half = m["pin_square_size"] / 2
        for pin_index in range(pin_count):
            pin_z = first_pin_z + pin_index * m["pin_pitch"]
            pin = create_rectangle_feature(
                component,
                plane,
                (
                    pin_x - pin_half,
                    pin_z - pin_half,
                    pin_x + pin_half,
                    pin_z + pin_half,
                ),
                (
                    m["pin_projection_below_board"]
                    + m["board_thickness"]
                    + 0.8
                ),
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
                0,
                f"Pin {index}.{pin_index + 1}",
                f"Pin {index}.{pin_index + 1}",
            )
            pin.bodies.item(0).name = f"Vierkantstift {index}.{pin_index + 1}"

    camera_x = board_x + m["board_width"] / 2
    board_top = board_z + m["board_length"]
    camera_base_z = board_top - p["camera_base_height"] / 2
    camera_z = (
        board_top
        - p["lens_base_from_top"]
        - p["lens_base_height"] / 2
    )
    camera_start = board_start + m["board_thickness"]

    camera_base = create_rectangle_feature(
        component,
        plane,
        (
            camera_x - p["camera_base_width"] / 2,
            camera_base_z - p["camera_base_height"] / 2,
            camera_x + p["camera_base_width"] / 2,
            camera_base_z + p["camera_base_height"] / 2,
        ),
        p["camera_base_depth"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        camera_start,
        "Kameraunterbau",
        "Kameraunterbau 15x15",
    )
    camera_base.bodies.item(0).name = "Kameraunterbau 15x15x2"

    lens_start = camera_start + p["camera_base_depth"]
    lens_base = create_rectangle_feature(
        component,
        plane,
        (
            camera_x - p["lens_base_width"] / 2,
            camera_z - p["lens_base_height"] / 2,
            camera_x + p["lens_base_width"] / 2,
            camera_z + p["lens_base_height"] / 2,
        ),
        p["lens_base_depth"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        lens_start,
        "Objektivsockel",
        "Objektivsockel 8x8",
    )
    lens_base.bodies.item(0).name = "Objektivsockel 8x8x2"

    middle_sketch = component.sketches.add(plane)
    middle_sketch.name = "Objektivstufe Ø8"
    middle_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(mm(camera_x), mm(camera_z), 0),
        mm(p["lens_middle_diameter"] / 2),
    )
    middle = extrude_profiles(
        component,
        middle_sketch,
        p["lens_middle_depth"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        lens_start + p["lens_base_depth"],
        "Objektivstufe Ø8",
    )
    middle.bodies.item(0).name = "Objektivzylinder Ø8x2"

    top_sketch = component.sketches.add(plane)
    top_sketch.name = "Objektivstufe Ø7"
    top_sketch.sketchCurves.sketchCircles.addByCenterRadius(
        adsk.core.Point3D.create(mm(camera_x), mm(camera_z), 0),
        mm(p["lens_top_diameter"] / 2),
    )
    top = extrude_profiles(
        component,
        top_sketch,
        p["lens_top_depth"],
        adsk.fusion.FeatureOperations.NewBodyFeatureOperation,
        lens_start + p["lens_base_depth"] + p["lens_middle_depth"],
        "Objektivstufe Ø7",
    )
    top.bodies.item(0).name = "Objektivzylinder Ø7x2"
    return component


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = get_or_create_design(app)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        module, parameters, generation, mbot_mount = load_parameters()
        register_parameters(design, module, parameters)
        if mbot_mount:
            register_mbot_parameters(design, mbot_mount)
        derived = derived_dimensions(module, parameters)

        target = generation["target"]
        if target == "ask":
            choice = ui.messageBox(
                "Welche einzelne Komponente soll erzeugt werden?\n\n"
                "Ja: Kamera-Dummy\n"
                "Nein: mBot-Halterung\n"
                "Abbrechen: nichts erzeugen",
                "ESP32-CAM Generator",
                adsk.core.MessageBoxButtonTypes.YesNoCancelButtonType,
            )
            if choice == adsk.core.DialogResults.DialogCancel:
                return
            target = (
                "module_dummy"
                if choice == adsk.core.DialogResults.DialogYes
                else "mbot_adapter"
            )

        if target not in ("module_dummy", "mbot_adapter"):
            raise ValueError(
                "generation.target muss 'ask', 'module_dummy' oder "
                "'mbot_adapter' sein."
            )

        if generation["create_holder"]:
            create_yoke(design, parameters, derived)
            create_cradle(design, module, parameters, derived)
        if target == "module_dummy":
            create_module_reference(
                design,
                module,
                parameters,
                derived,
                standalone=not generation["create_holder"],
            )
        if target == "mbot_adapter":
            create_mbot_adapter(
                design, module, mbot_mount, generation["adapter_version"]
            )
            if generation["create_faceplate"]:
                create_mbot_faceplate(
                    design,
                    module,
                    parameters,
                    mbot_mount,
                    generation["faceplate_version"],
                )
            if generation["create_camera_clip"]:
                create_camera_u_clip(
                    design, module, parameters, mbot_mount
                )

        if target == "module_dummy":
            result_name = "Kamera-Dummy"
        else:
            additions = []
            if generation["create_faceplate"]:
                additions.append("Adapterblende")
            if generation["create_camera_clip"]:
                additions.append("U-Kamera-Clip")
            result_name = "mBot-Halterung"
            if additions:
                result_name += " mit " + " und ".join(additions)
        ui.messageBox(
            f"{result_name} wurde als einzelne Komponente erzeugt.\n"
            f"Platine: {module['board_width']:g} × {module['board_length']:g} mm\n"
            f"Gesamthöhe Dummy: "
            f"{module['pin_projection_below_board'] + module['board_thickness'] + module['camera_height_above_board']:g} mm"
        )
    except Exception:
        if ui:
            ui.messageBox(
                "ESP32-CAM-Halter fehlgeschlagen:\n" + traceback.format_exc()
            )
        else:
            raise


def stop(context):
    """Für die Ausführung als Fusion-Skript ist keine Bereinigung nötig."""
