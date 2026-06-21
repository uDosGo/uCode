"""CLI main — Command-line interface for uCode4 spatial/3D operations."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional, Tuple

from ucode4 import __version__
from ucode4.world.engine import WorldEngine
from ucode4.scene.manager import SceneManager
from ucode4.camera.system import Camera, CameraSystem
from ucode4.renderer.renderer import Renderer, RenderConfig
from ucode4.portal.portal import PortalSystem
from ucode4.spatial.index import SpatialIndex, SpatialQuery
from ucode4.persistence.store import Persistence, WorldStore


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ucode4",
        description="uCode4 — Spatial/3D Layer: Virtual worlds and spatial computing",
    )
    parser.add_argument(
        "--version", action="version", version=f"ucode4 {__version__}"
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # world
    world_p = sub.add_parser("world", help="3D world operations")
    world_sub = world_p.add_subparsers(dest="world_cmd", help="World commands")
    world_create = world_sub.add_parser("create", help="Create a new world")
    world_create.add_argument("--name", required=True, help="World name")
    world_create.add_argument("--band", type=int, default=400, help="Layer band (400-499)")
    world_create.add_argument("--width", type=float, default=100.0)
    world_create.add_argument("--height", type=float, default=100.0)
    world_create.add_argument("--depth", type=float, default=100.0)
    world_sub.add_parser("list", help="List all worlds")

    # scene
    scene_p = sub.add_parser("scene", help="Scene composition")
    scene_sub = scene_p.add_subparsers(dest="scene_cmd", help="Scene commands")
    scene_create = scene_sub.add_parser("create", help="Create a new scene")
    scene_create.add_argument("--name", required=True, help="Scene name")
    scene_create.add_argument("--world", required=True, help="World ID")
    scene_add = scene_sub.add_parser("add", help="Add object to scene")
    scene_add.add_argument("--scene", required=True, help="Scene ID")
    scene_add.add_argument("--name", required=True, help="Object name")
    scene_add.add_argument("--type", required=True, choices=["sprite", "bob", "text", "model", "light"])
    scene_add.add_argument("--x", type=float, default=0.0)
    scene_add.add_argument("--y", type=float, default=0.0)
    scene_add.add_argument("--z", type=float, default=0.0)

    # camera
    cam_p = sub.add_parser("camera", help="Camera control")
    cam_sub = cam_p.add_subparsers(dest="camera_cmd", help="Camera commands")
    cam_set = cam_sub.add_parser("set", help="Set camera position")
    cam_set.add_argument("--x", type=float, default=0.0)
    cam_set.add_argument("--y", type=float, default=0.0)
    cam_set.add_argument("--z", type=float, default=10.0)
    cam_orbit = cam_sub.add_parser("orbit", help="Orbit camera")
    cam_orbit.add_argument("--angle", type=float, required=True)
    cam_orbit.add_argument("--radius", type=float, default=10.0)

    # render
    render_p = sub.add_parser("render", help="Render world/scene")
    render_p.add_argument("--scene", required=True, help="Scene ID")
    render_p.add_argument("--output", default="output.json", help="Output file")
    render_p.add_argument("--width", type=int, default=800)
    render_p.add_argument("--height", type=int, default=600)

    # portal
    portal_p = sub.add_parser("portal", help="Portal operations")
    portal_sub = portal_p.add_subparsers(dest="portal_cmd", help="Portal commands")
    portal_create = portal_sub.add_parser("create", help="Create a portal")
    portal_create.add_argument("--name", required=True)
    portal_create.add_argument("--from-world", required=True)
    portal_create.add_argument("--to-world", required=True)
    portal_create.add_argument("--from-x", type=float, default=0.0)
    portal_create.add_argument("--from-y", type=float, default=0.0)
    portal_create.add_argument("--from-z", type=float, default=0.0)
    portal_create.add_argument("--to-x", type=float, default=0.0)
    portal_create.add_argument("--to-y", type=float, default=0.0)
    portal_create.add_argument("--to-z", type=float, default=0.0)

    # spatial
    spatial_p = sub.add_parser("spatial", help="Spatial queries")
    spatial_sub = spatial_p.add_subparsers(dest="spatial_cmd", help="Spatial commands")
    spatial_query = spatial_sub.add_parser("query", help="Query entities within radius")
    spatial_query.add_argument("--x", type=float, default=0.0)
    spatial_query.add_argument("--y", type=float, default=0.0)
    spatial_query.add_argument("--z", type=float, default=0.0)
    spatial_query.add_argument("--radius", type=float, default=10.0)

    return parser


def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    engine = WorldEngine()
    scene_mgr = SceneManager()
    cam_sys = CameraSystem()
    portal_sys = PortalSystem()
    spatial_idx = SpatialIndex()
    persistence = Persistence()

    if args.command == "world":
        if args.world_cmd == "create":
            world = engine.create_world(
                name=args.name,
                band=args.band,
                width=args.width,
                height=args.height,
                depth=args.depth,
            )
            print(f"✅ World created: {world.name} (ID: {world.world_id})")
            print(f"   Band: {world.dimension.band}")
            print(f"   Bounds: {world.dimension.bounds}")
        elif args.world_cmd == "list":
            worlds = engine.list_worlds()
            if not worlds:
                print("No worlds created yet.")
            else:
                for w in worlds:
                    print(f"  {w.world_id[:8]}  {w.name}  (band {w.dimension.band})")

    elif args.command == "scene":
        if args.scene_cmd == "create":
            scene = scene_mgr.create_scene(name=args.name, world_id=args.world)
            print(f"✅ Scene created: {scene.name} (ID: {scene.scene_id})")
        elif args.scene_cmd == "add":
            obj = scene_mgr.add_object_to_scene(
                scene_id=args.scene,
                name=args.name,
                object_type=args.type,
                position=(args.x, args.y, args.z),
            )
            if obj:
                print(f"✅ Object added: {obj.name} ({obj.object_type}) at {obj.position}")
            else:
                print(f"❌ Scene not found: {args.scene}")

    elif args.command == "camera":
        if args.camera_cmd == "set":
            cam = cam_sys.create_camera(name="default", position=(args.x, args.y, args.z))
            print(f"✅ Camera set at ({args.x}, {args.y}, {args.z})")
        elif args.camera_cmd == "orbit":
            cam: Optional[Camera] = cam_sys.active_camera
            if cam:
                cam.orbit(args.angle, args.radius)
                print(f"✅ Camera orbited to {cam.position}")
            else:
                print("❌ No active camera. Create one with `camera set` first.")

    elif args.command == "render":
        scene = scene_mgr.get_scene(args.scene)
        if not scene:
            print(f"❌ Scene not found: {args.scene}")
            return
        config = RenderConfig(width=args.width, height=args.height)
        renderer = Renderer(config=config)
        result = renderer.export_scene(scene.to_dict(), args.output)
        print(f"✅ Scene rendered to {result}")

    elif args.command == "portal":
        if args.portal_cmd == "create":
            portal = portal_sys.create_portal(
                name=args.name,
                source_world_id=args.from_world,
                target_world_id=args.to_world,
                source_position=(args.from_x, args.from_y, args.from_z),
                target_position=(args.to_x, args.to_y, args.to_z),
            )
            print(f"✅ Portal created: {portal.name} (ID: {portal.portal_id})")
            print(f"   {args.from_world[:8]} → {args.to_world[:8]}")

    elif args.command == "spatial":
        if args.spatial_cmd == "query":
            query = SpatialQuery(
                center=(args.x, args.y, args.z),
                radius=args.radius,
            )
            results = spatial_idx.query(query)
            print(f"Found {len(results)} entities within {args.radius} units")
            for e in results:
                print(f"  {e.entity_id[:8]}  {e.entity_type}  at {e.position}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
