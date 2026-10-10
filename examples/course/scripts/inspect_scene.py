"""唯讀場景報告：在 Blender 執行；不改資料、不寫檔、不需額外套件。
可在 Text Editor 執行，或以 Blender --background FILE --python 本腳本執行。
只列出目前場景的物件；location / scale 是物件的本地變換值。
"""
import json
import bpy


def inspect_scene():
    scene = bpy.context.scene
    return {
        'version': bpy.app.version_string,
        'scene': scene.name,
        'objects': [
            {
                'name': obj.name,
                'type': obj.type,
                'location': list(obj.location),
                'scale': list(obj.scale),
                'collections': sorted(collection.name for collection in obj.users_collection),
            }
            for obj in sorted(scene.objects, key=lambda obj: obj.name)
        ],
    }


if __name__ == '__main__':
    print(json.dumps(inspect_scene(), ensure_ascii=False, indent=2))
