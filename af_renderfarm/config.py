import os
from dataclasses import dataclass

@dataclass(frozen=True)
class AFConfig():
    working_directory: str = os.getenv("AF_WORKING_DIRECTORY", "")
    maya_render_exec: str = os.getenv("MAYA_RENDER_EXEC", "Render")
    maya_redshift_wrapper: str = os.getenv("MAYA_REDSHIFT_WRAPPER", "")
    output_image_dir: str = os.getenv("AF_OUTPUT_IMAGE_DIR", "")