"""Parametrischer Generator für Makeblock-kompatible Beam-0412-Lochstäbe.

Das Skript wird in Autodesk Fusion über Dienstprogramme > Skripte und Add-Ins
ausgeführt. Die Datei ``parameter.json`` muss im selben Ordner liegen.

Die Geometrie ist ein eigenständig erzeugtes, funktionales Referenzmodell. Sie
verwendet keine Geometrie aus der Makeblock-STEP-Datei.
"""

import json
import math
import os
import traceback

import adsk.core
import adsk.fusion


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARAMETER_FILE = os.path.join(SCRIPT_DIR, "parameter.json")
TOLERANCE_MM = 1e-6


def mm(value):
    """Fusion verwendet intern Zentimeter."""
    return float(value) / 10.0


def load_parameters():
    with open(PARAMETER_FILE, "r", encoding="utf-8") as stream:
        data = json.load(stream)

    parameters = data["parameters"]
    required = (
        "length",
        "width",
        "thickness",
        "end_radius",
        "hole_diameter",
        "hole_pitch",
        "first_hole_offset",
        "groove_inner_width",
        "groove_depth",
    )
    missing = [name for name in required if name not in parameters]
    if missing:
        raise ValueError("Fehlende Parameter: " + ", ".join(missing))

    values = {name: float(parameters[name]) for name in required}
    values["create_grooves"] = bool(parameters.get("create_grooves", True))
    values["component_name"] = str(
        data.get("component_name", "Beam0412-parametrisch")
    )
    validate_parameters(values)
    values["hole_count"] = calculate_hole_count(values)
    return values


def validate_parameters(p):
    positive = (
        "length",
        "width",
        "thickness",
        "end_radius",
        "hole_diameter",
        "hole_pitch",
        "first_hole_offset",
    )
    for name in positive:
        if p[name] <= 0:
            raise ValueError(f"{name} muss größer als 0 sein.")

    if p["end_radius"] * 2 > p["width"] + TOLERANCE_MM:
        raise ValueError("Der Endradius darf höchstens der halben Breite entsprechen.")
    if p["length"] <= 2 * p["end_radius"]:
        raise ValueError("Die Länge ist für die abgerundeten Enden zu klein.")
    if p["hole_diameter"] >= p["width"]:
        raise ValueError("Der Lochdurchmesser muss kleiner als die Breite sein.")
    if not 0 <= p["groove_inner_width"] < p["width"]:
        raise ValueError("groove_inner_width muss zwischen 0 und width liegen.")
    if not 0 <= p["groove_depth"] < p["thickness"] / 2:
        raise ValueError("groove_depth muss kleiner als die halbe Dicke sein.")


def calculate_hole_count(p):
    usable_distance = p["length"] - 2 * p["first_hole_offset"]
    intervals = usable_distance / p["hole_pitch"]
    rounded_intervals = round(intervals)
    if not math.isclose(intervals, rounded_intervals, abs_tol=TOLERANCE_MM):
        raise ValueError(
            "Länge, erster Lochabstand und Lochraster ergeben kein vollständiges "
            f"Lochmuster: {intervals:.6f} Rasterabstände."
        )
    return int(rounded_intervals) + 1


def add_user_parameter(design, name, value_mm, comment):
    existing = design.userParameters.itemByName(name)
    expression = f"{value_mm:g} mm"
    if existing:
        existing.expression = expression
        existing.comment = comment
        return existing
    return design.userParameters.add(
        name,
        adsk.core.ValueInput.createByString(expression),
        "mm",
        comment,
    )


def register_user_parameters(design, p):
    entries = (
        ("beam_length", p["length"], "Gesamtlänge des Lochstabs"),
        ("beam_width", p["width"], "Gesamtbreite"),
        ("beam_thickness", p["thickness"], "Gesamtdicke"),
        ("beam_end_radius", p["end_radius"], "Radius der Enden"),
        ("beam_hole_diameter", p["hole_diameter"], "Durchmesser der M4-Bohrungen"),
        ("beam_hole_pitch", p["hole_pitch"], "Abstand benachbarter Lochmittelpunkte"),
        ("beam_first_hole_offset", p["first_hole_offset"], "Lochmitte zum Stirnende"),
        ("beam_groove_inner_width", p["groove_inner_width"], "Breite des ungenuteten Mittelbereichs"),
        ("beam_groove_depth", p["groove_depth"], "Nuttiefe je Breitseite"),
    )
    for name, value, comment in entries:
        add_user_parameter(design, name, value, comment)


def create_capsule_sketch(component, p):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = "Grundriss 0412"
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    radius = mm(p["end_radius"])
    half_width = mm(p["width"] / 2)
    left_x = radius
    right_x = mm(p["length"] - p["end_radius"])

    bottom_left = adsk.core.Point3D.create(left_x, -half_width, 0)
    bottom_right = adsk.core.Point3D.create(right_x, -half_width, 0)
    top_right = adsk.core.Point3D.create(right_x, half_width, 0)
    top_left = adsk.core.Point3D.create(left_x, half_width, 0)

    lines.addByTwoPoints(bottom_left, bottom_right)
    arcs.addByCenterStartSweep(
        adsk.core.Point3D.create(right_x, 0, 0), bottom_right, math.pi
    )
    lines.addByTwoPoints(top_right, top_left)
    arcs.addByCenterStartSweep(
        adsk.core.Point3D.create(left_x, 0, 0), top_left, math.pi
    )
    return sketch


