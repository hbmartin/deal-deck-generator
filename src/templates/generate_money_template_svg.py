import svgwrite
from svgwrite import cm, mm
import math

def generate_money_template_svg(filename="playing_card.svg"):
    # Dimensions specified by user
    WIDTH = 732
    HEIGHT = 1101
    
    # Colors based on the reference image
    COLOR_BG_PURPLE = "#A885C4"  # Muted Lavender/Purple
    COLOR_STROKE = "#000000"     # Black
    COLOR_TEXTURE = "#8A69A6"    # Slightly darker purple for the guilloche pattern
    
    # Create the drawing surface
    dwg = svgwrite.Drawing(filename, size=(WIDTH, HEIGHT), profile='full')
    
    # ---------------------------------------------------------
    # 1. DEFINE PATTERNS (The "Guilloche" Background)
    # ---------------------------------------------------------
    # We create a seamless pattern definition for the inner background.
    # The image shows a mesh of intersecting curves (hypocycloids or simple overlapping waves).
    
    pattern_size = 40
    pattern = dwg.defs.add(dwg.pattern(id="guilloche_bg", 
                                      size=(pattern_size, pattern_size), 
                                      patternUnits="userSpaceOnUse"))
    
    # Add a base color rectangle to the pattern (optional, but we usually fill the rect behind)
    # We will draw the pattern lines *over* the solid background.
    
    # Create a "spirograph" style overlapping circle mesh
    # Four interlocked semi-circles creating a diamond/star shape
    path_str = ""
    # Center of tile is (20, 20)
    # We draw arcs from corners to center
    r = pattern_size * 0.6
    
    # Sine wave mesh simulation using paths
    # Horizontal sine
    pattern.add(dwg.path(d=f"M 0,{pattern_size/2} Q {pattern_size/4},0 {pattern_size/2},{pattern_size/2} T {pattern_size},{pattern_size/2}",
                         stroke=COLOR_TEXTURE, stroke_width=1, fill="none", opacity=0.5))
    pattern.add(dwg.path(d=f"M 0,{pattern_size/2} Q {pattern_size/4},{pattern_size} {pattern_size/2},{pattern_size/2} T {pattern_size},{pattern_size/2}",
                         stroke=COLOR_TEXTURE, stroke_width=1, fill="none", opacity=0.5))
    
    # Vertical sine (rotated)
    pattern.add(dwg.path(d=f"M {pattern_size/2},0 Q 0,{pattern_size/4} {pattern_size/2},{pattern_size/2} T {pattern_size/2},{pattern_size}",
                         stroke=COLOR_TEXTURE, stroke_width=1, fill="none", opacity=0.5))
    pattern.add(dwg.path(d=f"M {pattern_size/2},0 Q {pattern_size},{pattern_size/4} {pattern_size/2},{pattern_size/2} T {pattern_size/2},{pattern_size}",
                         stroke=COLOR_TEXTURE, stroke_width=1, fill="none", opacity=0.5))

    # Concentric circles for that "engraved" look
    pattern.add(dwg.circle(center=(pattern_size/2, pattern_size/2), r=pattern_size/3,
                           stroke=COLOR_TEXTURE, stroke_width=0.5, fill="none"))
    pattern.add(dwg.circle(center=(0, 0), r=pattern_size/2.5,
                           stroke=COLOR_TEXTURE, stroke_width=0.5, fill="none"))
    pattern.add(dwg.circle(center=(pattern_size, 0), r=pattern_size/2.5,
                           stroke=COLOR_TEXTURE, stroke_width=0.5, fill="none"))
    pattern.add(dwg.circle(center=(0, pattern_size), r=pattern_size/2.5,
                           stroke=COLOR_TEXTURE, stroke_width=0.5, fill="none"))
    pattern.add(dwg.circle(center=(pattern_size, pattern_size), r=pattern_size/2.5,
                           stroke=COLOR_TEXTURE, stroke_width=0.5, fill="none"))


    # ---------------------------------------------------------
    # 2. BASE LAYERS
    # ---------------------------------------------------------
    # Full card solid fill
    dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=20, ry=20, fill="white")) # White paper edge
    
    # Main colored area (inset by a small margin)
    margin = 30
    main_rect_size = (WIDTH - 2*margin, HEIGHT - 2*margin)
    dwg.add(dwg.rect(insert=(margin, margin), size=main_rect_size, 
                     fill=COLOR_BG_PURPLE, stroke=COLOR_STROKE, stroke_width=4))

    # ---------------------------------------------------------
    # 3. INNER BORDER (The engraved frame)
    # ---------------------------------------------------------
    # This is the "track" that runs around the center.
    border_inset = 60
    border_thickness = 30
    
    # Coordinates for the decorative border
    ib_x = margin + border_inset
    ib_y = margin + border_inset
    ib_w = WIDTH - 2*(margin + border_inset)
    ib_h = HEIGHT - 2*(margin + border_inset)
    
    # Draw the background for the inner border (solid color or same purple)
    # We define the outer and inner rails of this decorative border
    dwg.add(dwg.rect(insert=(ib_x, ib_y), size=(ib_w, ib_h),
                     fill="none", stroke=COLOR_STROKE, stroke_width=2))
    
    dwg.add(dwg.rect(insert=(ib_x + border_thickness, ib_y + border_thickness), 
                     size=(ib_w - 2*border_thickness, ib_h - 2*border_thickness),
                     fill="none", stroke=COLOR_STROKE, stroke_width=2))

    # Generate the "Fanned" / "Arc" pattern inside the border
    # We create a group for the border decorations
    border_pattern_group = dwg.add(dwg.g(id="border_pattern", stroke=COLOR_STROKE, stroke_width=1, fill="none"))
    
    # Function to draw repeating semi-circles along a line
    def draw_frieze(start_x, start_y, length, is_vertical=False, reverse=False):
        step = 12 # Width of each arc
        steps = int(length / step)
        path_d = []
        
        for i in range(steps):
            offset = i * step
            if is_vertical:
                # Vertical strip (Left or Right)
                # Draw semi-circles facing in or out
                x_base = start_x
                y_base = start_y + offset
                
                # Adjust for perfect fit (stretch last segment slightly if needed, but ignoring for simplicity)
                if reverse: # Right side, facing left
                     path_d.append(f"M {x_base},{y_base} Q {x_base-border_thickness},{y_base+step/2} {x_base},{y_base+step}")
                     # Add inner detail lines (concentric arcs)
                     path_d.append(f"M {x_base},{y_base+2} Q {x_base-border_thickness*0.7},{y_base+step/2} {x_base},{y_base+step-2}")
                else: # Left side, facing right
                     path_d.append(f"M {x_base},{y_base} Q {x_base+border_thickness},{y_base+step/2} {x_base},{y_base+step}")
                     path_d.append(f"M {x_base},{y_base+2} Q {x_base+border_thickness*0.7},{y_base+step/2} {x_base},{y_base+step-2}")

            else:
                # Horizontal strip (Top or Bottom)
                x_base = start_x + offset
                y_base = start_y
                
                if reverse: # Bottom side, facing up
                    path_d.append(f"M {x_base},{y_base} Q {x_base+step/2},{y_base-border_thickness} {x_base+step},{y_base}")
                    path_d.append(f"M {x_base+2},{y_base} Q {x_base+step/2},{y_base-border_thickness*0.7} {x_base+step-2},{y_base}")
                else: # Top side, facing down
                    path_d.append(f"M {x_base},{y_base} Q {x_base+step/2},{y_base+border_thickness} {x_base+step},{y_base}")
                    path_d.append(f"M {x_base+2},{y_base} Q {x_base+step/2},{y_base+border_thickness*0.7} {x_base+step-2},{y_base}")
        
        return " ".join(path_d)

    # Top Border (inner rail)
    border_pattern_group.add(dwg.path(d=draw_frieze(ib_x + border_thickness, ib_y + border_thickness, ib_w - 2*border_thickness, False, True)))
    # Bottom Border (inner rail)
    border_pattern_group.add(dwg.path(d=draw_frieze(ib_x + border_thickness, ib_y + ib_h - border_thickness, ib_w - 2*border_thickness, False, False)))
    # Left Border (inner rail)
    border_pattern_group.add(dwg.path(d=draw_frieze(ib_x + border_thickness, ib_y + border_thickness, ib_h - 2*border_thickness, True, True)))
    # Right Border (inner rail)
    border_pattern_group.add(dwg.path(d=draw_frieze(ib_x + ib_w - border_thickness, ib_y + border_thickness, ib_h - 2*border_thickness, True, False)))

    # ---------------------------------------------------------
    # 4. BACKGROUND TEXTURE (Inside the inner border)
    # ---------------------------------------------------------
    texture_x = ib_x + border_thickness
    texture_y = ib_y + border_thickness
    texture_w = ib_w - 2*border_thickness
    texture_h = ib_h - 2*border_thickness
    
    # Fill the center with the pattern
    dwg.add(dwg.rect(insert=(texture_x, texture_y), size=(texture_w, texture_h),
                     fill="url(#guilloche_bg)"))
    
    # ---------------------------------------------------------
    # 5. CORNER ELEMENTS (Detail Circles)
    # ---------------------------------------------------------
    # In the reference image (landscape), they are Bottom-Left and Top-Right.
    # For this portrait version, to maintain standard playing card symmetry, we place them Top-Left and Bottom-Right.
    
    corner_radius = 55
    # Calculate centers
    # Top-Left (overlapping the decorative border corner)
    c1_center = (ib_x + 20, ib_y + 20) 
    # Bottom-Right
    c2_center = (ib_x + ib_w - 20, ib_y + ib_h - 20)

    def draw_corner_circle(center):
        g = dwg.g()
        # Outer fill (clears the borders behind it)
        g.add(dwg.circle(center=center, r=corner_radius, fill=COLOR_BG_PURPLE, stroke="none"))
        # Outer thick border
        g.add(dwg.circle(center=center, r=corner_radius, fill="none", stroke=COLOR_STROKE, stroke_width=3))
        # Inner thin border
        g.add(dwg.circle(center=center, r=corner_radius - 8, fill="none", stroke=COLOR_STROKE, stroke_width=1.5))
        return g

    dwg.add(draw_corner_circle(c1_center))
    dwg.add(draw_corner_circle(c2_center))

    # ---------------------------------------------------------
    # 6. CENTRAL CIRCLE
    # ---------------------------------------------------------
    center_radius = 200
    cx, cy = WIDTH / 2, HEIGHT / 2
    
    # Outer fill (clears background pattern)
    dwg.add(dwg.circle(center=(cx, cy), r=center_radius, fill=COLOR_BG_PURPLE, stroke="none"))
    
    # Outer double border
    # Thick outer
    dwg.add(dwg.circle(center=(cx, cy), r=center_radius, fill="none", stroke=COLOR_STROKE, stroke_width=5))
    # Thin inner
    dwg.add(dwg.circle(center=(cx, cy), r=center_radius - 12, fill="none", stroke=COLOR_STROKE, stroke_width=2))

    # Save the file
    dwg.save()
    print(f"SVG generated: {filename}")

if __name__ == "__main__":
    generate_money_template_svg()