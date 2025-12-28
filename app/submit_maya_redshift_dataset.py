import argparse
from enum import Enum
import os

from af_renderfarm.config import AFConfig
from af_renderfarm.submitters.maya_redshift import submit_maya_redshift_job

OPTIX_DENOISE = 3
DENOISE_OFF = 0

THRESHOLDS = {
    0: (0.001, 2000, True),
    1: (0.015, 2000, False),
    2: (0.025, 20900, False),
    3: (0.1, 2000, False),
    4: (0.3, 2000, False),
}

class QualityPreset(Enum):
    GT          = 0
    HIGH        = 1
    MEDIUM      = 2
    LOW         = 3
    AGGRESSIVE  = 4


def get_render_settings(quality: QualityPreset) -> dict:
    denoise_engine = OPTIX_DENOISE if THRESHOLDS[quality.value][2] else DENOISE_OFF
    return (
        f'setAttr redshiftOptions.unifiedAdaptiveErrorThreshold {THRESHOLDS[quality.value][0]};'
        f'setAttr "redshiftOptions.unifiedRandomizePattern" 1;'
        f'setAttr "redshiftOptions.unifiedMaxSamples" {THRESHOLDS[quality.value][1]};'
        f'setAttr redshiftOptions.denoiseEngine {denoise_engine};'
        f'setAttr rsAov_Cryptomatte.enabled 0;'
        f'setAttr rsAov_Custom.enabled 0;'
        f'setAttr rsAov_Depth.enabled 0;'
        f'setAttr rsAov_PuzzleMatte.enabled 0;'
        f'setAttr rsAov_PuzzleMatte1.enabled 0;'
        f'setAttr rsAov_WorldPosition.enabled 0;'
    )


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Submit Maya Redshift Render Job to Af Render Farm")
    parser.add_argument("--job_name", type=str, default="", help="Name of the render job")
    parser.add_argument("--scene", type=str, help="Path to the Maya scene file")
    parser.add_argument("--start", type=int, help="Start frame of the render")
    parser.add_argument("--end", type=int, help="End frame of the render")
    parser.add_argument(
        "--quality",
        type=str,
        help="Render quality preset(GT, HIGH, MEDIUM, LOW, AGGRESSIVE)",
        choices=[q.name for q in QualityPreset] + [""],
        default="")
    parser.add_argument("--project_dir", type=str, help="Maya project directory")
    parser.add_argument("--output", type=str, help="Output directory for rendered images")
    parser.add_argument("--frames-per-task", type=int, default=5, help="Number of frames per task")
    parser.add_argument("--pre-render-script", type=str, default="", help="Path to pre-render script")
    parser.add_argument("--log-level", type=int, default=2, help="Log level for Redshift renderer")

    return parser


if __name__ == "__main__":
    config = AFConfig()
    arg_parser = build_argparser()
    args = arg_parser.parse_args()

    proj_dir = args.project_dir or config.working_directory
    out_dir = args.output or config.output_image_dir

    if not out_dir:
        raise ValueError("Output directory must be specified via --output or AF_OUTPUT_IMAGE_DIR env variable.")

    if args.quality:
        quality = [QualityPreset[args.quality.upper()]]
    else:
        quality = sorted([q for q in QualityPreset], key=lambda x: x.value, reverse=True)

    for q in quality:
        job_name = f"{os.path.basename(os.path.splitext(args.scene)[0])}-render-{q.name.lower()}" or args.job_name
        output_dir = os.path.join(out_dir.strip('"'), job_name)
        submit_maya_redshift_job(
            job_name=job_name,
            project_dir=proj_dir,
            scene_file=args.scene,
            output_path=output_dir,
            start_frame=args.start,
            end_frame=args.end,
            frames_per_task=args.frames_per_task,
            pre_render_script=get_render_settings(q) + args.pre_render_script,
            log_level=args.log_level
        )