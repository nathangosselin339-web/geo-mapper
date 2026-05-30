import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from map_engine import MapEngine, BLOCK_COLORS
from paint_net_bridge import PaintNetBridge
from minecraft_listener import MinecraftListener


def print_usage():
    print("Paint.NET GeoMapper for Minecraft")
    print()
    print("Usage:")
    print("  python main.py <reference_image> [options]")
    print()
    print("Options:")
    print("  --origin X Z         World origin (default: 0 0)")
    print("  --scale N            Blocks per pixel (default: 1)")
    print("  --tcp                Listen for Fabric mod data")
    print("  --port N             TCP port (default: 19528)")
    print()
    print("Correct placement -> green pixel, Wrong placement -> red pixel")
    print()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "/?"):
        print_usage()
        return

    ref_path = sys.argv[1]
    if not Path(ref_path).exists():
        print(f"Error: File not found: {ref_path}")
        return

    origin_x, origin_z = 0, 0
    scale = 1.0
    use_tcp = False
    port = 19528

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--origin" and i + 2 < len(args):
            origin_x, origin_z = int(args[i + 1]), int(args[i + 2])
            i += 3
        elif args[i] == "--scale" and i + 1 < len(args):
            scale = float(args[i + 1])
            i += 2
        elif args[i] == "--tcp":
            use_tcp = True
            i += 1
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        else:
            i += 1

    engine = MapEngine(ref_path, block_scale=scale)
    bridge = PaintNetBridge(ref_path)

    print("Opening reference image in Paint.NET...")
    bridge.open_reference()

    print("Quantizing reference image to Minecraft blocks...")
    engine.generate_plan()
    stats = engine.get_stats()
    print(f"  Build plan: {stats['total']} positions, {len(BLOCK_COLORS)} block types")

    plan_img = engine.generate_build_plan_image()
    bridge.open_in_paintnet(plan_img, "geomap_build_plan")
    print("  Build plan opened in Paint.NET")

    def on_command(cmd):
        if cmd == "reset":
            engine.completed.clear()
            engine.wrong.clear()
            bridge._overlay_pasted = False
            print("Progress reset")
        elif cmd == "stats":
            s = engine.get_stats()
            print(f"Stats: {s['completed']}/{s['total']} ({s['progress_pct']:.1f}%)  {s['wrong']} wrong  {s['remaining']} remaining")

    listener = MinecraftListener(lambda wx, wz, blk: None, on_command=on_command)
    listener.set_origin(origin_x, origin_z)

    def on_block_place(wx, wz, block_id):
        correct, (px, py), expected = engine.check_placement(
            wx, wz, block_id, listener.origin_x, listener.origin_z
        )
        if expected is None:
            return
        label = "CORRECT" if correct else "WRONG"
        expected_name = expected.replace("minecraft:", "")
        placed_name = block_id.replace("minecraft:", "")
        print(f"[{label}] @ ({wx},{wz}) px=({px},{py}) expect={expected_name} got={placed_name}")

        overlay_img = engine.generate_overlay()
        bridge.update_overlay(overlay_img)

        s = engine.get_stats()
        print(
            f"  {s['completed']}/{s['total']} ({s['progress_pct']:.1f}%)  "
            f"{s['wrong']} wrong  {s['remaining']} remaining"
        )

    listener.on_place = on_block_place

    print(f"  Origin: ({origin_x}, {origin_z})  Scale: {scale}")
    print(f"  Each pixel = {scale} block(s)")
    if use_tcp:
        print(f"  TCP server on {listener.host}:{listener.port}")
        listener.start_tcp_server()
    print()
    print("Manual input:  x z block_id")
    print("  Example: 0 0 minecraft:red_wool")
    if use_tcp:
        print("  Or use the Fabric mod with --tcp")
    print("  Commands: reset, stats, origin <x> <z>, exit")
    print()
    listener.start_manual_input()
    listener.stop()


if __name__ == "__main__":
    main()
