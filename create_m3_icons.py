import zlib
import struct
import math
import os

def create_png(width, height, draw_func, filename):
    raw_data = bytearray()
    for y in range(height):
        raw_data.append(0) # filter type 0 (None)
        for x in range(width):
            r, g, b, a = draw_func(x, y, width, height)
            raw_data.extend([r, g, b, a])
            
    def chunk(tag, data):
        return struct.pack('>I', len(data)) + tag + data + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    idat = zlib.compress(bytes(raw_data), 9)

    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', idat) + chunk(b'IEND', b'')

    with open(filename, 'wb') as f:
        f.write(png)

def draw_m3_rss_icon(x, y, w, h):
    # Normalized coordinates 0.0 to 1.0
    nx = (x + 0.5) / float(w)
    ny = (y + 0.5) / float(h)
    
    # Rounded squircle container with radius ~0.24
    cx, cy = 0.5, 0.5
    dx = abs(nx - cx)
    dy = abs(ny - cy)
    corner_r = 0.22
    edge = 0.5 - corner_r
    
    alpha = 1.0
    if dx > edge and dy > edge:
        dist = math.hypot(dx - edge, dy - edge)
        if dist > corner_r:
            return (0, 0, 0, 0) # Outside rounded corners
        elif dist > corner_r - (1.5 / w):
            alpha = max(0.0, min(1.0, (corner_r - dist) / (1.5 / w)))

    # Material 3 Primary background (#5B6400 -> r:91, g:100, b:0)
    # Subtle vertical gradient to give M3 depth
    grad = 1.0 - (ny * 0.12)
    bg_r = int(min(255, 91 * grad))
    bg_g = int(min(255, 100 * grad))
    bg_b = int(min(255, 0 * grad))
    
    # RSS symbol elements:
    # Origin of concentric circles is near bottom-left: (ox, oy) = (0.26, 0.74)
    ox, oy = 0.26, 0.74
    dist_origin = math.hypot(nx - ox, oy - ny)
    
    # RSS dot: center at (ox, oy), radius ~0.075
    dot_r = 0.075
    pixel_w = 1.5 / w
    is_symbol = False
    sym_alpha = 0.0
    
    if dist_origin <= dot_r:
        is_symbol = True
        if dist_origin > dot_r - pixel_w:
            sym_alpha = (dot_r - dist_origin) / pixel_w
        else:
            sym_alpha = 1.0
            
    # Wave 1: inner radius 0.22, outer radius 0.32, in upper-right quadrant from (ox, oy)
    # Check quadrant: nx >= ox - 0.01 and ny <= oy + 0.01
    in_quadrant = (nx >= ox - 0.02) and (ny <= oy + 0.02)
    
    # Wave 1
    w1_in, w1_out = 0.21, 0.31
    if in_quadrant and (w1_in - pixel_w <= dist_origin <= w1_out + pixel_w):
        # Angle check for nice rounded ends
        if nx >= ox and ny <= oy:
            d_mid = abs(dist_origin - (w1_in + w1_out) / 2.0)
            half_thickness = (w1_out - w1_in) / 2.0
            if d_mid <= half_thickness:
                edge_dist = half_thickness - d_mid
                curr_alpha = min(1.0, max(0.0, edge_dist / pixel_w))
                if curr_alpha > sym_alpha:
                    sym_alpha = curr_alpha
                    is_symbol = True
                    
    # Wave 2
    w2_in, w2_out = 0.40, 0.50
    if in_quadrant and (w2_in - pixel_w <= dist_origin <= w2_out + pixel_w):
        if nx >= ox and ny <= oy:
            d_mid = abs(dist_origin - (w2_in + w2_out) / 2.0)
            half_thickness = (w2_out - w2_in) / 2.0
            if d_mid <= half_thickness:
                edge_dist = half_thickness - d_mid
                curr_alpha = min(1.0, max(0.0, edge_dist / pixel_w))
                if curr_alpha > sym_alpha:
                    sym_alpha = curr_alpha
                    is_symbol = True

    # Color blending
    # Symbol color: On-Primary (#FFFFFF / Crisp White)
    sym_r, sym_g, sym_b = 255, 255, 255
    
    if is_symbol and sym_alpha > 0:
        final_r = int(bg_r * (1.0 - sym_alpha) + sym_r * sym_alpha)
        final_g = int(bg_g * (1.0 - sym_alpha) + sym_g * sym_alpha)
        final_b = int(bg_b * (1.0 - sym_alpha) + sym_b * sym_alpha)
    else:
        final_r, final_g, final_b = bg_r, bg_g, bg_b
        
    return (final_r, final_g, final_b, int(alpha * 255))

if __name__ == '__main__':
    create_png(192, 192, draw_m3_rss_icon, 'icon-192.png')
    create_png(512, 512, draw_m3_rss_icon, 'icon-512.png')
    print("M3 icons generated successfully!")
