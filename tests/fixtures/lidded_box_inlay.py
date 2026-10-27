"""Test model: an open box, a slide-fit lid on its own plate, and a stripe inlaid
in the lid top. Three colours: white body, blue lid, red stripe.
"""

import bpy

c = params["fit"]["slide"]
colours = params.get("colours") or ["white", "blue", "red"]


def block(name, size, centre):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(scale=True)
    obj.location = centre
    bpy.ops.object.transform_apply(location=True)
    return obj


def apply(obj, other, operation):
    mod = obj.modifiers.new(operation.lower(), "BOOLEAN")
    mod.operation = operation
    mod.object = other
    mod.solver = "EXACT"
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(other, do_unlink=True)


body = block("body", (40, 30, 20), (0, 0, 10))
apply(body, block("cavity", (36, 26, 20), (0, 0, 12)), "DIFFERENCE")

lid = block("lid", (40, 30, 3), (0, 0, 21.5))
apply(lid, block("plug", (36 - 2 * c, 26 - 2 * c, 3), (0, 0, 18.5)), "UNION")
# The pocket's cutter is taller than the lid so it breaks through the top.
apply(lid, block("pocket", (24, 4, 2), (0, 0, 23.4)), "DIFFERENCE")
stripe = block("stripe", (24, 4, 0.6), (0, 0, 22.7))

part(body, "body", color=colours[0])
part(lid, "lid", color=colours[1], rotate=(180, 0, 0), plate=2)
part(stripe, "stripe", color=colours[2], group="lid", rotate=(180, 0, 0), plate=2)
fit("body", "lid", "slide")
