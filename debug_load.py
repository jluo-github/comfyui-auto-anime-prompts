import importlib.util
import os
import sys

# Add the parent directory of 'comfyui-auto-anime-prompts' to sys.path
# This simulates 'comfyui-auto-anime-prompts' being in 'custom_nodes'
repo_root = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(repo_root)

# We want to import 'comfyui-auto-anime-prompts' as a module
# But it has hyphens, so we can't just 'import comfyui-auto-anime-prompts'
# We have to use importlib
module_name = "comfyui_auto_anime_prompts"
module_path = os.path.join(repo_root, "__init__.py")

spec = importlib.util.spec_from_file_location(module_name, module_path)
if spec and spec.loader:
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    print(f"Successfully loaded {module_name}")

    if hasattr(module, "NODE_CLASS_MAPPINGS"):
        print("NODE_CLASS_MAPPINGS found:")
        for k, v in module.NODE_CLASS_MAPPINGS.items():
            print(f"  - {k}: {v}")
    else:
        print("NODE_CLASS_MAPPINGS NOT found")

    if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
        print("NODE_DISPLAY_NAME_MAPPINGS found:")
        for k, v in module.NODE_DISPLAY_NAME_MAPPINGS.items():
            print(f"  - {k}: {v}")
