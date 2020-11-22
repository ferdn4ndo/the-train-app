import glob
import multiprocessing
import os
import traceback
from functools import partial
from pathlib import Path
from typing import List

import cv2
from PIL import Image, ImageDraw

from app.common.logger import generate_logger, LoggerFolders
from app.common.threading import ThreadingExecutor
from app.simulation.exception.error import UnprocessableEntityError
from app.simulation.graph.font import H3Font
from app.simulation.graph.synoptic_panel import SynopticPanel
from app.simulation.model.simulation_frame import SimulationFrame
from app.simulation.model.simulation_results import SimulationResults


class SynopticPanelVideo:
    DEFAULT_OPTIONS = {
        'thread_renders': multiprocessing.cpu_count() * 5,
    }

    def __init__(self, results: SimulationResults, **options):
        self.options = self.DEFAULT_OPTIONS
        self.options.update(options)
        self.logger = generate_logger(results.simulation_uuid, LoggerFolders.SIMULATIONS)

        self.results = results
        self.total_frames = len(results.frames)

        if self.total_frames == 0:
            raise UnprocessableEntityError("Unable to export video: no frames in the simulation results!")

        sizes = set([SynopticPanel(results.sections, frame).get_content_size() for frame in results.frames])
        if len(sizes) > 1:
            raise UnprocessableEntityError("There are different sizes of frames: {}".format(", ".format(sizes)))

        self.image_size = SynopticPanel(results.sections, results.frames[0]).get_content_size()

    def get_video_filename(self):
        video_name = "simulation_{}.mp4".format(self.results.simulation_uuid)
        video_path = os.path.join(os.environ['DATA_DIR'], 'results', 'simulation_videos')
        Path(video_path).mkdir(parents=True, exist_ok=True)
        return os.path.join(video_path, video_name)

    def mark_frame(self, image, frame_to_render):
        draw = ImageDraw.Draw(image)
        font = H3Font().load()
        image_w, image_h = image.size

        left_text = "FRAME {} - COST {:.2f}".format(frame_to_render, self.results.frames[frame_to_render].total_cost)
        left_text_w, left_text_h = font.getsize(left_text)
        draw.text((5, 5), left_text, font=font)

        right_text = self.results.frames[frame_to_render].timestamp_formatted
        right_text_w, right_text_h = font.getsize(right_text)
        x_position = image_w - right_text_w - 5
        draw.text((x_position, 5), right_text, font=font)

        center_text = "{} [{}]".format(self.results.controller_name, self.results.simulation_uuid)
        center_text_w, center_test_h = font.getsize(center_text)
        x_position = left_text_w + (image_w - left_text_w - right_text_w)/2 - center_text_w/2
        draw.text((x_position, 5), center_text, font=font)
        return image

    def export_video(self, filename=None, fps=30):
        if not filename:
            filename = self.get_video_filename()
        filename = filename if filename[-4:] == 'avi' else '{}.avi'.format(filename)
        temp_file = '{}.original.avi'.format(filename[:-4])

        total_frames = len(self.results.frames)

        self.logger.info("Rendering {} frames...".format(total_frames))

        method = partial(render_single_frame, total_frames, self.results.sections)
        executor = ThreadingExecutor(method, self.options['thread_renders'])
        executor.run(self.results.frames)

        # retrieves the ordered list of rendered frames
        frames_folder = get_frames_folder(self.results.simulation_uuid)
        pattern = os.path.join(frames_folder, '*.jpg')
        files = sorted(glob.glob(pattern))

        self.logger.info("Marking frames...")
        for index, file in enumerate(files):
            image = Image.open(file)
            self.mark_frame(image, index)
            image.save(file)
            os.chown(file, int(os.environ['OUT_FILES_USER_ID']), int(os.environ['OUT_FILES_GROUP_ID']))

        self.logger.info("Exporting frames to video file...".format(total_frames))

        codec = cv2.VideoWriter_fourcc(*'XVID')
        video = cv2.VideoWriter(filename, codec, fps, self.image_size)
        for index, file in enumerate(files):
            video.write(cv2.imread(file))
        video.release()
        os.chown(filename, int(os.environ['OUT_FILES_USER_ID']), int(os.environ['OUT_FILES_GROUP_ID']))

        # delete the temp frames
        if os.environ['DELETE_TEMP_THUMBNAILS'] == 1:
            for file in files:
                os.remove(file)

        # self.logger.info("Encoding file...")
        # logging.disable(logging.INFO)
        #
        # stream = ffmpeg.input(temp_file)
        # stream = ffmpeg.output(stream, filename)
        # ffmpeg.run(stream, quiet=True)
        #
        # logging.disable(logging.NOTSET)
        #os.remove(temp_file)

        self.logger.info("Finished exporting video to '{}'".format(filename))


def get_frames_folder(simulation_uuid: str):
    filepath = os.path.join(os.environ['TEMP_DIR'], 'synoptic_panel_frames', simulation_uuid)
    Path(filepath).mkdir(parents=True, exist_ok=True)
    return filepath


def get_frame_filepath(frame: SimulationFrame):
    filepath = get_frames_folder(frame.simulation_uuid)
    return os.path.join(filepath, '{:08d}.jpg'.format(frame.index))


def render_single_frame(total_frames, sections: List, frame: SimulationFrame):
    logger = generate_logger(frame.simulation_uuid, LoggerFolders.SIMULATIONS)
    filepath = get_frame_filepath(frame)

    logger.debug("Rendering frame {} to {}".format(frame.index, filepath))

    try:
        synoptic = SynopticPanel(sections, frame)
        image = synoptic.render()
        image.save(filepath, format="JPEG", quality=95)
    except:
        logger.critical("Exception!", traceback.format_exc())

    if frame.index > 0 and frame.index % 25 == 0:
        logger.info("Rendered frame {} of {} ({:.2f}%)...".format(
            frame.index, total_frames, float(frame.index) * 100.0 / float(total_frames)
        ))