def extrude_base(component, sketch, p):
    profile = sketch.profiles.item(0)
    extrudes = component.features.extrudeFeatures
    extrude_input = extrudes.createInput(
        profile, adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    )
    distance = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(mm(p["thickness"]))
    )
    extrude_input.setOneSideExtent(
        distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(extrude_input)
    feature.name = "Grundkörper"
    body = feature.bodies.item(0)
    body.name = f"Beam0412-{int(round(p['length'])):03d}"
    return body


def create_holes(component, p):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = f"{p['hole_count']} Bohrungen Ø{p['hole_diameter']:g}"
    circles = sketch.sketchCurves.sketchCircles
    radius = mm(p["hole_diameter"] / 2)
    for index in range(p["hole_count"]):
        x = p["first_hole_offset"] + index * p["hole_pitch"]
        circles.addByCenterRadius(adsk.core.Point3D.create(mm(x), 0, 0), radius)

    profiles = adsk.core.ObjectCollection.create()
    for index in range(sketch.profiles.count):
        profiles.add(sketch.profiles.item(index))

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    distance = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(mm(p["thickness"]))
    )
    cut_input.setOneSideExtent(
        distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(cut_input)
    feature.name = f"Lochmuster {p['hole_count']} × Ø{p['hole_diameter']:g}"


def add_rectangle(lines, x_min, y_min, x_max, y_max):
    lines.addTwoPointRectangle(
        adsk.core.Point3D.create(mm(x_min), mm(y_min), 0),
        adsk.core.Point3D.create(mm(x_max), mm(y_max), 0),
    )


def create_groove_sketch(component, p, name):
    sketch = component.sketches.add(component.xYConstructionPlane)
    sketch.name = name
    half_width = p["width"] / 2
    half_inner = p["groove_inner_width"] / 2
    # Die Rechtecke ragen minimal über die Außenkontur hinaus. Dadurch werden
    # auch die gerundeten Stirnbereiche zuverlässig geschnitten.
    overlap = p["end_radius"] + 1
    add_rectangle(
        sketch.sketchCurves.sketchLines,
        -overlap,
        half_inner,
        p["length"] + overlap,
        half_width + overlap,
    )
    add_rectangle(
        sketch.sketchCurves.sketchLines,
        -overlap,
        -half_width - overlap,
        p["length"] + overlap,
        -half_inner,
    )
    return sketch


def cut_grooves(component, p, from_top=False):
    side = "oben" if from_top else "unten"
    sketch = create_groove_sketch(component, p, f"Längsnuten {side}")
    profiles = adsk.core.ObjectCollection.create()
    for index in range(sketch.profiles.count):
        profiles.add(sketch.profiles.item(index))

    extrudes = component.features.extrudeFeatures
    cut_input = extrudes.createInput(
        profiles, adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    if from_top:
        cut_input.startExtent = adsk.fusion.OffsetStartDefinition.create(
            adsk.core.ValueInput.createByReal(
                mm(p["thickness"] - p["groove_depth"])
            )
        )
    distance = adsk.fusion.DistanceExtentDefinition.create(
        adsk.core.ValueInput.createByReal(mm(p["groove_depth"]))
    )
    cut_input.setOneSideExtent(
        distance, adsk.fusion.ExtentDirections.PositiveExtentDirection
    )
    feature = extrudes.add(cut_input)
    feature.name = f"Längsnuten {side}"


def get_or_create_design(app):
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design:
        return design
    document = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    return adsk.fusion.Design.cast(document.products.itemByProductType("DesignProductType"))


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = get_or_create_design(app)
        design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        parameters = load_parameters()
        register_user_parameters(design, parameters)

        occurrence = design.rootComponent.occurrences.addNewComponent(
            adsk.core.Matrix3D.create()
        )
        component = occurrence.component
        component.name = parameters["component_name"]

        base_sketch = create_capsule_sketch(component, parameters)
        extrude_base(component, base_sketch, parameters)
        create_holes(component, parameters)
        if parameters["create_grooves"] and parameters["groove_depth"] > 0:
            cut_grooves(component, parameters, from_top=False)
            cut_grooves(component, parameters, from_top=True)

        ui.messageBox(
            f"{component.name} wurde erzeugt.\n"
            f"Länge: {parameters['length']:g} mm\n"
            f"Bohrungen: {parameters['hole_count']} × Ø"
            f"{parameters['hole_diameter']:g} mm"
        )
    except Exception:
        if ui:
            ui.messageBox("Beam-Generator fehlgeschlagen:\n" + traceback.format_exc())
        else:
            raise


def stop(context):
    """Für die Ausführung als Fusion-Skript ist keine Bereinigung nötig."""

