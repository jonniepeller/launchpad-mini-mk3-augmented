from novation.channel_strip import ChannelStripComponent
from itertools import chain
from ableton.v2.base import liveobj_valid
import logging
import Live
from novation.colors import CLIP_COLOR_TABLE

logger = logging.getLogger(__name__)


class ChannelStripComponentAugmented(ChannelStripComponent):
    def _on_mute_changed(self):
        if self.is_enabled() and self._mute_button != None:
            if liveobj_valid(self._track) or self.empty_color == None:
                if (
                    self._track in chain(self.song.tracks, self.song.return_tracks)
                    and self._track.mute != self._invert_mute_feedback
                ):
                    track_color = CLIP_COLOR_TABLE[self._track.color]
                    try:
                        self._mute_button.set_light(track_color)
                    except:
                        self._mute_button.set_light("Mixer.MuteOff")
                else:
                    self._mute_button.set_light("Mixer.MuteOn")
            else:
                self._mute_button.set_light(self.empty_color)
