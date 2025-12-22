import os
import sys
import af # pyright: ignore[reportMissingImports]
import argparse
from typing import List

from dataclasses import dataclass, field
from pathlib import Path

from af_renderfarm.config import AFConfig

@dataclass
class Command:
    title: str
    command: str

@dataclass
class CommandBlock:
    title: str 
    commands: List[Command] = field(default_factory=list)
    service: str = 'generic'

@dataclass
class Job:
    name: str
    working_directory: str
    start_frame: int
    end_frame: int
    frames_per_task: int = 1
    command_blocks: list[CommandBlock] = field(default_factory=list)


def submit_af_job(job: Job, parser: str = "generic") -> None:
    af_job = af.Job(job.name)
    for cmd_block in job.command_blocks:
        block = af.Block(cmd_block.title, cmd_block.service)
        block.setWorkingDirectory(
            working_directory=str(job.working_directory)
        )
        block.setParser(parser=parser)
        if len(cmd_block.commands) > 1:
            for cmd in cmd_block.commands:
                task = af.Task(cmd.title)
                task.setCommand(cmd.command)
                block.tasks.append(task)
        elif len(cmd_block.commands) == 1:
            cmd = cmd_block.commands[0]
            block.setNumeric(job.start_frame, job.end_frame, job.frames_per_task)
            block.setCommand(cmd.command)

        af_job.blocks.append(block)

    af_job.output()
    af_job.send()