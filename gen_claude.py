import math

def generate_monopoly_card_svg():
    width = 732
    height = 1101
    
    # Colors - adjusted to match the image more closely
    border_color = "#2a2020"  # Dark brownish border
    fill_color = "#9B7BB8"    # Main purple fill
    pattern_color = "#5D4175" # Darker purple for patterns
    light_fill = "#C4A8D8"    # Lighter purple for circle fills
    
    # Measurements
    outer_border = 14
    
    # Guilloche border dimensions
    guilloche_outer_x = 42
    guilloche_outer_y = 42
    guilloche_thickness = 58
    guilloche_inner_x = guilloche_outer_x + guilloche_thickness
    guilloche_inner_y = guilloche_outer_y + guilloche_thickness
    
    inner_width = width - 2 * guilloche_inner_x
    inner_height = height - 2 * guilloche_inner_y
    
    # Center circle
    center_x = width / 2
    center_y = height / 2
    large_circle_radius = 160
    
    # Corner circles
    corner_circle_radius = 40
    corner_offset_x = 88
    corner_offset_y = 88
    
    svg_parts = []
    
    # SVG header
    svg_parts.append(f'''<svg xmlns="http://www.w3.org/2000/svg" 
     width="{width}" height="{height}" 
     viewBox="0 0 {width} {height}">
''')
    
    # Definitions for patterns
    svg_parts.append('  <defs>\n')
    
    # Rosette pattern for background - concentric circles with subtle texture
    rosette_size = 52
    svg_parts.append(f'''    <pattern id="rosettePattern" x="0" y="0" width="{rosette_size}" height="{rosette_size}" patternUnits="userSpaceOnUse">
      <rect width="{rosette_size}" height="{rosette_size}" fill="{fill_color}"/>
''')
    
    # Create concentric circle rosette with more rings
    rcx = rosette_size / 2
    rcy = rosette_size / 2
    for r in [24, 21, 18, 15, 12, 9, 6]:
        svg_parts.append(f'      <circle cx="{rcx}" cy="{rcy}" r="{r}" fill="none" stroke="{pattern_color}" stroke-width="0.6" opacity="0.35"/>\n')
    
    # Add radiating lines
    num_rays = 24
    for i in range(num_rays):
        angle = (2 * math.pi * i) / num_rays
        x1 = rcx + 4 * math.cos(angle)
        y1 = rcy + 4 * math.sin(angle)
        x2 = rcx + 24 * math.cos(angle)
        y2 = rcy + 24 * math.sin(angle)
        svg_parts.append(f'      <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{pattern_color}" stroke-width="0.4" opacity="0.25"/>\n')
    
    svg_parts.append('    </pattern>\n\n')
    
    # Create a more detailed guilloche wave pattern
    svg_parts.append(f'''    <pattern id="guillocheH" x="0" y="0" width="32" height="{guilloche_thickness}" patternUnits="userSpaceOnUse">
''')
    # Multiple interleaving sine waves
    for offset in range(4, int(guilloche_thickness) - 4, 5):
        phase = (offset * 0.3) % (2 * math.pi)
        path_d = f'M0,{offset}'
        for x in range(1, 33):
            y = offset + 3 * math.sin(x * 0.4 + phase)
            path_d += f' L{x},{y:.2f}'
        svg_parts.append(f'      <path d="{path_d}" fill="none" stroke="{pattern_color}" stroke-width="0.6" opacity="0.6"/>\n')
    svg_parts.append('    </pattern>\n\n')
    
    svg_parts.append(f'''    <pattern id="guillocheV" x="0" y="0" width="{guilloche_thickness}" height="32" patternUnits="userSpaceOnUse">
''')
    for offset in range(4, int(guilloche_thickness) - 4, 5):
        phase = (offset * 0.3) % (2 * math.pi)
        path_d = f'M{offset},0'
        for y in range(1, 33):
            x = offset + 3 * math.sin(y * 0.4 + phase)
            path_d += f' L{x:.2f},{y}'
        svg_parts.append(f'      <path d="{path_d}" fill="none" stroke="{pattern_color}" stroke-width="0.6" opacity="0.6"/>\n')
    svg_parts.append('    </pattern>\n\n')
    
    svg_parts.append('  </defs>\n\n')
    
    # Background - outer black border
    svg_parts.append(f'  <!-- Outer dark border -->\n')
    svg_parts.append(f'  <rect x="0" y="0" width="{width}" height="{height}" fill="{border_color}"/>\n\n')
    
    # Main purple fill area
    svg_parts.append(f'  <!-- Main purple fill -->\n')
    svg_parts.append(f'  <rect x="{outer_border}" y="{outer_border}" width="{width - 2*outer_border}" height="{height - 2*outer_border}" fill="{fill_color}"/>\n\n')
    
    # Rosette pattern background in inner area
    svg_parts.append(f'  <!-- Rosette pattern background -->\n')
    svg_parts.append(f'  <rect x="{guilloche_inner_x}" y="{guilloche_inner_y}" width="{inner_width}" height="{inner_height}" fill="url(#rosettePattern)"/>\n\n')
    
    # ===== GUILLOCHE BORDER FRAME =====
    svg_parts.append(f'  <!-- Guilloche border frame -->\n')
    svg_parts.append(f'  <g id="guillocheFrame">\n')
    
    # Outer decorative lines of guilloche frame
    for i, offset in enumerate([0, 3, 6]):
        sw = 2.5 if i == 0 else 1.0
        svg_parts.append(f'    <rect x="{guilloche_outer_x + offset}" y="{guilloche_outer_y + offset}" ')
        svg_parts.append(f'width="{width - 2*(guilloche_outer_x + offset)}" height="{height - 2*(guilloche_outer_y + offset)}" ')
        svg_parts.append(f'fill="none" stroke="{pattern_color}" stroke-width="{sw}"/>\n')
    
    # Inner decorative lines of guilloche frame
    for i, offset in enumerate([0, 3, 6]):
        sw = 2.5 if i == 0 else 1.0
        inner_rect_x = guilloche_inner_x - offset
        inner_rect_y = guilloche_inner_y - offset
        svg_parts.append(f'    <rect x="{inner_rect_x}" y="{inner_rect_y}" ')
        svg_parts.append(f'width="{width - 2*inner_rect_x}" height="{height - 2*inner_rect_y}" ')
        svg_parts.append(f'fill="none" stroke="{pattern_color}" stroke-width="{sw}"/>\n')
    
    svg_parts.append(f'  </g>\n\n')
    
    # ===== GUILLOCHE WAVE PATTERNS IN BORDER =====
    svg_parts.append(f'  <!-- Guilloche wave patterns -->\n')
    
    # Create guilloche patterns using manual wave generation
    wave_amplitude = 4
    wave_frequency = 0.12
    line_spacing = 5
    
    # TOP BORDER guilloche waves
    svg_parts.append(f'  <g id="topGuillocheWaves">\n')
    for line_num in range(10):
        y_base = guilloche_outer_y + 10 + line_num * line_spacing
        if y_base > guilloche_inner_y - 10:
            break
        phase = line_num * 0.5
        path_d = f'M{guilloche_outer_x + 10},{y_base}'
        for x in range(int(guilloche_outer_x + 11), int(width - guilloche_outer_x - 10)):
            y = y_base + wave_amplitude * math.sin(x * wave_frequency + phase)
            path_d += f' L{x},{y:.2f}'
        svg_parts.append(f'    <path d="{path_d}" fill="none" stroke="{pattern_color}" stroke-width="0.7" opacity="0.65"/>\n')
    svg_parts.append(f'  </g>\n\n')
    
    # BOTTOM BORDER guilloche waves
    svg_parts.append(f'  <g id="bottomGuillocheWaves">\n')
    for line_num in range(10):
        y_base = height - guilloche_outer_y - 10 - line_num * line_spacing
        if y_base < height - guilloche_inner_y + 10:
            break
        phase = line_num * 0.5
        path_d = f'M{guilloche_outer_x + 10},{y_base}'
        for x in range(int(guilloche_outer_x + 11), int(width - guilloche_outer_x - 10)):
            y = y_base + wave_amplitude * math.sin(x * wave_frequency + phase)
            path_d += f' L{x},{y:.2f}'
        svg_parts.append(f'    <path d="{path_d}" fill="none" stroke="{pattern_color}" stroke-width="0.7" opacity="0.65"/>\n')
    svg_parts.append(f'  </g>\n\n')
    
    # LEFT BORDER guilloche waves
    svg_parts.append(f'  <g id="leftGuillocheWaves">\n')
    for line_num in range(10):
        x_base = guilloche_outer_x + 10 + line_num * line_spacing
        if x_base > guilloche_inner_x - 10:
            break
        phase = line_num * 0.5
        path_d = f'M{x_base},{guilloche_outer_y + 10}'
        for y in range(int(guilloche_outer_y + 11), int(height - guilloche_outer_y - 10)):
            x = x_base + wave_amplitude * math.sin(y * wave_frequency + phase)
            path_d += f' L{x:.2f},{y}'
        svg_parts.append(f'    <path d="{path_d}" fill="none" stroke="{pattern_color}" stroke-width="0.7" opacity="0.65"/>\n')
    svg_parts.append(f'  </g>\n\n')
    
    # RIGHT BORDER guilloche waves  
    svg_parts.append(f'  <g id="rightGuillocheWaves">\n')
    for line_num in range(10):
        x_base = width - guilloche_outer_x - 10 - line_num * line_spacing
        if x_base < width - guilloche_inner_x + 10:
            break
        phase = line_num * 0.5
        path_d = f'M{x_base},{guilloche_outer_y + 10}'
        for y in range(int(guilloche_outer_y + 11), int(height - guilloche_outer_y - 10)):
            x = x_base + wave_amplitude * math.sin(y * wave_frequency + phase)
            path_d += f' L{x:.2f},{y}'
        svg_parts.append(f'    <path d="{path_d}" fill="none" stroke="{pattern_color}" stroke-width="0.7" opacity="0.65"/>\n')
    svg_parts.append(f'  </g>\n\n')
    
    # Corner diagonal patterns (where borders meet)
    svg_parts.append(f'  <!-- Corner diagonal patterns -->\n')
    svg_parts.append(f'  <g id="cornerPatterns">\n')
    
    # Top-left corner diagonals
    for i in range(0, guilloche_thickness - 5, 4):
        svg_parts.append(f'    <line x1="{guilloche_outer_x + i + 8}" y1="{guilloche_outer_y + 8}" ')
        svg_parts.append(f'x2="{guilloche_outer_x + 8}" y2="{guilloche_outer_y + i + 8}" ')
        svg_parts.append(f'stroke="{pattern_color}" stroke-width="0.5" opacity="0.5"/>\n')
    
    # Top-right corner diagonals
    for i in range(0, guilloche_thickness - 5, 4):
        svg_parts.append(f'    <line x1="{width - guilloche_outer_x - i - 8}" y1="{guilloche_outer_y + 8}" ')
        svg_parts.append(f'x2="{width - guilloche_outer_x - 8}" y2="{guilloche_outer_y + i + 8}" ')
        svg_parts.append(f'stroke="{pattern_color}" stroke-width="0.5" opacity="0.5"/>\n')
    
    # Bottom-left corner diagonals
    for i in range(0, guilloche_thickness - 5, 4):
        svg_parts.append(f'    <line x1="{guilloche_outer_x + i + 8}" y1="{height - guilloche_outer_y - 8}" ')
        svg_parts.append(f'x2="{guilloche_outer_x + 8}" y2="{height - guilloche_outer_y - i - 8}" ')
        svg_parts.append(f'stroke="{pattern_color}" stroke-width="0.5" opacity="0.5"/>\n')
    
    # Bottom-right corner diagonals
    for i in range(0, guilloche_thickness - 5, 4):
        svg_parts.append(f'    <line x1="{width - guilloche_outer_x - i - 8}" y1="{height - guilloche_outer_y - 8}" ')
        svg_parts.append(f'x2="{width - guilloche_outer_x - 8}" y2="{height - guilloche_outer_y - i - 8}" ')
        svg_parts.append(f'stroke="{pattern_color}" stroke-width="0.5" opacity="0.5"/>\n')
    
    svg_parts.append(f'  </g>\n\n')
    
    # ===== LARGE CENTER CIRCLE =====
    svg_parts.append(f'  <!-- Large center circle with double border -->\n')
    svg_parts.append(f'  <circle cx="{center_x}" cy="{center_y}" r="{large_circle_radius}" fill="{light_fill}"/>\n')
    svg_parts.append(f'  <circle cx="{center_x}" cy="{center_y}" r="{large_circle_radius}" fill="none" stroke="{pattern_color}" stroke-width="3.5"/>\n')
    svg_parts.append(f'  <circle cx="{center_x}" cy="{center_y}" r="{large_circle_radius - 10}" fill="none" stroke="{pattern_color}" stroke-width="2"/>\n\n')
    
    # ===== CORNER CIRCLES =====
    # Top-right corner circle
    tr_cx = width - corner_offset_x
    tr_cy = corner_offset_y
    # Bottom-left corner circle  
    bl_cx = corner_offset_x
    bl_cy = height - corner_offset_y
    
    svg_parts.append(f'  <!-- Corner circles with double borders -->\n')
    
    # Top-right
    svg_parts.append(f'  <circle cx="{tr_cx}" cy="{tr_cy}" r="{corner_circle_radius}" fill="{light_fill}"/>\n')
    svg_parts.append(f'  <circle cx="{tr_cx}" cy="{tr_cy}" r="{corner_circle_radius}" fill="none" stroke="{pattern_color}" stroke-width="2.5"/>\n')
    svg_parts.append(f'  <circle cx="{tr_cx}" cy="{tr_cy}" r="{corner_circle_radius - 6}" fill="none" stroke="{pattern_color}" stroke-width="1.5"/>\n')
    
    # Bottom-left
    svg_parts.append(f'  <circle cx="{bl_cx}" cy="{bl_cy}" r="{corner_circle_radius}" fill="{light_fill}"/>\n')
    svg_parts.append(f'  <circle cx="{bl_cx}" cy="{bl_cy}" r="{corner_circle_radius}" fill="none" stroke="{pattern_color}" stroke-width="2.5"/>\n')
    svg_parts.append(f'  <circle cx="{bl_cx}" cy="{bl_cy}" r="{corner_circle_radius - 6}" fill="none" stroke="{pattern_color}" stroke-width="1.5"/>\n\n')
    
    # Close SVG
    svg_parts.append('</svg>')
    
    return ''.join(svg_parts)


def main():
    svg_content = generate_monopoly_card_svg()
    
    output_path = '/mnt/user-data/outputs/monopoly_card.svg'
    with open(output_path, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG generated successfully: {output_path}")


if __name__ == "__main__":
    main()