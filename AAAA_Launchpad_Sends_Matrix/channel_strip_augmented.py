from novation.channel_strip import ChannelStripComponent as ChannelStripComponentBase
import logging

logger = logging.getLogger(__name__)


class ChannelStripComponent(ChannelStripComponentBase):
    def __init__(self, *a, **k):
        logger.info("I am doing the thing!")
        super().__init__(*a, **k)
        self._colored_mute_buttons = None

        def make_button_slot(name):
            return self.register_slot(
                None, getattr(self, u"_%s_value" % name), u"value"
            )

        self._colored_mute_button_slot = make_button_slot(u"colored_mute")

    def disconnect(self):
        ChannelStripComponent._active_instances.remove(self)
        self.reset_button(self._colored_mute_button)
        self._colored_mute_button = None
        super().disconnect()

    # def _mute_value(self, value):
    #     if self.is_enabled():
    #         if liveobj_valid(self._track) and self._track != self.song.master_track:
    #             if not self._mute_button.is_momentary() or value != 0:
    #                 self._track.mute = not self._track.mute
    #     self._mute_button_slot = make_button_slot(u'colored_mute')

    # def _on_mute_changed(self):
    #     if self.is_enabled() and self._mute_button != None:
    #         if liveobj_valid(self._track) or self.empty_color == None:
    #             if (
    #                 self._track in chain(self.song.tracks, self.song.return_tracks)
    #                 and self._track.mute != self._invert_mute_feedback
    #             ):
    #                 self._mute_button.set_light(u"Mixer.MuteOff")
    #             else:
    #                 self._mute_button.set_light(u"Mixer.MuteOn")
    #         else:
    #             self._mute_button.set_light(self.empty_color)
