import os
import subprocess

from af_renderfarm.config import AFConfig
from af_renderfarm.af_job import Command, Job, CommandBlock, submit_af_job


def build_render_command(
        scene_file: str,
        project_dir: str,
        output_path: str,
        pre_render_script: str = "",
        log_level: int = 2,
    ) -> str:
    config = AFConfig()

    exe = config.maya_render_exec.rstrip('\\/').strip('"').strip("'")
    wrapper = config.maya_redshift_wrapper.rstrip('\\/').strip('"').strip("'")

    argv: list[str] = []
    if wrapper:
        argv.extend([wrapper, exe])
    else:
        argv.append(exe)

    proj = os.path.normpath(project_dir)
    proj = proj.rstrip('\\/').strip('"').strip("'")
    out = os.path.normpath(output_path)
    if not out.endswith(os.sep):
        out += os.sep
    image_name = os.path.splitext(os.path.basename(scene_file))[0]

    pre_render_cmd = (
        f'optionVar -iv useOpenCL 0;'
        f'catchQuiet(`evaluationManager -mode off`);'
        f'setAttr redshiftOptions.logLevel {log_level};'
        f'{pre_render_script}'
    )

    parts = argv + [
        "-r", "redshift",
        "-proj", proj,
        "-rd", out,
        "-of", "exr",
        "-im", image_name,
    ]
    if pre_render_cmd:
        parts.extend(["-preRender", pre_render_cmd])

    parts.extend([
        "-s", "@####@",
        "-e", "@####@",
        scene_file,
    ])

    return subprocess.list2cmdline(parts)


def create_maya_redshift_job(
    job_name: str,
    project_dir: str,
    scene_file: str,
    output_path: str,
    start_frame: int,
    end_frame: int,
    frames_per_task: int = 1,
    pre_render_script: str = "",
    log_level: int = 2,
) -> Job:
    command_str = build_render_command(
        scene_file=scene_file,
        project_dir=project_dir,
        output_path=output_path,
        pre_render_script=pre_render_script,
        log_level=log_level
    )
    command = Command(
        title="Maya Redshift Render",
        command=command_str
    )
    command_block = CommandBlock(
        title="Render Block",
        commands=[command],
        service="generic"
    )
    job = Job(
        name=job_name,
        working_directory=project_dir,
        start_frame=start_frame,
        end_frame=end_frame,
        frames_per_task=frames_per_task,
        command_blocks=[command_block]
    )
    return job


def submit_maya_redshift_job(
    job_name: str,
    project_dir: str,
    scene_file: str,
    output_path: str,
    start_frame: int,
    end_frame: int,
    frames_per_task: int = 1,
    pre_render_script: str = "",
    log_level: int = 2,
) -> None:
    
    job = create_maya_redshift_job(
        job_name=job_name,
        project_dir=project_dir,
        scene_file=scene_file,
        output_path=output_path,
        start_frame=start_frame,
        end_frame=end_frame,
        frames_per_task=frames_per_task,
        pre_render_script=pre_render_script,
        log_level=log_level
    )
    submit_af_job(job)